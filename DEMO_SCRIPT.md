# ProjectPilot — Live Demo & Interview Pitch Script

**Duration:** ~2 Minutes  
**Audience:** Technical Interviewers, Engineering Managers, Product Evaluators  
**Speaker:** Prachi Zala (Creator & Full-Stack Developer)  

---

## 1. 30-Second Elevator Pitch

> *"Hi, I'm Prachi Zala. I built **ProjectPilot**, a full-stack client and project management SaaS designed for freelancers and boutique agencies.
>
> Freelancers and small studios often lose hours juggling client communications on WhatsApp, tracking task deadlines across disparate spreadsheets, and manually typing out invoices in Word. ProjectPilot consolidates this entire lifecycle into a single, cohesive platform: from automated AI proposal generation and one-click project conversion to an interactive drag-and-drop Kanban board, vector PDF invoice generation, and a secure client portal.
>
> I built it with FastAPI and SQLAlchemy on the backend, React with TypeScript and Tailwind on the frontend, and containerized the entire stack with Docker Compose and automated GitHub Actions CI."*

---

## 2. 90-Second Technical Demo Walkthrough

### Step 1: Authentication & Role-Based Access Control (0:00 - 0:20)
- **Action:** Open `http://localhost:5173` and click **"Demo Owner Account"** (or log in with `demo@projectpilot.io` / `Password123!`).
- **Talking Point:** *"Notice the clean authentication flow. We use JWT tokens with Argon2id password hashing. The system supports three distinct roles: Owner, Team Member, and Client, each strictly isolated at the database query layer."*

### Step 2: The Executive Dashboard (0:20 - 0:35)
- **Action:** Point out the top 4 KPI widgets and the Recharts revenue stream chart.
- **Talking Point:** *"The dashboard aggregates financial and operational health in real time: active projects, pending invoice balances, overdue tasks, and a 6-month monthly revenue area chart. All figures are dynamically calculated using SQLAlchemy aggregate queries rather than heavy client-side filtering."*

### Step 3: Interactive Kanban Board (0:35 - 0:50)
- **Action:** Navigate to **Projects**, select *"E-Commerce Replatforming"*, and switch to the **Tasks** tab. Drag a card from *In Progress* to *Review*.
- **Talking Point:** *"The Kanban board uses optimistic UI updates for instant feedback while synchronizing state via a dedicated position-rebalancing endpoint. We use zero-indexed sequential integers with contiguous normalization, which prevents the floating-point precision bugs common in naive midpoint indexing."*

### Step 4: AI Proposal Generation & Project Conversion (0:50 - 1:10)
- **Action:** Navigate to **Proposals**, open *"AI Customer Support Bot Proposal"*, or click **"New Proposal"** and generate from client notes. Then click **"Convert to Active Project"**.
- **Talking Point:** *"Here is our proposal engine. You can paste raw client requirements, and our structured prompt parser extracts the project scope, recommended milestones, and estimated budget. With one click on 'Convert to Project', an active project is instantiated and all extracted milestone tasks are atomically populated directly onto the project's Kanban board."*

### Step 5: Invoicing & Vector PDF Generation (1:10 - 1:25)
- **Action:** Go to **Invoices**, select invoice `#INV-2026-001`, and click **"Download PDF"**.
- **Talking Point:** *"For invoicing, we render vector-based, print-ready PDF documents directly in memory using PyMuPDF in under 15 milliseconds. It avoids the heavy memory overhead and headless browser dependencies of tools like Puppeteer, and we wrap it in strict `try...finally` resource cleanups to ensure zero C-level memory leaks."*

### Step 6: Client Portal & Wrap-up (1:25 - 1:30)
- **Action:** Log out and log in as client `sarah@apexdesign.com` / `Password123!`.
- **Talking Point:** *"Finally, logging in as a client restricts visibility exclusively to that company's active projects and invoices. Everything is covered by automated pytest and Vitest suites running in GitHub Actions CI."*

---

## 3. Anticipated Technical Deep-Dive Questions

### Q1: *"How do you handle multi-tenancy and prevent IDOR (Insecure Direct Object Reference)?"*
> **Answer:** *"Every query in our FastAPI router dependencies filters by `owner_id == current_user.id`. If a user attempts to access an ID belonging to another tenant, the API returns a 404 Not Found rather than a 403 Forbidden. This prevents ID enumeration attacks and ensures complete tenant isolation."*

### Q2: *"Why did you use PyMuPDF instead of WeasyPrint or Puppeteer for PDF generation?"*
> **Answer:** *"Puppeteer requires launching a full headless Chromium browser process, which consumes 200MB+ of RAM per request and introduces significant latency. WeasyPrint requires complex system cairo/pango dependencies. PyMuPDF is a lightweight C-library binding that generates vector PDFs in memory in ~12 milliseconds with zero external OS packages, making our Docker containers lean and fast."*

### Q3: *"How does the Kanban reordering algorithm work under the hood?"*
> **Answer:** *"When a task moves to a new position in a column, the backend fetches all siblings in that column ordered by their existing rank. It inserts the moved task at the target index and reassigns contiguous sequential integers (0, 1, 2, 3...) to every sibling in a single database transaction. This eliminates fractional float rounding errors and keeps the database clean."*
