import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_missing_auth_header_returns_403(client):
    """Requests without an Authorization header should be rejected with 403."""
    resp = await client.get("/admin/plans")
    assert resp.status_code == 403


async def test_wrong_token_returns_403(client):
    """Requests with an incorrect token should be rejected with 403."""
    resp = await client.get(
        "/admin/plans",
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Invalid admin token"


async def test_correct_token_is_accepted(client, admin_headers):
    """Requests with the correct token should pass through (200)."""
    resp = await client.get("/admin/plans", headers=admin_headers)
    assert resp.status_code == 200


async def test_malformed_auth_scheme_returns_403(client):
    """Non-Bearer schemes (e.g. Basic) should be rejected with 403."""
    resp = await client.get(
        "/admin/plans",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert resp.status_code == 403
