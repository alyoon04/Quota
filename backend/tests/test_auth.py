import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_register_returns_token(client):
    resp = await client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_returns_token(client):
    await client.post(
        "/auth/register",
        json={"email": "loginuser@example.com", "password": "mypassword"},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": "loginuser@example.com", "password": "mypassword"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password_returns_401(client):
    await client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "correct"},
    )
    resp = await client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "incorrect"},
    )
    assert resp.status_code == 401


async def test_duplicate_register_returns_409(client):
    await client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "pass123"},
    )
    resp = await client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "pass123"},
    )
    assert resp.status_code == 409


async def test_login_unknown_email_returns_401(client):
    resp = await client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "anything"},
    )
    assert resp.status_code == 401


async def test_jwt_scopes_plans_to_owner(client):
    """Two users should not see each other's plans."""
    # Register user A
    resp_a = await client.post(
        "/auth/register",
        json={"email": "usera@example.com", "password": "pass"},
    )
    token_a = resp_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register user B
    resp_b = await client.post(
        "/auth/register",
        json={"email": "userb@example.com", "password": "pass"},
    )
    token_b = resp_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a plan
    await client.post(
        "/admin/plans",
        json={"name": "plan-for-a", "default_rpm": 10},
        headers=headers_a,
    )

    # User B should not see user A's plan
    resp = await client.get("/admin/plans", headers=headers_b)
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "plan-for-a" not in names
