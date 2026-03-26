import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://app:app@localhost:5432/ratelimiter",
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "dev-admin-token")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "7"))
