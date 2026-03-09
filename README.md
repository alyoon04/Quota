# Quota — Rate Limiter Platform

API rate limiting as a service. Fixed-window rate limiting backed by Redis, with Postgres for plan/key management and a Next.js admin dashboard.

## Architecture

| Component | Tech | Port |
|-----------|------|------|
| Backend | FastAPI (Python) | 8000 |
| Frontend | Next.js | 3000 |
| Database | PostgreSQL 16 | 5432 |
| Cache | Redis 7 | 6379 |

## Quick start

```bash
docker compose up --build
```

Services:

- Backend API + Swagger docs: http://localhost:8000/docs
- Admin dashboard: http://localhost:3000

## Local dev (without Docker)

**Prerequisites**: Python 3.12+, Node 20+, PostgreSQL 16, Redis 7

```bash
# 1. Start postgres and redis (e.g. via Homebrew)
brew services start postgresql@16
brew services start redis

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/ratelimiter
export REDIS_URL=redis://localhost:6379/0
export ADMIN_API_TOKEN=dev-admin-token
alembic upgrade head
uvicorn app.main:app --reload

# 3. Frontend (new terminal)
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
NEXT_PUBLIC_ADMIN_TOKEN=dev-admin-token \
npm run dev
```

## Usage

### 1. Create a plan

```bash
curl -X POST http://localhost:8000/admin/plans \
  -H "Authorization: Bearer dev-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "free", "default_rpm": 10}'
```

### 2. Create an API key

```bash
curl -X POST http://localhost:8000/admin/api-keys \
  -H "Authorization: Bearer dev-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"label": "my-key", "plan_id": "<plan-uuid>"}'
```

The response includes `plaintext_key` — save it, it's only shown once.

### 3. Make rate-limited requests

```bash
curl -H "X-API-Key: <plaintext_key>" http://localhost:8000/v1/hello
```

Responses include rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. Exceeding the plan's RPM returns `429` with a `Retry-After` header.

## API endpoints

### Public (rate-limited, requires `X-API-Key` header)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/hello` | Hello world |
| GET | `/v1/search` | Search placeholder |
| POST | `/v1/export` | Export placeholder |

### Admin (requires `Authorization: Bearer <token>`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/stats` | Total plans, keys, requests today |
| POST | `/admin/plans` | Create a plan |
| GET | `/admin/plans` | List plans (`?skip=0&limit=100`) |
| GET | `/admin/plans/{id}` | Get a single plan |
| PATCH | `/admin/plans/{id}` | Update plan name/RPM |
| DELETE | `/admin/plans/{id}` | Delete plan (blocked if keys exist) |
| POST | `/admin/api-keys` | Create an API key |
| GET | `/admin/api-keys` | List keys (`?skip=0&limit=100`) |
| PATCH | `/admin/api-keys/{id}` | Activate/deactivate a key |
| DELETE | `/admin/api-keys/{id}` | Delete a key |

### Infrastructure

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth) |
| GET | `/docs` | Swagger UI (interactive API explorer) |

## Project structure

```
backend/
  app/
    main.py             Application entrypoint + middleware wiring
    config.py           Environment variable configuration
    database.py         Async SQLAlchemy engine + session
    models.py           Plans + API keys tables
    schemas.py          Pydantic request/response models
    dependencies.py     DB session + admin auth dependencies
    logging_config.py   Structured JSON logging setup
    redis_client.py     Async Redis singleton
    rate_limiter.py     Fixed-window rate limit middleware (Lua script)
    routers/
      public.py         /v1/* placeholder endpoints
      admin.py          /admin/* CRUD + stats endpoints
  alembic/
    versions/           Database migrations
  entrypoint.sh         Runs migrations then starts uvicorn
frontend/
  components/
    Layout.js           Shared nav bar
  lib/
    api.js              Fetch wrapper with admin auth
  pages/
    index.js            Dashboard with stats cards
    plans.js            Plans management page
    api-keys.js         API keys management page
docker-compose.yml
.env.example
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+psycopg://app:app@localhost:5432/ratelimiter` | Postgres connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `ADMIN_API_TOKEN` | `dev-admin-token` | Bearer token for admin endpoints |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed CORS origins |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Backend URL (baked in at build time) |
| `NEXT_PUBLIC_ADMIN_TOKEN` | `dev-admin-token` | Admin token for frontend (baked in at build time) |

## Running tests

```bash
# Start docker services first
docker compose up -d postgres redis

# Stop local postgres if it conflicts on port 5432
brew services stop postgresql@14

cd backend
pip install -r requirements.txt
pytest
```

## Progress

- [x] Step 1 — Monorepo + local infra (docker-compose)
- [x] Step 2 — Backend skeleton (FastAPI + CORS + example endpoints)
- [x] Step 3 — Postgres models + Alembic migrations
- [x] Step 4 — Admin API (plans + API keys full CRUD)
- [x] Step 5 — Rate limiter middleware (fixed window via Redis)
- [x] Step 6 — Next.js admin dashboard UI
- [x] Step 7 — DB indexes + admin auth hardening
- [x] Step 8 — Structured JSON logging + observability stats
- [x] Step 9 — Docker health checks, restart policies, multi-stage builds
- [x] Step 10 — Pagination, Swagger docs, full README
