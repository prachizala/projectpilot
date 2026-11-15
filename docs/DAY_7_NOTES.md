# Day 7 Notes — Docker Containerization, CI/CD Pipeline, Seed Data & Final Release

**Date:** Day 7  
**Author:** Engineering Team  

---

## 1. What Was Built Today

1. **Multi-Stage Docker Architecture:**
   - **Backend Container (`backend/Dockerfile`):** Python 3.11 slim image, layer-cached dependency installation (`pip install --no-cache-dir`), non-root execution considerations, and health check validation.
   - **Frontend Container (`frontend/Dockerfile` & `frontend/nginx.conf`):** Multi-stage build (`node:20-alpine` build stage compiling Vite bundle, followed by `nginx:alpine` runtime serving static assets in ~25MB). Configured with single-page application fallback routing (`try_files $uri $uri/ /index.html`) and backend API reverse-proxying.
2. **Production-Ready Docker Compose (`docker-compose.yml`):**
   - Orchestrates 3 services: `db` (PostgreSQL 16 alpine with health checks and persistent volume storage), `backend` (FastAPI with wait-for-database initialization), and `frontend` (Nginx reverse proxy on port 80).
   - Environment variable parametrization via `.env`.
3. **Automated GitHub Actions CI Workflow (`.github/workflows/ci.yml`):**
   - Triggers on every push and pull request targeting `main`.
   - Parallel jobs:
     - **Backend Test Job:** Sets up Python 3.11, caches pip dependencies, installs backend requirements, runs Ruff linter, and executes pytest across all 15 automated test suites.
     - **Frontend Build Job:** Sets up Node.js 20, caches npm packages, runs `npm run lint`, and verifies type-safe production build via `npm run build`.
4. **Automated Demo Seed Engine (`backend/app/core/seed.py` & `POST /api/v1/seed`):**
   - Idempotently populates realistic test data:
     - 1 Demo Business Owner (`demo@projectpilot.io`)
     - 1 Client Portal User (`sarah@apexdesign.com`)
     - 3 Client Accounts (Apex Design Studio, Nexus Tech Solutions, CloudScale Analytics)
     - 4 Projects across active, planning, and completed states
     - 9 Tasks distributed across Kanban columns (`todo`, `in_progress`, `review`, `done`) with integer position indexes
     - 3 Invoices with line items and calculated totals
     - 2 Proposals (1 draft, 1 converted)
5. **Quality, Security, and Final Documentation:**
   - Authored `DEPLOYMENT.md`, `TEST_REPORT.md`, `SECURITY_REPORT.md`, `KNOWN_ISSUES.md`, and `DEMO_SCRIPT.md`.
   - Comprehensive `README.md` with architecture diagram, quickstart guide, API catalog, and demo credentials.

---

## 2. How the Core Day 7 Flow Works (Container Architecture & CI/CD)

```
[ Developer Git Push ] ──► GitHub Actions CI
                              ├── Job 1: Backend CI (Python 3.11)
                              │     ├── pip install -r requirements.txt
                              │     ├── ruff check .
                              │     └── pytest (15/15 passing)
                              └── Job 2: Frontend CI (Node 20)
                                    ├── npm ci
                                    └── npm run build (tsc + vite)

[ Local / Production Deployment ] ──► docker compose up --build
      │
      ├── Service: db (Postgres 16)
      │     └── Healthcheck: pg_isready -U postgres
      │
      ├── Service: backend (FastAPI :8000)
      │     └── Depends on: db (condition: service_healthy)
      │     └── Seeds schema & starts Uvicorn ASGI server
      │
      └── Service: frontend (Nginx :80)
            ├── Serves compiled React SPA assets
            └── Proxies /api/v1/* requests to backend:8000
```

---

## 3. Five Technical Interview Questions & Answers (Day 7 DevOps & Architecture)

### Q1: Why did you use a multi-stage Docker build for the React frontend, and what are the benefits?
> **Answer:**  
> "A standard Node.js development image with full `node_modules` and compilation tools is easily 800MB–1GB. In `frontend/Dockerfile`, we use a two-stage build:
> 1. Stage 1 (`build`): Uses `node:20-alpine` to install dependencies and run `npm run build`, producing an optimized production bundle in `/app/dist`.
> 2. Stage 2 (`runtime`): Copies only the compiled static assets into a fresh `nginx:alpine` image.
>
> The resulting runtime image is only ~25MB, has zero Node runtime vulnerabilities, uses negligible memory, and serves static files at maximum Nginx speeds."

### Q2: How do you prevent the FastAPI backend container from crashing if PostgreSQL isn't ready on startup?
> **Answer:**  
> "In `docker-compose.yml`, we define a health check on the `db` service:
> ```yaml
> healthcheck:
>   test: ["CMD-SHELL", "pg_isready -U postgres -d projectpilot"]
>   interval: 5s
>   timeout: 5s
>   retries: 5
> ```
> We configure the backend with `depends_on: db: condition: service_healthy`. This instructs Docker Compose to wait until PostgreSQL is accepting connections before launching Uvicorn, avoiding race conditions and startup crashes."

### Q3: How does Nginx handle client-side routing in our Single-Page Application (SPA)?
> **Answer:**  
> "In client-side routers like React Router, navigation paths such as `/projects` or `/invoices` do not correspond to physical files on the web server. If a user refreshes `/invoices`, a naive web server returns a 404 Not Found. In `frontend/nginx.conf`, we configure:
> ```nginx
> location / {
>     try_files $uri $uri/ /index.html;
> }
> ```
> This tells Nginx to look for an exact matching static file first; if not found, it falls back to serving `index.html`, allowing React Router to parse the URL and render the appropriate page."

### Q4: How is the database seed function designed to be idempotent and safe for repeated calls?
> **Answer:**  
> "In `backend/app/core/seed.py`, `seed_demo_data(db)` queries existing records by unique identifiers (e.g., `user.email == 'demo@projectpilot.io'` and `client.email == 'contact@apexdesign.com'`) before creating new entities. If records already exist, the seeder updates or preserves them rather than inserting duplicate records that violate unique constraints. This allows developers and reviewers to trigger `POST /api/v1/seed` at any time to verify application features safely."

### Q5: How does the GitHub Actions CI pipeline ensure that broken code cannot be merged into main?
> **Answer:**  
> "Our `.github/workflows/ci.yml` runs on every push and PR targeting `main`. It runs backend unit tests (`pytest`) and frontend compilation checks (`npm run build`) in parallel isolated virtual runners. If any test fails or if a TypeScript type error occurs during bundling, the pipeline exits with a non-zero exit code, which fails the GitHub check and prevents merging."

---

## 4. One Small Change You Should Try Yourself

**Exercise: Add a custom database health check query.**  
Open `backend/app/api/v1/endpoints/health.py`. Currently, `health_check()` returns static metadata:
```python
return {
    "status": "healthy",
    "version": settings.VERSION,
    "environment": settings.ENVIRONMENT
}
```
Try making it check live database connectivity by injecting `db: Session = Depends(get_db)` and executing a simple probe:
```python
from sqlalchemy import text

@router.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"
        
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
```
Run `python -m pytest tests/` to confirm that all tests continue to pass!
