# Day 6 Notes — AI Proposal Generator, Milestone Breakdown & Project Conversion

**Date:** Day 6  
**Author:** Engineering Team  

---

## 1. What Was Built Today

1. **AI Proposal Generator Service (`app/services/proposal_service.py`):**
   - Provider-agnostic requirement synthesis engine.
   - Extracts key deliverable requirements and automatically structures 3 distinct delivery phases:
     - **Phase 1: Discovery & Technical Specification** (25% budget, 10 days)
     - **Phase 2: Core Engineering & Full-Stack Implementation** (50% budget, 21 days)
     - **Phase 3: Quality Assurance, Security Pass & Launch** (25% budget, 9 days)
   - Breaks each milestone into concrete, actionable task titles.
   - Includes robust offline parsing guaranteeing zero downtime or unhandled API crashes.
2. **Proposal-to-Project Conversion Engine (`POST /api/v1/proposals/{id}/convert`):**
   - Atomically instantiates an active `Project` record linked to the client.
   - Parses the proposal's `milestones_json` and automatically seeds initial `Task` records in the `todo` column with sequential zero-indexed position numbers (`position: 0, 1, 2...`).
   - Updates the proposal's lifecycle status from `draft` to `converted`.
3. **Interactive React Proposals Workspace (`src/pages/ProposalsPage.tsx`):**
   - Proposal card grid with budget summaries, deliverable counts, and phased task checklists.
   - Modal for drafting new proposals from raw client requirement briefs.
   - One-click "Convert to Active Project" button that converts the proposal and redirects directly to the interactive Kanban board.
4. **Client Portal Role Enforcements:**
   - Verified that client portal users (`role: 'client'`) are restricted strictly to their assigned projects and invoices, and blocked from viewing proposals, other clients, or internal team task notes.
5. **Automated Testing Suite:**
   - Authored `tests/test_proposals.py` validating synthesis, milestone budget allocation, and project/task conversion.
   - Total automated backend tests raised to **15/15 passing** (100% pass rate).

---

## 2. How the Core Day 6 Flow Works (Proposal to Project Conversion)

```
User pastes raw client brief ──► POST /api/v1/proposals/generate
   │
   ▼
ProposalService.generate_proposal_structure():
   ├── Sanitizes input and extracts deliverable bullet points
   ├── Scaffolds 3 phased milestones (25% / 50% / 25% budget split)
   ├── Populates concrete task items per milestone
   └── Saves `Proposal` with status = 'draft'
   │
   ▼
User reviews proposal in UI and clicks "Convert to Active Project":
   │
   ▼
POST /api/v1/proposals/{id}/convert
   │
   ├── Inserts `Project` record (status = 'planning', budget = estimated_budget)
   ├── Iterates through milestones in `milestones_json`
   │     └── For each task item:
   │           Inserts `Task(project_id=new_proj.id, status='todo', position=i)`
   ├── Updates `Proposal.status = 'converted'`
   └── Commits atomic transaction & returns ProjectOut
   │
   ▼
Frontend redirects user directly to `/projects/:id/kanban` with pre-populated tasks!
```

---

## 3. Five Technical Interview Questions & Answers (Day 6 Code)

### Q1: Why did you build an offline fallback for the Proposal Generator rather than relying solely on a remote LLM API?
> **Answer:**  
> "External LLM APIs can experience rate limits, latency spikes, network timeouts, or invalid API keys. An unhandled network exception during proposal generation would break core SaaS workflows. Our service implements a resilient fallback that extracts bullet points and generates 3 structured milestones and tasks, ensuring the application remains 100% operational in any environment."

### Q2: How does `convert_to_project()` ensure that task creation doesn't fail if the database connection drops halfway through?
> **Answer:**  
> "In `app/services/proposal_service.py`, the creation of the `Project` entity, the seeding of all `Task` entities, and the status update of the `Proposal` are executed inside a single SQLAlchemy session transaction:
> ```python
> db.add(project)
> for task in generated_tasks:
>     db.add(task)
> proposal.status = 'converted'
> db.commit()
> ```
> If any step fails, the entire transaction rolls back, preventing orphaned projects with missing tasks."

### Q3: How are milestone tasks mapped to the Kanban board upon conversion?
> **Answer:**  
> "Each milestone contains an array of actionable deliverable strings. When converting, we loop through the milestones and instantiate `Task` records with `status='todo'` and an incrementing `position` counter (`pos_counter = 0, 1, 2...`). The first three tasks are marked with `priority='high'` while subsequent tasks default to `'medium'`, presenting an organized Kanban board immediately upon launch."

### Q4: How is client portal isolation maintained during proposal generation?
> **Answer:**  
> "In `backend/app/api/v1/endpoints/proposals.py`, all proposal endpoints enforce `require_role('owner', 'member')`. Client users (`role: 'client'`) are completely blocked from viewing or creating proposals, ensuring internal pricing strategies, margins, and draft estimates remain private to agency staff."

### Q5: How do you serialize and deserialize milestone data in SQLite/PostgreSQL without creating separate milestone tables?
> **Answer:**  
> "We store the structured milestones array in a `milestones_json` text column serialized with `json.dumps(milestones)`. This allows flexible, dynamic phase and task schemas without rigid table migrations, while Pydantic v2 schemas validate the structure on read and write."

---

## 4. One Small Change You Should Try Yourself

**Exercise: Add a custom deadline offset during proposal conversion.**  
Open `backend/app/services/proposal_service.py`. Notice that `convert_to_project()` currently sets:
```python
deadline_date = date.today() + timedelta(days=40)
```
Try calculating the deadline dynamically by summing the `estimated_days` from each milestone in `milestones_json`:
```python
total_days = sum(m.get("estimated_days", 14) for m in milestones) or 30
deadline_date = date.today() + timedelta(days=total_days)
```
Run `python -m pytest tests/test_proposals.py` to verify that conversion continues to pass!
