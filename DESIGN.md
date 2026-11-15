# UI/UX Design System & Layout Guidelines — ProjectPilot

**Author:** UI/UX Designer  
**Version:** 1.0.0 (Day 1 Specification)  
**Status:** Approved  

---

## 1. Visual Hierarchy & Design System Tokens

ProjectPilot follows a clean, modern SaaS design language tailored for fast decision-making and low cognitive load.

### Color Palette (Tailwind CSS Mappings)

| Token Name | Hex Code | Tailwind Class | Semantic Purpose |
| :--- | :--- | :--- | :--- |
| **Primary Blue** | `#2563EB` | `bg-blue-600` | Primary actions, brand identity, active tabs |
| **Primary Hover** | `#1D4ED8` | `hover:bg-blue-700` | Button interactive hover state |
| **Slate Dark** | `#0F172A` | `bg-slate-900` | Sidebar navigation background, dark headers |
| **Slate Medium** | `#1E293B` | `bg-slate-800` | Card borders, secondary containers |
| **Neutral Canvas** | `#F8FAFC` | `bg-slate-50` | Main application content background |
| **Surface White** | `#FFFFFF` | `bg-white` | Content cards, modal dialogs, table rows |
| **Text Primary** | `#0F172A` | `text-slate-900` | Primary page headers, critical metrics |
| **Text Muted** | `#64748B` | `text-slate-500` | Secondary metadata, labels, captions |
| **Success Emerald** | `#10B981` | `text-emerald-600` | 'Paid' status, completed tasks, positive profit |
| **Warning Amber** | `#F59E0B` | `text-amber-500` | 'In Review' status, approaching deadlines |
| **Danger Rose** | `#EF4444` | `text-rose-600` | 'Overdue' tasks, unpaid invoices, destructive actions |

### Typography & Spacing
- **Font Family:** Inter / System UI sans-serif (`font-sans`)
- **Scale:**
  - `text-2xl font-bold` (Page Titles: 24px)
  - `text-lg font-semibold` (Card Headers: 18px)
  - `text-sm font-medium` (Body / Table rows: 14px)
  - `text-xs font-normal` (Captions / Badges: 12px)
- **Radii:** Consistent rounded corners (`rounded-xl` for cards, `rounded-lg` for buttons and inputs).

---

## 2. Information Architecture & Navigation

The layout follows a persistent responsive shell:
1. **Collapsible Left Sidebar:**
   - Agency Brand & Switcher
   - Navigation Items:
     - 📊 **Dashboard** (`/dashboard`)
     - 👥 **Clients** (`/clients`)
     - 📁 **Projects** (`/projects`)
     - 📋 **Kanban Board** (`/projects/:id/kanban`)
     - 🧾 **Invoices** (`/invoices`)
     - 💡 **Proposals** (`/proposals`)
     - ⚙️ **Settings & Profile** (`/settings`)
   - User Profile Card with Logout Trigger
2. **Top Application Bar:**
   - Breadcrumb navigation (`Projects > Mobile App Redesign > Tasks`)
   - Quick Action Button (`+ New Project`, `+ New Client`)
   - Role indicator badge (`Owner`, `Member`, or `Client`)
3. **Main Content Canvas:**
   - Dedicated scroll area with generous 24px (`p-6`) gutter.

---

## 3. Core Component Layouts

### A. Kanban Board Layout
- **Container:** Horizontal flex with `gap-6` and `overflow-x-auto`.
- **Columns (4):**
  - **To Do:** Neutral slate header with task count badge.
  - **In Progress:** Blue accent header indicating active work.
  - **In Review:** Amber accent header signaling verification.
  - **Done:** Emerald accent header representing completed milestones.
- **Card Primitives:**
  - Draggable handle with subtle grab cursor.
  - Title, priority badge (`High`, `Medium`, `Low`), assigned initials avatar, and due date.

### B. Executive Dashboard Layout
- **Top Row (4 Metric Cards):**
  - Active Projects, Total Clients, Overdue Tasks, Monthly Revenue.
- **Middle Row (2 Analytics Columns):**
  - Left (60%): 6-Month Revenue Bar / Area Chart using Recharts.
  - Right (40%): Project Status Distribution Donut Chart.
- **Bottom Row:** Recent Activity & Upcoming Deadlines list.

### C. State Handling Patterns
- **Loading State:** Skeleton shimmers (`animate-pulse bg-slate-200 rounded`) preserving layout geometry.
- **Empty State:** Illustrated SVG icon, bold headline, explanatory text, and primary call-to-action button (e.g., *"No clients added yet. Add your first client to start creating projects."*).
- **Error State:** Non-intrusive toast notifications for network alerts; inline red text for form validation errors.
