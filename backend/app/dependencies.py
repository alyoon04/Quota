from collections.abc import AsyncGenerator

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ADMIN_API_TOKEN
from app.database import AsyncSessionLocal

bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> None:
    if credentials.credentials != ADMIN_API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")
