# Day 3 Notes — React SPA Setup, Auth State, Protected Routes, Clients & Projects UI

**Date:** Day 3  
**Author:** Engineering Team  

---

## 1. What Was Built Today

1. **Vite + React + TypeScript Single Page Application (`frontend/`):**
   - Configured Vite 5 with `@vitejs/plugin-react` and local backend reverse proxy (`/api` -> `http://localhost:8000`).
   - Integrated Tailwind CSS with custom brand colors (`#2563eb`), Inter typography, and responsive layouts.
   - Set up TypeScript definitions in `src/types/index.ts` strictly mirroring backend Pydantic models.
2. **Centralized API Client with Transparent Token Refresh (`src/api/client.ts`):**
   - Built a lightweight `ApiClient` class managing `access_token` and `refresh_token` in `localStorage`.
   - Automatically attaches `Authorization: Bearer <access_token>` to outgoing requests.
   - Intercepts HTTP 401 Unauthorized responses, transparently calls `/api/v1/auth/refresh`, updates tokens, and retries the original request without user interruption.
3. **Session Management & Route Guards (`src/context/` & `src/components/common/`):**
   - `AuthContext`: Provides `user`, `isAuthenticated`, `isLoading`, `login()`, `signup()`, and `logout()`.
   - `ProtectedRoute`: Guards authenticated routes and enforces `allowedRoles: ['owner', 'member']` to shield administrative pages from Client Portal users.
4. **Responsive App Shell (`src/components/layout/AppLayout.tsx`):**
   - Persistent 64px dark slate sidebar with brand identity, role status pill (`Owner`, `Member`, `Client`), and navigation links.
   - Clean top application bar showing active workspace and environment badge.
5. **Interactive Core Management Pages:**
   - **`LoginPage` & `SignupPage`:** Form validation, error state callouts, and instant session bootstrapping.
   - **`ClientsPage`:** Multi-field live search, table with project count and total billed metrics, modal form for new client registration, and delete confirmation.
   - **`ProjectsPage`:** Filter tabs by delivery status (`all`, `in_progress`, `planning`, `in_review`, `completed`), project cards with budget and deadline tags, modal for creating projects linked to clients, and direct navigation into Kanban boards.

---

## 2. How the Core Day 3 Flow Works (Transparent Token Refresh)

```
User Action (e.g. clicks "Add Client")
   │
   ▼
ApiClient.request('/clients', { method: 'POST' })
   │
   ├── Attach header: "Authorization: Bearer <access_token>"
   │
   ▼
Backend returns HTTP 401 (Access Token expired after 15 minutes)
   │
   ▼
ApiClient Interceptor activates:
   │
   ├── Reads stored `refresh_token` (7-day lifetime)
   ├── POST /api/v1/auth/refresh { refresh_token }
   │
   ├── If Refresh Succeeds:
   │     - Stores fresh `access_token`
   │     - Re-executes original POST /clients with new token
   │     - UI completes smoothly without error modal
   │
   └── If Refresh Fails (token revoked or expired):
         - Clears all tokens from localStorage
         - Redirects user cleanly to `/login`
```

---

## 3. Five Technical Interview Questions & Answers (Day 3 Code)

### Q1: How does your React application prevent infinite loops when refreshing expired tokens?
> **Answer:**  
> "In `src/api/client.ts`, the refresh call is targeted explicitly at `/auth/refresh` without calling the recursive `request()` wrapper. If the refresh request itself returns a non-200 status, we immediately clear all tokens from `localStorage` and trigger `window.location.href = '/login'`. This guarantees that an expired or revoked refresh token terminates the session cleanly instead of re-triggering endless 401 retries."

### Q2: How does `ProtectedRoute` implement role-based access control (RBAC) in React Router v6?
> **Answer:**  
> "In `src/components/common/ProtectedRoute.tsx`, the component checks `isLoading` first to prevent premature login redirects while local storage is being validated. It then checks `!isAuthenticated` to redirect unauthenticated visitors to `/login`. Finally, if an `allowedRoles` array is provided, it verifies `allowedRoles.includes(user.role)`. If unauthorized (e.g. a `client` trying to access `/clients`), it displays a tailored 'Access Restricted' screen rather than crashing or flashing unauthorized data."

### Q3: Why did you choose Tailwind CSS over a component library like MUI or Ant Design for ProjectPilot?
> **Answer:**  
> "Tailwind CSS provides zero runtime JavaScript overhead, resulting in sub-250KB total bundle size (our complete compiled JS is 245KB and CSS is 19.5KB). It allows complete architectural control over design tokens, responsive breakpoints, and animations without overriding heavy third-party CSS stylesheets."

### Q4: How is optimistic or synchronized state managed when creating new clients and projects?
> **Answer:**  
> "In `ClientsPage.tsx` and `ProjectsPage.tsx`, form submission triggers the API call, resets modal inputs, and immediately re-executes `fetchClients()` or `fetchData()`. For multi-tab filtering, `useEffect` depends on `activeTab`, dynamically passing the status parameter to `api.getProjects(status)` to guarantee server-synchronized data."

### Q5: How do you prevent layout shifts during authentication loading?
> **Answer:**  
> "In `App.tsx` and `ProtectedRoute.tsx`, `isLoading` displays an initial centered spinner maintaining screen proportions. Once auth status is resolved, the DOM transitions directly to the two-column sidebar layout, preventing cumulative layout shift (CLS)."

---

## 4. One Small Change You Should Try Yourself

**Exercise: Add an active search indicator badge.**  
Open `frontend/src/pages/ClientsPage.tsx`. In the search bar section, observe how `searchTerm` filters clients in real time.
Try displaying the match count right beside the search input:
```tsx
{searchTerm && (
  <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
    {clients.length} match{clients.length === 1 ? '' : 'es'}
  </span>
)}
```
Run `npm run build` inside `frontend/` to confirm that TypeScript compiles cleanly!
