# Day 2 Notes — Clients & Projects API, Multi-Tenancy & Client Portal

**Date:** Day 2  
**Author:** Engineering Team  

---

## 1. What Was Built Today

1. **Clients REST API (`/api/v1/clients`):**
   - Implemented full CRUD with Pydantic v2 validation (`ClientCreate`, `ClientUpdate`, `ClientOut`).
   - Integrated real-time query aggregation computing `projects_count` and `total_billed` across invoices.
   - Built case-insensitive search (`?q=<keyword>`) spanning client name, company, and email address.
   - Enforced strict tenant isolation: agency owners can only access clients linked to their own `owner_id`.
2. **Projects REST API (`/api/v1/projects`):**
   - Implemented full CRUD (`ProjectCreate`, `ProjectUpdate`, `ProjectOut`).
   - Added status filtering (`?status=planning|in_progress|in_review|completed|on_hold`).
   - Added cross-tenant validation: an agency owner cannot create a project pointing to another agency's client ID.
   - Implemented **Client Portal Isolation**: when a client user (`role: 'client'`) queries `/projects`, the query automatically scopes down to `Project.client_id == current_user.client_id`.
3. **Automated Testing Suite:**
   - Authored `tests/test_clients.py` and `tests/test_projects.py`.
   - Raised total automated test count to **11/11 tests passing** (100% pass rate).

---

## 2. How the Core Day 2 Flows Work

### A. Multi-Tenant Isolation Flow
```
Incoming Request: GET /api/v1/clients/42
   │
   ▼
Extract Bearer Token ──► `get_current_user` decodes JWT signature
   │
   ▼
Extract `current_user.id` (e.g., User ID: 5)
   │
   ▼
SQLAlchemy Query:
   SELECT * FROM clients
   WHERE id = 42 AND owner_id = 5
   │
   ├── If record matches: Return ClientOut (HTTP 200)
   └── If record belongs to another user (owner_id = 9): Return HTTP 404 (Not Found)
```
*Security note:* Returning HTTP 404 rather than HTTP 403 prevents attackers from enumerating valid resource IDs across different tenants.

### B. Client Portal Role Scoping
```
Client User logs in ──► JWT issued with `role: "client"` and `client_id: 12`
   │
   ▼
Request: GET /api/v1/projects
   │
   ▼
Endpoint inspects `current_user.role`:
   if current_user.role == "client":
       query = db.query(Project).filter(Project.client_id == current_user.client_id)
   else:
       query = db.query(Project).filter(Project.owner_id == current_user.id)
   │
   ▼
Client user sees strictly their company's projects, with zero visibility into other agency clients.
```

---

## 3. Five Technical Interview Questions & Answers (Day 2 Code)

### Q1: Why did you return HTTP 404 rather than HTTP 403 when a user accesses another tenant's client ID?
> **Answer:**  
> "Returning HTTP 403 Forbidden confirms that the resource ID exists on the server, which facilitates resource enumeration attacks. Returning HTTP 404 Not Found conceals the existence of other tenants' data entirely, treating unauthorized IDs as nonexistent."

### Q2: How does the Clients API calculate `projects_count` and `total_billed` without N+1 query overhead?
> **Answer:**  
> "In `app/api/v1/endpoints/clients.py`, we execute aggregate subqueries using SQLAlchemy `func.count(Project.id)` and `func.sum(Invoice.total_amount)`. In production with hundreds of clients, we can bundle this into a single `LEFT OUTER JOIN` with `GROUP BY clients.id`, ensuring a single SQL query execution."

### Q3: How do you prevent cross-tenant foreign key hijacking when creating a project?
> **Answer:**  
> "When `POST /api/v1/projects` receives a `client_id`, we never blindly insert it. In `create_project()`, we execute a preliminary verification query:
> ```python
> client = db.query(Client).filter(Client.id == project_in.client_id, Client.owner_id == current_user.id).first()
> ```
> If the client does not belong to the authenticated owner, the request is aborted with an HTTP 404, preventing an attacker from associating their projects with an arbitrary company."

### Q4: How does status filtering work in `list_projects`?
> **Answer:**  
> "The endpoint takes an optional query parameter `status_filter: Optional[str] = Query(None, alias='status')`. If provided, it dynamically chains `.filter(Project.status == status_filter.lower())` onto the base query before executing `.all()`. Pydantic schemas further validate that project statuses adhere strictly to the allowed enum (`planning`, `in_progress`, `in_review`, `completed`, `on_hold`)."

### Q5: How do you support multi-field search in `list_clients`?
> **Answer:**  
> "We construct a SQL `OR` filter using SQLAlchemy's `or_` conjunction:
> ```python
> search_pattern = f'%{q.strip()}%'
> query.filter(or_(
>     Client.name.ilike(search_pattern),
>     Client.company.ilike(search_pattern),
>     Client.email.ilike(search_pattern)
> ))
> ```
> Using `.ilike()` ensures case-insensitive matching across SQLite and PostgreSQL."

---

## 4. One Small Change You Should Try Yourself

**Exercise: Add a minimum budget constraint check.**  
Open `backend/app/schemas/project.py`. The budget field currently enforces `budget: float = Field(0.0, ge=0.0)`.
Try creating a custom `@field_validator('deadline')` to verify that new project deadlines cannot be set in the past:
```python
from datetime import date

@field_validator("deadline")
@classmethod
def validate_deadline_not_past(cls, v: Optional[date]) -> Optional[date]:
    if v and v < date.today():
        raise ValueError("Project deadline cannot be in the past.")
    return v
```
Run `python -m pytest tests/test_projects.py` to verify that existing tests pass, and then write a test with a yesterday deadline to observe the Pydantic 422 validation response.
