import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.main import app
from app.rate_limiter import redis_client

ADMIN_TOKEN = "dev-admin-token"


@pytest.fixture(autouse=True, scope="session")
async def _warmup_redis():
    """Ping Redis once at session start so the connection pool binds to the session event loop."""
    await redis_client.ping()


@pytest.fixture(autouse=True, scope="session")
async def _clean_db():
    """Truncate all tables before the test session to avoid cross-run pollution."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE api_keys, plans RESTART IDENTITY CASCADE"))
        await session.commit()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def admin_headers():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}


@pytest.fixture
async def plan(client, admin_headers):
    """Create a test plan (100 RPM) via admin API."""
    name = f"test-plan-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/admin/plans",
        json={"name": name, "default_rpm": 100},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def api_key(client, admin_headers, plan):
    """Create a test API key via admin API. Returns response with plaintext_key."""
    resp = await client.post(
        "/admin/api-keys",
        json={"label": "test-key", "plan_id": plan["id"]},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    return resp.json()
