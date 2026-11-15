# Product Requirements Document (PRD) — ProjectPilot

**Product Name:** ProjectPilot  
**Tagline:** Modern Client & Project Management SaaS for Freelancers and Boutique Agencies  
**Document Version:** 1.0.0 (Day 1 Scope Freeze)  
**Author:** Product Manager  

---

## 1. Executive Summary & Problem Statement

Independent freelancers and small agencies juggle project delivery across fragmented channels:
- Client communications and requirement changes happen across WhatsApp and email threads.
- Scope, milestones, and task statuses are tracked in disparate spreadsheets.
- Invoices are drafted manually in text editors, leading to calculation discrepancies and delayed billings.
- Drafting structured proposals from unstructured client briefs consumes hours of unpaid administrative time.

**ProjectPilot** consolidates client relations, project workspaces, drag-and-drop Kanban execution, vector PDF invoicing, and automated proposal scaffolding into an integrated, multi-tenant web application.

---

## 2. Target Personas

### Persona 1: Agency Founder / Freelancer (`role: owner`)
- **Needs:** Centralized oversight of active clients, contract values, project delivery states, overdue tasks, and revenue pipeline.
- **Pain Point:** Lack of unified visibility; high administrative burden drafting estimates and invoices.

### Persona 2: Project Associate (`role: member`)
- **Needs:** Clear task prioritization, interactive Kanban workflow, task status updates, and milestone deadlines.
- **Pain Point:** Unclear task priorities, scope creep, lack of context on client requirements.

### Persona 3: Agency Client (`role: client`)
- **Needs:** A dedicated, transparent Client Portal to track project progress, milestone completions, and download official invoices.
- **Pain Point:** Anxious about project delivery timelines; constantly messaging founders for status updates.

---

## 3. Scope Definition (MoSCoW Matrix)

### MUST HAVE (Core MVP)
1. **Authentication & Multi-Role Authorization:**
   - Email/password signup, login, JWT token pair (access + refresh), bcrypt password hashing.
   - Strict Role-Based Access Control (`owner`, `member`, `client`).
2. **Client Management:**
   - CRUD operations for clients (name, company, email, phone, notes, address).
   - Direct aggregation of active projects and total billed amounts.
3. **Project Management:**
   - CRUD operations for projects tied to clients (title, description, status, budget, deadline).
   - Status transitions: `planning` → `in_progress` → `in_review` → `completed` → `on_hold`.
4. **Kanban Task Board:**
   - 4-column workflow: `todo`, `in_progress`, `review`, `done`.
   - Drag-and-drop interaction with persistent fractional or integer order index saving.
5. **Executive Dashboard:**
   - Real-time KPI cards: Active Projects, Total Clients, Overdue Tasks, Gross Revenue.
   - Interactive charts: Monthly revenue trends, project status distribution.

### SHOULD HAVE (Key Differentiators)
6. **Invoicing Engine:**
   - Line items with quantity, unit price, tax calculation (e.g., 18% GST), and payment terms.
   - Server-side vector PDF generation and instant download.
   - Status tracking: `draft`, `sent`, `paid`, `overdue`.
7. **Proposal Generator:**
   - Input: Unstructured client requirements or meeting notes.
   - Output: Structured project scope, proposed milestones, estimated budget, and task list.
   - One-click action to convert an approved proposal into an active `Project` + `Tasks`.
8. **Client Portal:**
   - Dedicated portal login restricting client visibility strictly to their own projects and invoices.

### COULD HAVE (Future Enhancements)
9. Activity audit log and comment feeds.
10. Automated email reminders for upcoming deadlines and overdue invoices.
11. Advanced global search and multi-column sorting.

---

## 4. User Stories & Acceptance Criteria

### US-01: Authentication & Session Management
- **As an** agency owner or team member,
- **I want to** authenticate with email and password and receive a secure JWT token,
- **So that** my data is isolated and protected against unauthorized access.
- **Acceptance Criteria:**
  - Password must be hashed using bcrypt before database insertion.
  - Returns `access_token` (15-min lifetime) and `refresh_token` (7-day lifetime).
  - Protected endpoints reject missing, expired, or tampered tokens with HTTP 401.

### US-02: Client Directory Management
- **As an** agency owner,
- **I want to** create and update client profiles,
- **So that** all business engagements are organized by client entity.
- **Acceptance Criteria:**
  - Client emails must be unique per owner account.
  - Deleting a client with active projects requires explicit confirmation or rejection.

### US-03: Project Lifecycle Tracking
- **As an** agency owner or member,
- **I want to** create projects assigned to clients with deadlines and budgets,
- **So that** our delivery team has clear scope and financial bounds.
- **Acceptance Criteria:**
  - Budget must be a non-negative numerical value.
  - Deadline validation enforces proper ISO date formats.

### US-04: Kanban Task Prioritization
- **As a** team member,
- **I want to** drag and drop tasks between status columns and reorder them within a column,
- **So that** our workflow state is transparent and real-time.
- **Acceptance Criteria:**
  - Moving a card across columns updates its `status` and `position` index in the database.
  - Board re-renders optimistically with graceful fallback if the network request fails.

### US-05: Automated Proposal Scaffolding
- **As an** agency owner,
- **I want to** generate a structured proposal from raw client requirements,
- **So that** I can send detailed quotes within minutes.
- **Acceptance Criteria:**
  - Parses client input into deliverables, milestones, and estimated costs.
  - Clicking "Convert to Project" instantiates an active project record with pre-populated tasks.

---

## 5. Non-Functional Requirements
- **Performance:** Sub-100ms API response time on standard CRUD endpoints under local SQLite / PostgreSQL.
- **Security:** Strict tenant isolation; users can only query resources where `owner_id == current_user.id` (or `client_id` for client users).
- **Reliability:** 100% test coverage on authentication, role authorization, and core business calculations.
