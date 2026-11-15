# Deployment Guide & Production Playbook — ProjectPilot

**Author:** DevOps Engineer  
**Version:** 1.0.0  

---

## 1. Architecture Topology

```
                  ┌──────────────────────┐
                  │    Browser Client    │
                  └──────────┬───────────┘
                             │ HTTPS
                             ▼
                  ┌──────────────────────┐
                  │   Vercel / Nginx     │ (React Single Page App)
                  │   Port 80 / 443      │
                  └──────────┬───────────┘
                             │ Reverse Proxy: /api/*
                             ▼
                  ┌──────────────────────┐
                  │    FastAPI Server    │ (Render / Railway / Docker)
                  │      Port 8000       │
                  └──────────┬───────────┘
                             │ Pooling
                             ▼
                  ┌──────────────────────┐
                  │  PostgreSQL Database │ (Render Postgres / RDS)
                  │      Port 5432       │
                  └──────────────────────┘
```

---

## 2. Option A: Local Docker Compose (Recommended for Verification)

Prerequisites: Docker Engine 24+ and Docker Compose v2+.

```bash
# 1. Clone repository
git clone https://github.com/prachizala/projectpilot.git
cd projectpilot

# 2. Build and launch all three containers (Postgres, FastAPI, React/Nginx)
docker-compose up --build -d

# 3. Verify health
curl http://localhost:8000/api/v1/health

# 4. Open in browser:
# Frontend SPA: http://localhost:3000
# Backend Swagger Docs: http://localhost:8000/docs
```

---

## 3. Option B: Cloud Production Deployment

### Frontend Deployment (Vercel)
1. Push repository to GitHub.
2. Log in to [Vercel](https://vercel.com) and click **Add New Project**.
3. Select `projectpilot` and configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. In `frontend/vite.config.ts`, update `/api` target to your live backend domain (e.g. `https://projectpilot-api.onrender.com`).
5. Click **Deploy**.

### Backend & Database Deployment (Render or Railway)
1. In [Render](https://render.com), create a **PostgreSQL Database** (`projectpilot-db`).
2. Copy the Internal Database URL (`postgresql://user:pass@host:5432/db`).
3. Create a **New Web Service**:
   - **Root Directory:** `backend`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `ENVIRONMENT`: `production`
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A secure 32+ character random secret
   - `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`
5. Save and deploy. Seed demo data by sending `POST /api/v1/seed`.
