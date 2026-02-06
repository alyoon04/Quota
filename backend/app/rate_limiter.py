import asyncio
import hashlib
import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.database import AsyncSessionLocal
from app.models import ApiKey, Plan
from app.redis_client import redis_client

# In-memory plan cache: {plan_id: (rpm, cached_at)}
_plan_cache: dict[str, tuple[int, float]] = {}
PLAN_CACHE_TTL = 60  # seconds

# Lua script for atomic increment + expire
RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
return count
"""


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/v1"):
            return await call_next(request)

        api_key_header = request.headers.get("X-API-Key")
        if not api_key_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing X-API-Key header"},
            )

        key_hash = hashlib.sha256(api_key_header.encode()).hexdigest()

        async with AsyncSessionLocal() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(ApiKey).where(
                    ApiKey.key_hash == key_hash, ApiKey.is_active.is_(True)
                )
            )
            api_key = result.scalar_one_or_none()

            if not api_key:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or inactive API key"},
                )

            plan_id_str = str(api_key.plan_id)
            api_key_id_str = str(api_key.id)

            # Get plan RPM with caching
            rpm = await self._get_plan_rpm(session, api_key.plan_id, plan_id_str)

            # Fire-and-forget last_used_at update
            asyncio.create_task(
                self._update_last_used(api_key_id_str)
            )

        # Fixed window rate limiting
        now = time.time()
        window = int(now) // 60
        redis_key = f"rl:{api_key_id_str}:{window}"
        window_reset = (window + 1) * 60

        count = await redis_client.eval(RATE_LIMIT_SCRIPT, 1, redis_key, 60)

        remaining = max(0, rpm - count)
        headers = {
            "X-RateLimit-Limit": str(rpm),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(window_reset),
        }

        if count > rpm:
            retry_after = window_reset - int(now)
            headers["Retry-After"] = str(max(1, retry_after))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers=headers,
            )

        response = await call_next(request)
        for k, v in headers.items():
            response.headers[k] = v
        return response

    async def _get_plan_rpm(self, session, plan_id, plan_id_str: str) -> int:
        now = time.time()
        cached = _plan_cache.get(plan_id_str)
        if cached and now - cached[1] < PLAN_CACHE_TTL:
            return cached[0]

        plan = await session.get(Plan, plan_id)
        if not plan:
            return 0
        _plan_cache[plan_id_str] = (plan.default_rpm, now)
        return plan.default_rpm

    async def _update_last_used(self, api_key_id_str: str):
        try:
            import uuid

            async with AsyncSessionLocal() as session:
                api_key = await session.get(ApiKey, uuid.UUID(api_key_id_str))
                if api_key:
                    api_key.last_used_at = datetime.now(timezone.utc)
                    await session.commit()
        except Exception:
            pass  # fire-and-forget
