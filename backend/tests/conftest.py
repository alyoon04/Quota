import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

ADMIN_TOKEN = "dev-admin-token"


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
