import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://app:app@localhost:5432/ratelimiter",
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "dev-admin-token")
