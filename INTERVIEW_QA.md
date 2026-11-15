# Technical Interview Questions & Answers — ProjectPilot

Based on the actual codebase in `projectpilot` (`github.com/prachizala/projectpilot`).

---

### Question 1: How does ProjectPilot implement zero-trust multi-tenancy and prevent Insecure Direct Object Reference (IDOR / BOLA) vulnerabilities?
**Answer:**  
In ProjectPilot, every resource query (Clients, Projects, Tasks, Invoices, Proposals) strictly binds data access to the authenticated user's session identifier inside FastAPI dependency injection:

```python
# Multi-tenant isolation pattern
client = db.query(Client).filter(
    Client.id == client_id,
    Client.owner_id == current_user.id
).first()

if not client:
    raise HTTPException(status_code=404, detail="Client not found")
```

**Key Architectural Decisions:**
1. **HTTP 404 over HTTP 403:** If User A attempts to request `/api/v1/clients/{id}` belonging to User B, the endpoint returns an HTTP 404 Not Found rather than 403 Forbidden. This completely eliminates resource ID enumeration attacks, preventing attackers from probing valid integer or UUID ranges.
2. **Dual-Token Authentication with Argon2id:** Passwords are encrypted using memory-hard Argon2id (`passlib[argon2]`). JWT access tokens expire after 15 minutes and carry role claims (`owner`, `member`, `client`), while refresh tokens expire in 7 days and must be validated against database state.
3. **Role-Based Client Portal Isolation:** When a user with `role == 'client'` logs in, endpoints enforce `require_client_or_owner()`. Client users are restricted strictly to projects and invoices where `client_id == current_user.client_id` and are barred from write operations or internal team proposal drafts.

---

### Question 2: Why did you choose contiguous sequential integer normalization over floating-point midpoint indexing for the Kanban board?
**Answer:**  
In collaborative Kanban boards, moving a task between existing cards requires recalculating position:
- **Midpoint Indexing Flaw:** In naive implementations (e.g. assigning $pos_{new} = \frac{pos_{prev} + pos_{next}}{2}$), rapid drags in the same slot quickly degrade into tiny floating-point fractions (e.g. $1.0000000000000002$). Eventually, IEEE 754 precision limits cause rounding collisions where two distinct cards receive identical positions, causing erratic UI card swapping.
- **ProjectPilot's Integer Engine (`KanbanService.reorder_task`):**  
  Our backend uses contiguous zero-indexed sequential integers (`0, 1, 2, 3...`):
  ```python
  # Fetch all siblings in destination column excluding the moving task
  siblings = db.query(Task).filter(
      Task.project_id == project_id,
      Task.status == target_status,
      Task.id != task_id
  ).order_by(Task.position.asc()).all()

  # Insert the moving task at target_position and re-index sequentially
  siblings.insert(target_position, task)
  for index, sibling in enumerate(siblings):
      sibling.position = index
  db.commit()
  ```
  This guarantees deterministic card ordering across all devices, zero precision degradation, and consistent state across concurrent sessions in a single database transaction.

---

### Question 3: How does the server-side PyMuPDF invoice generator work, and how did you prevent memory leaks?
**Answer:**  
In `backend/app/services/invoice_service.py`, invoices are rendered dynamically as vector PDFs in memory:
1. **Sub-15ms Latency:** Rather than spawning a heavy headless Chromium browser via Puppeteer (which consumes 200MB+ RAM and takes 1–2 seconds per PDF), we use PyMuPDF (`fitz`), a C-library binding that generates vector drawing primitives (rectangles, table rules, and typographic typography) directly into a memory buffer (`fitz.open() -> doc.write()`).
2. **Deterministic Financial Math:**
   - Subtotal: $\sum (\text{quantity} \times \text{unit\_price})$
   - Tax: $\text{subtotal} \times (\frac{\text{tax\_rate}}{100.0})$
   - Total: $\text{subtotal} + \text{tax}$
3. **Memory Safety & C-Reclamation:** PyMuPDF operates on an underlying C-heap. To guarantee that abandoned PDF buffers do not cause memory leaks in high-throughput FastAPI processes, generation is enclosed in a strict `try...finally` block:
   ```python
   doc = fitz.open()
   try:
       page = doc.new_page(width=595, height=842) # A4 format
       # Draw header, client details, line-item grid, totals...
       pdf_bytes = doc.write()
       return pdf_bytes
   finally:
       doc.close() # Guarantees immediate C-level memory deallocation
   ```
   The bytes are streamed directly via `Response(content=pdf_bytes, media_type="application/pdf")`.

---

### Question 4: How does the AI Proposal Generator convert raw requirements into a live Kanban project atomically?
**Answer:**  
In `backend/app/services/proposal_service.py`, client requirements are transformed into active projects through a two-step pipeline:
1. **Structure Synthesis:** The engine parses requirements into 3 balanced delivery phases (Phase 1: Discovery @ 25%, Phase 2: Implementation @ 50%, Phase 3: QA & Launch @ 25%) with estimated delivery days and concrete task checklists. If an external LLM API key is unavailable, a deterministic heuristic extractor activates automatically, ensuring zero runtime crashes.
2. **Atomic Project & Task Instantiation (`POST /api/v1/proposals/{id}/convert`):**
   ```python
   # Inside a single SQLAlchemy transaction
   project = Project(
       name=proposal.title,
       client_id=proposal.client_id,
       owner_id=current_user.id,
       status="planning",
       budget=proposal.estimated_budget,
       deadline=date.today() + timedelta(days=40)
   )
   db.add(project)
   db.flush() # Resolves project.id for foreign keys

   pos = 0
   for milestone in proposal.milestones_json:
       for task_title in milestone.get("tasks", []):
           db.add(Task(
               project_id=project.id,
               title=task_title,
               status="todo",
               position=pos,
               priority="high" if pos < 3 else "medium"
           ))
           pos += 1

   proposal.status = "converted"
   db.commit()
   ```
   Executing project creation, task generation, and proposal status update in a single atomic database transaction prevents orphaned records if a failure occurs halfway through.

---

### Question 5: Describe a complex technical hurdle you encountered and solved in ProjectPilot.
**Answer:**  
**The Problem:** During Day 1 database schema design, SQLAlchemy threw a circular dependency error during table creation:
- A `User` with `role == 'client'` points to `Client.id` via `User.client_id`.
- Simultaneously, every `Client` belongs to an agency owner via `Client.owner_id`, pointing to `User.id`.
When generating foreign keys, SQLite and PostgreSQL could not determine which table to create first.

**The Solution:**  
I resolved the circular foreign key constraint using SQLAlchemy's `ForeignKey(..., use_alter=True, name="fk_users_client_id")`:
```python
client_id = Column(
    Integer,
    ForeignKey("clients.id", ondelete="SET NULL", use_alter=True, name="fk_users_client_id"),
    nullable=True
)
```
This instructed SQLAlchemy and Alembic migrations to create the tables first without circular constraints and apply the `client_id` foreign key via an `ALTER TABLE` step once both tables exist, cleanly resolving circularity while preserving referential integrity.
