import asyncio
import uuid

import pytest

from app.database import AsyncSessionLocal
from app.models import ApiKey

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_create_api_key_returns_plaintext_key(client, admin_headers, plan):
    """Creating an API key should return the plaintext key exactly once."""
    resp = await client.post(
        "/admin/api-keys",
        json={"label": "my-key", "plan_id": plan["id"]},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    data = resp.json()

    assert "plaintext_key" in data
    assert len(data["plaintext_key"]) == 32  # secrets.token_hex(16)
    assert data["label"] == "my-key"
    assert data["plan_id"] == plan["id"]
    assert data["is_active"] is True
    assert data["last_used_at"] is None


async def test_list_api_keys_excludes_plaintext(client, admin_headers, api_key):
    """Listing API keys should return metadata but never the plaintext key."""
    resp = await client.get("/admin/api-keys", headers=admin_headers)
    assert resp.status_code == 200

    keys = resp.json()
    assert len(keys) >= 1

    matching = [k for k in keys if k["id"] == api_key["id"]]
    assert len(matching) == 1
    assert "plaintext_key" not in matching[0]
    assert matching[0]["label"] == api_key["label"]
    assert matching[0]["plan_id"] == api_key["plan_id"]
    assert matching[0]["is_active"] is True


async def test_create_key_invalid_plan_returns_404(client, admin_headers):
    """Creating a key with a non-existent plan_id should return 404."""
    fake_plan_id = str(uuid.uuid4())
    resp = await client.post(
        "/admin/api-keys",
        json={"label": "orphan-key", "plan_id": fake_plan_id},
        headers=admin_headers,
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Plan not found"


async def test_create_key_without_auth_returns_401(client):
    """Creating a key without an Authorization header should return 401/403."""
    fake_plan_id = str(uuid.uuid4())
    resp = await client.post(
        "/admin/api-keys",
        json={"label": "no-auth-key", "plan_id": fake_plan_id},
    )
    assert resp.status_code == 403


async def test_last_used_at_updates_after_request(client, admin_headers, api_key):
    """After a rate-limited request, last_used_at should be set on the key."""
    # Confirm last_used_at starts as None
    assert api_key["last_used_at"] is None

    # Make a request through the rate limiter
    resp = await client.get(
        "/v1/hello",
        headers={"X-API-Key": api_key["plaintext_key"]},
    )
    assert resp.status_code == 200

    # The update is fire-and-forget; give it time to flush
    await asyncio.sleep(0.5)

    # Check the DB directly
    async with AsyncSessionLocal() as session:
        key = await session.get(ApiKey, uuid.UUID(api_key["id"]))
        assert key is not None
        assert key.last_used_at is not None
