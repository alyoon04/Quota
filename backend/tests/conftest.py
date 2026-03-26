import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.main import app
from app.rate_limiter import redis_client


@pytest.fixture(autouse=True, scope="session")
async def _warmup_redis():
    """Ping Redis once at session start so the connection pool binds to the session event loop."""
    await redis_client.ping()


@pytest.fixture(autouse=True, scope="session")
async def _clean_db():
    """Truncate all tables before the test session to avoid cross-run pollution."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("TRUNCATE api_keys, plans, users RESTART IDENTITY CASCADE")
        )
        await session.commit()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def user_token():
    """Register a test user once per session and return their JWT."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/auth/register",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        assert resp.status_code == 201
        return resp.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


# Backward-compat alias used by older test files
@pytest.fixture
def admin_headers(auth_headers):
    return auth_headers


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
