# Quota — Daily Implementation Plan

15 days, one focused chunk per day. Each day builds on the last.

- **Days 1–10**: Foundation — tests, full CRUD, hardening, docs. Result: a solid tool for personal/internal use.
- **Days 11–15**: Production SaaS — multi-tenant auth, TLS, scaling, billing, onboarding. Result: ready for external users.

---

## Day 1: Rate Limiter Tests
**Goal**: Test the most critical piece of the app — the rate limiting middleware.

- [ ] Add test fixtures that create a plan + API key in the test DB
- [ ] Test that a valid API key returns 200 with correct `X-RateLimit-*` headers
- [ ] Test that exceeding RPM returns 429 with `Retry-After` header
- [ ] Test that a missing/invalid `X-API-Key` header returns 401
- [ ] Test that an inactive key is rejected

**Files**: `backend/tests/test_rate_limiter.py`, `backend/tests/conftest.py`

---

## Day 2: API Key Endpoint Tests
**Goal**: Full test coverage for API key creation and listing.

- [ ] Test creating an API key returns plaintext key (shown once)
- [ ] Test listing API keys returns metadata (no plaintext)
- [ ] Test creating a key with an invalid plan_id returns 404
- [ ] Test creating a key without auth returns 401
- [ ] Test `last_used_at` updates after a rate-limited request

**Files**: `backend/tests/test_api_keys.py`

---

## Day 3: Complete Plan CRUD (Backend)
**Goal**: Add update and delete endpoints for plans.

- [ ] `PATCH /admin/plans/{plan_id}` — update name and/or default_rpm
- [ ] `DELETE /admin/plans/{plan_id}` — delete a plan (reject if keys still reference it)
- [ ] `GET /admin/plans/{plan_id}` — get a single plan
- [ ] Add tests for each new endpoint
- [ ] Update schemas.py with PlanUpdate model

**Files**: `backend/app/routers/admin.py`, `backend/app/schemas.py`, `backend/tests/test_plans.py`

---

## Day 4: API Key Lifecycle (Backend)
**Goal**: Add deactivate/activate and delete for API keys.

- [ ] `PATCH /admin/api-keys/{key_id}` — toggle `is_active`
- [ ] `DELETE /admin/api-keys/{key_id}` — delete a key
- [ ] Add tests for deactivate, reactivate, and delete
- [ ] Verify deactivated keys get rejected by rate limiter

**Files**: `backend/app/routers/admin.py`, `backend/app/schemas.py`, `backend/tests/test_api_keys.py`

---

## Day 5: Database Indexes + Admin Auth Hardening
**Goal**: Performance and security quick wins.

- [ ] Add Alembic migration with indexes on `api_keys.key_hash` and `api_keys.plan_id`
- [ ] Move hardcoded `dev-admin-token` out of frontend — read from env var at build time
- [ ] Add rate limiting on `/admin/*` endpoints (e.g. 60 RPM per IP)
- [ ] Add tests for admin auth failures (missing token, wrong token)

**Files**: `alembic/versions/0002_*.py`, `frontend/lib/api.js`, `backend/app/dependencies.py`

---

## Day 6: Plans Page — Full CRUD in Dashboard
**Goal**: Make the plans page fully functional (edit + delete).

- [ ] Add edit button that opens inline form to update name/RPM
- [ ] Add delete button with confirmation dialog
- [ ] Show key count per plan (to warn before delete)
- [ ] Add loading states and error messages
- [ ] Wire up to new PATCH/DELETE backend endpoints

**Files**: `frontend/pages/plans.js`

---

## Day 7: API Keys Page — Lifecycle in Dashboard
**Goal**: Make the API keys page fully functional.

- [ ] Add activate/deactivate toggle per key
- [ ] Add delete button with confirmation
- [ ] Add filtering by plan
- [ ] Add loading states and error messages
- [ ] Show `last_used_at` timestamp

**Files**: `frontend/pages/api-keys.js`

---

## Day 8: Logging + Basic Observability
**Goal**: Know what's happening in your app.

- [ ] Add Python `logging` throughout backend (structured JSON logs)
- [ ] Log every rate limit rejection (key, plan, endpoint)
- [ ] Log admin actions (create/update/delete plan/key)
- [ ] Add `GET /admin/stats` endpoint — total keys, total plans, requests today
- [ ] Add a simple stats card to the dashboard home page

**Files**: `backend/app/main.py`, `backend/app/rate_limiter.py`, `backend/app/routers/admin.py`, `frontend/pages/index.js`

---

## Day 9: Docker + Deployment Hardening
**Goal**: Make it ready to run outside localhost.

- [ ] Add health checks to docker-compose for postgres, redis, backend
- [ ] Add restart policies (`unless-stopped`)
- [ ] Multi-stage Dockerfile builds (smaller images)
- [ ] Make CORS origins configurable via env var
- [ ] Add `.env.example` file documenting all env vars

**Files**: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `backend/app/main.py`, `.env.example`

---

## Day 10: Documentation + Final Polish
**Goal**: Make it presentable and easy for someone else to use.

- [ ] Update README with new endpoints and features
- [ ] Add setup guide (local dev without Docker)
- [ ] Enable FastAPI's built-in `/docs` (Swagger UI) for API exploration
- [ ] Add pagination to list endpoints (plans + keys)
- [ ] Final pass: remove TODOs, clean up dead code

**Files**: `README.md`, `backend/app/main.py`, `backend/app/routers/admin.py`

---

# Phase 2: Production SaaS (Days 11–15)

Everything below takes Quota from "works for me" to "works for strangers."

---

## Day 11: Multi-Tenant Auth — User Accounts
**Goal**: Replace the single admin token with real user accounts.

- [ ] Add `User` model (id, email, password_hash, created_at)
- [ ] Add Alembic migration for users table
- [ ] Add `POST /auth/register` and `POST /auth/login` endpoints (return JWT)
- [ ] Add JWT verification dependency to replace the static token check
- [ ] Tie Plans and ApiKeys to a `user_id` foreign key
- [ ] Add migration to add `user_id` column to plans and api_keys tables
- [ ] Add tests for register, login, and JWT-protected routes

**Files**: `backend/app/models.py`, `backend/app/routers/auth.py`, `backend/app/dependencies.py`, `backend/app/schemas.py`, `backend/tests/test_auth.py`

---

## Day 12: Frontend Auth — Login + Scoped Dashboard
**Goal**: Dashboard only shows your own plans and keys.

- [ ] Add login page (`/login`) and register page (`/register`)
- [ ] Store JWT in httpOnly cookie or localStorage
- [ ] Update `lib/api.js` to attach JWT instead of hardcoded token
- [ ] Add auth guard — redirect unauthenticated users to `/login`
- [ ] Filter plans and keys by logged-in user
- [ ] Add logout button to Layout

**Files**: `frontend/pages/login.js`, `frontend/pages/register.js`, `frontend/lib/api.js`, `frontend/components/Layout.js`

---

## Day 13: TLS, HTTPS + Reverse Proxy
**Goal**: Encrypted traffic in production.

- [ ] Add nginx (or Caddy) as a reverse proxy service in docker-compose
- [ ] Configure TLS termination (Let's Encrypt with Caddy, or self-signed for dev)
- [ ] Route `/api/*` to backend, `/*` to frontend
- [ ] Set `Secure`, `HttpOnly`, `SameSite` flags on auth cookies
- [ ] Update CORS to accept the production domain
- [ ] Add `ALLOWED_ORIGINS` env var for dynamic CORS config
- [ ] Document deployment with a real domain

**Files**: `docker-compose.prod.yml`, `Caddyfile` (or `nginx.conf`), `backend/app/main.py`, `.env.example`

---

## Day 14: Horizontal Scaling + Shared State
**Goal**: Support multiple backend instances behind a load balancer.

- [ ] Move plan cache from in-memory dict to Redis (shared across instances)
- [ ] Add TTL-based cache invalidation in Redis
- [ ] Invalidate cache on plan update/delete (cache-busting)
- [ ] Add connection pooling config for PostgreSQL (`pool_size`, `max_overflow`)
- [ ] Test with 2+ backend instances via docker-compose `replicas`
- [ ] Add basic load test script (e.g. using `wrk` or `locust`)

**Files**: `backend/app/rate_limiter.py`, `backend/app/database.py`, `docker-compose.prod.yml`, `scripts/loadtest.py`

---

## Day 15: Usage Metering, Billing Hooks + Landing Page
**Goal**: Track usage per user and prepare for monetization.

- [ ] Add `usage_log` table (key_id, endpoint, timestamp, was_rejected)
- [ ] Record every rate-limited request into usage_log (async, non-blocking)
- [ ] Add `GET /admin/usage` endpoint — daily/hourly breakdown per key
- [ ] Add usage chart to dashboard (simple bar chart or table)
- [ ] Add Stripe webhook stub or billing flag on plans (free/paid)
- [ ] Add a simple landing page at `/` explaining what Quota does
- [ ] Final README update with full architecture and deployment guide

**Files**: `backend/app/models.py`, `backend/app/routers/admin.py`, `backend/tests/test_usage.py`, `frontend/pages/index.js`, `frontend/pages/usage.js`, `README.md`

---

## How to Use This Plan

When starting a session, tell Claude: **"Let's work on Day N"** and it will pick up from here.
