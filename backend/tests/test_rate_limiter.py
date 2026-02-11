import hashlib
import uuid

import pytest
from sqlalchemy import update

from app.database import AsyncSessionLocal
from app.models import ApiKey
from app.rate_limiter import _plan_cache

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(autouse=True)
def _clean_plan_cache():
    """Clear in-memory plan cache between tests."""
    _plan_cache.clear()
    yield
    _plan_cache.clear()


@pytest.fixture
async def low_rpm_key(client, admin_headers):
    """Create a plan with 3 RPM and an API key. Returns the plaintext key."""
    name = f"rl-plan-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/admin/plans",
        json={"name": name, "default_rpm": 3},
        headers=admin_headers,
    )
    plan = resp.json()

    resp = await client.post(
        "/admin/api-keys",
        json={"label": "rl-key", "plan_id": plan["id"]},
        headers=admin_headers,
    )
    return resp.json()["plaintext_key"]


async def test_valid_key_returns_rate_limit_headers(client, low_rpm_key):
    resp = await client.get("/v1/hello", headers={"X-API-Key": low_rpm_key})

    assert resp.status_code == 200
    assert resp.headers["X-RateLimit-Limit"] == "3"
    assert resp.headers["X-RateLimit-Remaining"] == "2"
    assert "X-RateLimit-Reset" in resp.headers


async def test_remaining_decrements(client, low_rpm_key):
    headers = {"X-API-Key": low_rpm_key}

    resp = await client.get("/v1/hello", headers=headers)
    assert resp.headers["X-RateLimit-Remaining"] == "2"

    resp = await client.get("/v1/hello", headers=headers)
    assert resp.headers["X-RateLimit-Remaining"] == "1"

    resp = await client.get("/v1/hello", headers=headers)
    assert resp.headers["X-RateLimit-Remaining"] == "0"


async def test_exceeding_rpm_returns_429(client, low_rpm_key):
    headers = {"X-API-Key": low_rpm_key}

    # Use all 3 allowed requests
    for _ in range(3):
        resp = await client.get("/v1/hello", headers=headers)
        assert resp.status_code == 200

    # 4th request should be rejected
    resp = await client.get("/v1/hello", headers=headers)
    assert resp.status_code == 429
    assert resp.headers["X-RateLimit-Remaining"] == "0"
    assert "Retry-After" in resp.headers
    assert int(resp.headers["Retry-After"]) > 0
    assert resp.json()["detail"] == "Rate limit exceeded"


async def test_missing_api_key_returns_401(client):
    resp = await client.get("/v1/hello")

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Missing X-API-Key header"


async def test_invalid_api_key_returns_401(client):
    resp = await client.get("/v1/hello", headers={"X-API-Key": "not-a-real-key"})

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or inactive API key"


async def test_inactive_key_rejected(client, low_rpm_key):
    # Deactivate the key directly in the database
    key_hash = hashlib.sha256(low_rpm_key.encode()).hexdigest()
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(ApiKey).where(ApiKey.key_hash == key_hash).values(is_active=False)
        )
        await session.commit()

    resp = await client.get("/v1/hello", headers={"X-API-Key": low_rpm_key})

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or inactive API key"
