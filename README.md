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
docker-compose up --build
```

Services:

- Backend health check: http://localhost:8000/health
- Frontend dashboard: http://localhost:3000

## Project structure

```
backend/        FastAPI service
  app/
    main.py     Application entrypoint
frontend/       Next.js admin dashboard
  pages/
    index.js    Dashboard home
docker-compose.yml
```

## Progress

- [x] Step 1 — Monorepo + local infra (docker-compose)
- [ ] Step 2 — Backend skeleton (FastAPI + CORS + example endpoints)
- [ ] Step 3 — Postgres models + Alembic migrations
- [ ] Step 4 — Admin API (plans + API keys)
- [ ] Step 5 — Rate limiter middleware (fixed window via Redis)
- [ ] Step 6 — Next.js admin dashboard UI
