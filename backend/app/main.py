import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.logging_config import setup_logging
from app.rate_limiter import RateLimitMiddleware
from app.redis_client import redis_client
from app.routers import admin, public

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.aclose()


_cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]

app = FastAPI(title="Quota – Rate Limiter Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

app.include_router(public.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"ok": True}
