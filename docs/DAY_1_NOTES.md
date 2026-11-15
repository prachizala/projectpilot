# Day 1 Notes — ProjectPilot Architecture & Authentication Foundation

**Date:** Day 1  
**Author:** Engineering Team  

---

## 1. What Was Built Today

1. **Project Specification Suite:**
   - `PRD.md`: Outlined user personas (Owner, Member, Client), MoSCoW prioritization, and user stories.
   - `ARCHITECTURE.md`: Established system topology, relational schema (ERD), OpenAPI REST contract, and tenant isolation rules.
   - `DESIGN.md`: Defined layout tokens, persistent responsive app shell, Kanban column specs, and state patterns.
   - `TASKS.md`: Initialized the 18-task sprint board tracking features across the 7-day schedule.
2. **Backend Application Foundation:**
   - Configured FastAPI with Pydantic v2 settings (`app/core/config.py`).
   - Setup SQLAlchemy database session pooling (`app/core/database.py`).
   - Implemented relational entity models (`app/models/models.py`): `User`, `Client`, `Project`, `Task`, `Invoice`, `InvoiceItem`, `Proposal`.
   - Built cryptographic security service with Argon2id password hashing and HS256 JWT access/refresh token generation (`app/core/security.py`).
   - Built authentication endpoints: `/api/v1/auth/signup`, `/api/v1/auth/login`, `/api/v1/auth/refresh`, and `/api/v1/auth/me`.
   - Setup automated test framework with 6/6 passing tests covering hashing, signup, duplicate handling, login, token refresh, unauthorized rejection, and relational cascading.

---

## 2. How the Core Day 1 Flow Works (Authentication & RBAC)

```
Client (Frontend)
   │
   ├─► POST /api/v1/auth/signup ──► Validates email/password with Pydantic
   │                                  │
   │                                  ▼
   │                              Hashes password with Argon2id (salt + memory cost)
   │                                  │
   │                                  ▼
   │                              Inserts into 'users' table
   │                                  │
   │                                  ▼
   │                              Generates Token Pair:
   │                                - Access Token (JWT, 15m lifetime, payload: {sub, role})
   │                                - Refresh Token (JWT, 7d lifetime, payload: {sub, type})
   │
   ├─► Protected Requests ────────► Header: "Authorization: Bearer <access_token>"
   │                                  │
   │                                  ▼
   │                              `get_current_user` dependency:
   │                                - Decodes JWT using SECRET_KEY & HS256
   │                                - Validates expiration timestamp ('exp')
   │                                - Queries database for active user record
   │                                - Rejects with HTTP 401 if expired or invalid
   │
   └─► Token Refresh ─────────────► POST /api/v1/auth/refresh {refresh_token}
                                      │
                                      ▼
                                  Decodes refresh token, confirms 'type == refresh',
                                  and issues a fresh 15-minute access token.
```

---

## 3. Five Technical Interview Questions & Answers (Day 1 Code)

### Q1: Why did you choose Argon2id over classic bcrypt or SHA-256 for password hashing?
> **Answer:**  
> "Argon2id won the Password Hashing Competition (PHC) and is the primary OWASP recommendation. Unlike SHA-256 (which is vulnerable to ultra-fast GPU and ASIC brute-forcing) or standard bcrypt, Argon2id is hybrid: it protects against side-channel cache-timing attacks (like Argon2i) and GPU-accelerated parallel attacks by enforcing both CPU computation time and memory hardness (like Argon2d)."

### Q2: How does your JWT token strategy separate access tokens and refresh tokens?
> **Answer:**  
> "In `app/core/security.py`, we issue short-lived **access tokens** (15-minute lifetime) containing the user ID and role (`role: 'owner'|'member'|'client'`). This limits the window of exposure if a token is intercepted. To prevent users from having to constantly log in, we also issue a long-lived **refresh token** (7-day lifetime) with `type: 'refresh'`. The `/auth/refresh` endpoint accepts only tokens explicitly stamped with `type: 'refresh'`, verifying that access tokens cannot be recycled to request new tokens."

### Q3: What is the purpose of `use_alter=True` on the `User.client_id` foreign key relationship?
> **Answer:**  
> "In `app/models/models.py`, `Client` has a foreign key to `User` (`owner_id`), while `User` optionally links back to `Client` (`client_id`) for client portal users. This creates a circular dependency in the database schema. In SQLite (which does not support deferred constraint checking by default during metadata teardown), `use_alter=True` instructs SQLAlchemy to drop or alter this constraint after table creation, avoiding unresolvable circular lockups during testing."

### Q4: How does your authentication dependency prevent Direct Object Reference (IDOR) attacks?
> **Answer:**  
> "The `get_current_user` dependency in `app/services/auth_service.py` extracts and validates the subject ID directly from the cryptographic signature of the JWT token. Downstream endpoints never trust client-supplied owner IDs in the URL or payload; instead, queries explicitly filter by `owner_id == current_user.id`. For client roles, access is restricted strictly to records matching `current_user.client_id`."

### Q5: How is in-memory SQLite isolation configured for Pytest?
> **Answer:**  
> "In `backend/tests/conftest.py`, we use `create_engine('sqlite:///:memory:', poolclass=StaticPool, connect_args={'check_same_thread': False})`. SQLite in-memory databases are normally destroyed when a connection closes; `StaticPool` maintains a single persistent connection across the test session while our test fixtures handle transactional rollback (`transaction.rollback()`), guaranteeing zero state pollution between tests and sub-second execution speeds."

---

## 4. One Small Change You Should Try Yourself

**Exercise: Add minimum password strength validation in Pydantic.**  
Open `backend/app/schemas/auth.py`. Notice that `UserCreate` currently validates `password: str = Field(..., min_length=6, max_length=128)`.
Try adding a `@field_validator('password')` method to enforce that the password contains at least one digit:
```python
@field_validator("password")
@classmethod
def validate_password_strength(cls, v: str) -> str:
    if not any(char.isdigit() for char in v):
        raise ValueError("Password must contain at least one numerical digit.")
    return v
```
Run `python -m pytest tests/test_auth.py` and see what happens when a test registers with a password lacking digits!
