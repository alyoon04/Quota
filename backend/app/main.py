from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.rate_limiter import RateLimitMiddleware
from app.redis_client import redis_client
from app.routers import admin, public


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.aclose()


app = FastAPI(title="Quota – Rate Limiter Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
