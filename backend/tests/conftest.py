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
