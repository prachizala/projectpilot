# ProjectPilot — Sprint Task Board

**Sprint Duration:** 7 Days (Days 1–7)  
**Status Key:** `Backlog` | `In Progress` | `In Review` | `Done`  

---

## Task Board Table

| Task ID | Day | Area | Description | Owner Agent | Acceptance Criteria | Branch / PR | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T-001** | Day 1 | Setup & Specs | Repository initialization, .gitignore, PRD, ARCHITECTURE, DESIGN, TASKS | Orchestrator & PM | Project scaffolded, specifications complete and frozen | `feat/T-001-day1-foundation-and-auth` | **Done** |
| **T-002** | Day 1 | Backend | SQLAlchemy models: User, Client, Project, Task, Invoice, Proposal | Backend Engineer | Full relational model defined with foreign keys and indexes | `feat/T-001-day1-foundation-and-auth` | **Done** |
| **T-003** | Day 1 | Backend | JWT authentication engine (signup, login, refresh, me) with bcrypt | Backend Engineer | Token generation, password hashing, and role checks working | `feat/T-001-day1-foundation-and-auth` | **Done** |
| **T-004** | Day 1 | QA & Review | Automated test suite for Auth and database models; Day 1 tag v0.1.0 | QA & Reviewer | 100% pytest pass on auth endpoints, zero tool/bot mentions | `feat/T-001-day1-foundation-and-auth` | **Done** |
| **T-005** | Day 2 | Backend | Clients CRUD API with owner tenancy isolation and search | Backend Engineer | Validated endpoints for GET, POST, PUT, DELETE /clients | `feat/T-005-clients-and-projects-api` | **Done** |
| **T-006** | Day 2 | Backend | Projects CRUD API with status transitions and budget validation | Backend Engineer | Endpoints for GET, POST, PUT, DELETE /projects | `feat/T-005-clients-and-projects-api` | **Done** |
| **T-007** | Day 2 | QA | Pytest suite for Clients and Projects CRUD with tenant isolation | QA Engineer | Automated tests verifying multi-tenant access restrictions | `feat/T-005-clients-and-projects-api` | **Done** |
| **T-008** | Day 3 | Frontend | Vite + React + TypeScript setup, Tailwind CSS, React Router | Frontend Engineer | Single page application skeleton with routing | `feat/T-008-frontend-core-and-management` | **Done** |
| **T-009** | Day 3 | Frontend | Auth provider, login/signup forms, protected route wrappers | Frontend Engineer | Seamless JWT session management in frontend | `feat/T-008-frontend-core-and-management` | **Done** |
| **T-010** | Day 3 | Frontend | Clients and Projects management UI with modals and status badges | Frontend Engineer | Interactive tables, forms, and client detail views | `feat/T-008-frontend-core-and-management` | **Done** |
| **T-011** | Day 4 | Backend | Tasks CRUD and column reordering endpoint with integer indexing | Backend Engineer | PATCH /tasks/{id}/position persisting column and rank | `feat/T-011-tasks-api` | Backlog |
| **T-012** | Day 4 | Frontend | Interactive drag-and-drop Kanban board with optimistic update | Frontend Engineer | 4 columns (todo, in_progress, review, done) with DnD | `feat/T-012-kanban-board` | Backlog |
| **T-013** | Day 5 | Backend | Invoicing API: line items calculation and PyMuPDF vector PDF stream | Backend Engineer | Automated tax calculation and print-ready PDF export | `feat/T-013-invoices-api` | Backlog |
| **T-014** | Day 5 | Frontend | Executive Dashboard with Recharts revenue graphs and KPI widgets | Frontend Engineer | Interactive charts and overdue task alerts | `feat/T-014-dashboard-ui` | Backlog |
| **T-015** | Day 6 | AI & Backend| Proposal generator service (specs -> milestones/tasks) & converter | AI Engineer | Structured proposal extraction and project conversion | `feat/T-015-proposals-engine` | Backlog |
| **T-016** | Day 6 | Frontend | Client Portal view restricting clients to their own projects | Frontend Engineer | Client role isolation in frontend router and views | `feat/T-016-client-portal` | Backlog |
| **T-017** | Day 7 | DevOps | Dockerfile, docker-compose (app + PostgreSQL), CI workflows | DevOps Engineer | Containerized local and production configurations | `feat/T-017-devops-deployment` | Backlog |
| **T-018** | Day 7 | Documentation| README with real screenshots, demo script, v0.9.0 release tag | Technical Writer | Polished documentation, FINAL_REPORT.md, interview pitch | `feat/T-018-final-release` | Backlog |
