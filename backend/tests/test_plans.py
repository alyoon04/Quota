import uuid


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
