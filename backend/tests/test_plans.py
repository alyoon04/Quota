import uuid

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_plan_crud(client, admin_headers):
    plan_name = f"test-plan-{uuid.uuid4().hex[:8]}"

    # Create a plan
    resp = await client.post(
        "/admin/plans",
        json={"name": plan_name, "default_rpm": 100},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    plan = resp.json()
    assert plan["name"] == plan_name
    assert plan["default_rpm"] == 100
    assert "id" in plan

    # List plans and verify it appears
    resp = await client.get("/admin/plans", headers=admin_headers)
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert plan_name in names

    # Duplicate name returns 409
    resp = await client.post(
        "/admin/plans",
        json={"name": plan_name, "default_rpm": 50},
        headers=admin_headers,
    )
    assert resp.status_code == 409


async def test_get_single_plan(client, admin_headers, plan):
    resp = await client.get(
        f"/admin/plans/{plan['id']}", headers=admin_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == plan["id"]
    assert data["name"] == plan["name"]
    assert data["default_rpm"] == plan["default_rpm"]


async def test_get_plan_not_found(client, admin_headers):
    fake_id = uuid.uuid4()
    resp = await client.get(
        f"/admin/plans/{fake_id}", headers=admin_headers
    )
    assert resp.status_code == 404


async def test_update_plan_name(client, admin_headers, plan):
    new_name = f"updated-{uuid.uuid4().hex[:8]}"
    resp = await client.patch(
        f"/admin/plans/{plan['id']}",
        json={"name": new_name},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == new_name
    assert data["default_rpm"] == plan["default_rpm"]  # unchanged


async def test_update_plan_rpm(client, admin_headers, plan):
    resp = await client.patch(
        f"/admin/plans/{plan['id']}",
        json={"default_rpm": 500},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["default_rpm"] == 500
    assert resp.json()["name"] == plan["name"]  # unchanged


async def test_update_plan_duplicate_name(client, admin_headers):
    # Create two plans
    name_a = f"plan-a-{uuid.uuid4().hex[:8]}"
    name_b = f"plan-b-{uuid.uuid4().hex[:8]}"
    resp_a = await client.post(
        "/admin/plans",
        json={"name": name_a, "default_rpm": 10},
        headers=admin_headers,
    )
    assert resp_a.status_code == 201
    await client.post(
        "/admin/plans",
        json={"name": name_b, "default_rpm": 20},
        headers=admin_headers,
    )
    # Try to rename plan_a to plan_b's name
    resp = await client.patch(
        f"/admin/plans/{resp_a.json()['id']}",
        json={"name": name_b},
        headers=admin_headers,
    )
    assert resp.status_code == 409


async def test_update_plan_not_found(client, admin_headers):
    fake_id = uuid.uuid4()
    resp = await client.patch(
        f"/admin/plans/{fake_id}",
        json={"name": "nope"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


async def test_delete_plan(client, admin_headers):
    # Create a plan with no keys
    name = f"delete-me-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/admin/plans",
        json={"name": name, "default_rpm": 10},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    plan_id = resp.json()["id"]

    # Delete it
    resp = await client.delete(
        f"/admin/plans/{plan_id}", headers=admin_headers
    )
    assert resp.status_code == 204

    # Confirm it's gone
    resp = await client.get(
        f"/admin/plans/{plan_id}", headers=admin_headers
    )
    assert resp.status_code == 404


async def test_delete_plan_with_keys_rejected(client, admin_headers, api_key):
    """Deleting a plan that has API keys should return 409."""
    plan_id = api_key["plan_id"]
    resp = await client.delete(
        f"/admin/plans/{plan_id}", headers=admin_headers
    )
    assert resp.status_code == 409
    assert "existing API keys" in resp.json()["detail"]


async def test_delete_plan_not_found(client, admin_headers):
    fake_id = uuid.uuid4()
    resp = await client.delete(
        f"/admin/plans/{fake_id}", headers=admin_headers
    )
    assert resp.status_code == 404
