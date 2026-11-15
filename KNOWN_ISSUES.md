# ProjectPilot — Known Issues & Technical Limitations

This document tracks known architectural limitations, environmental edge cases, and deferred backlog items for the **ProjectPilot v0.9.0** release. Being honest and transparent about technical boundaries is essential for software engineering and production readiness.

---

## 1. Current Limitations (v0.9.0)

### 1.1 Local SQLite Database Concurrency
- **Symptom:** In high-concurrency local development environments with multiple simultaneous write transactions, SQLite may occasionally raise `sqlite3.OperationalError: database is locked`.
- **Root Cause:** SQLite operates with file-level database locking during write operations, unlike client-server databases that implement row-level locking (MVCC).
- **Workaround / Production Fix:** In Docker and production environments, ProjectPilot connects to PostgreSQL via `DATABASE_URL=postgresql://user:pass@host:5432/projectpilot`, which handles concurrent transactions smoothly. For local SQLite development, WAL mode (`PRAGMA journal_mode=WAL;`) mitigates contention.

### 1.2 AI Proposal Generator Fallback Mode
- **Symptom:** When running without an active LLM API key (`OPENAI_API_KEY` or `GEMINI_API_KEY` unset), the proposal generator utilizes a deterministic heuristic parser.
- **Root Cause:** Intentional architectural design to ensure offline reproducibility, zero-cost continuous integration testing, and uninterrupted development.
- **Behavior:** The deterministic parser extracts scope statements, budget figures, and milestone tasks from standard markdown headings and bulleted requirement patterns. Providing a valid API key in `.env` automatically activates the generative LLM service.

### 1.3 Client Portal Read-Only Scope
- **Symptom:** Authenticated clients cannot modify project deadlines, add tasks, or mark invoices as paid.
- **Design Intent:** By design in v0.9.0, clients have read-only visibility into projects and invoices assigned to their specific company profile (`User.role == "client"`). Task creation and invoice status transitions are reserved for business owners (`User.role == "owner"`). Future releases will support client comment threads and payment gateway integration.

### 1.4 Single Currency Support
- **Symptom:** All budget and invoice calculations currently default to USD (`$`).
- **Workaround:** Currency symbols are formatted on the frontend. Multi-currency support (EUR, GBP, INR) with real-time conversion rates is prioritized on the post-v1.0 roadmap.

---

## 2. Minor UI / UX Polishing Deferred to v1.0

1. **Kanban Multi-Touch Mobile Drag-and-Drop:** On small mobile screens (<640px), dragging cards across columns can occasionally trigger page scroll. A drop-down column selector modal for mobile devices is planned for v1.0.
2. **Avatar Image Uploads:** User and client avatars currently render dynamic SVG initials based on the company or contact name rather than binary file uploads to S3/GCS.
3. **Invoice Email Dispatch:** Invoices can be downloaded as crisp vector PDFs, but direct SMTP email delivery (`Send Invoice via Email`) requires an external SendGrid or AWS SES configuration, which is currently deferred.

---

## 3. Security & Operational Notes

- **Secret Keys in `.env.example`:** The default `SECRET_KEY` in `.env.example` is a placeholder. Users must generate a cryptographically strong 64-character hex string (`openssl rand -hex 32`) before deploying to staging or production.
- **Database Seed Endpoint:** The `/api/v1/seed` endpoint is exposed for demonstration environments. In strict production deployments, this endpoint should be disabled via `ENVIRONMENT=production` in `app/core/config.py`.
