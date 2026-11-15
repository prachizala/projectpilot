# Day 4 Notes — Tasks Engine, Sequential Integer Indexing & Drag-and-Drop Kanban

**Date:** Day 4  
**Author:** Engineering Team  

---

## 1. What Was Built Today

1. **Tasks REST API (`/api/v1/projects/{id}/tasks` & `/api/v1/tasks/{id}`):**
   - Implemented task creation, listing, updating, deletion, and rank position updates.
   - Strictly enforced project tenancy: agency members can only view or manage tasks within projects owned by their organization.
2. **Column Rebalancing Algorithm (`app/services/kanban_service.py`):**
   - Built a deterministic integer position indexer that automatically shifts existing cards when a card is moved within a column or across columns.
   - When a task is deleted or moved, subsequent tasks shift up (`position -= 1`) to ensure contiguous zero-indexed sequences (`0, 1, 2, ...`).
3. **Interactive React Kanban Board (`src/pages/KanbanPage.tsx`):**
   - 4-column layout: **To Do**, **In Progress**, **In Review**, and **Done**.
   - Built using HTML5 native Drag and Drop (`draggable`, `onDragStart`, `onDragOver`, `onDrop`), eliminating heavy third-party bundle weight.
   - Implemented optimistic UI updates: dropped cards update their column immediately on the client, with automatic state rollback if the backend request fails.
   - Modal for creating tasks with priority tags (`High`, `Medium`, `Low`) and due date pickers.
4. **Automated Testing Suite:**
   - Authored `tests/test_tasks.py` verifying same-column reordering, cross-column moves, position boundary checks, and post-delete gap closure.
   - Total automated backend tests raised to **12/12 passing** (100% pass rate).

---

## 2. How the Core Day 4 Flow Works (Kanban Position Balancing)

```
User drags Task A from "To Do" (Position 1) to "In Progress" (Position 0)
   │
   ▼
Frontend Optimistic Update:
   - Moves Task A to "In Progress" in local state
   - Calls PATCH /api/v1/tasks/{id}/position { status: "in_progress", position: 0 }
   │
   ▼
Backend Execution (`KanbanService.reorder_task`):
   │
   ├── Step 1: Close the gap in "To Do"
   │     UPDATE tasks SET position = position - 1
   │     WHERE project_id = X AND status = 'todo' AND position > 1;
   │
   ├── Step 2: Open space in "In Progress"
   │     UPDATE tasks SET position = position + 1
   │     WHERE project_id = X AND status = 'in_progress' AND position >= 0;
   │
   ├── Step 3: Insert Task A at target position
   │     UPDATE tasks SET status = 'in_progress', position = 0
   │     WHERE id = task_id;
   │
   └── Step 4: Commit transaction & return updated TaskOut
```

---

## 3. Five Technical Interview Questions & Answers (Day 4 Code)

### Q1: Why did you use contiguous integer indexing (`0, 1, 2...`) instead of floating-point positioning (e.g. Lexorank) for task ordering?
> **Answer:**  
> "Floating-point ordering (like Jira's Lexorank) allows $O(1)$ single-row updates by inserting between fractions (e.g., between 1.0 and 2.0 comes 1.5). However, floating-point precision degrades over repeated moves within small boundaries, eventually necessitating periodic column-wide rebalancing scripts. For small-to-medium project teams (where a column rarely holds more than 50 active tasks), deterministic integer shifting inside a database transaction is straightforward, beginner-readable, and immune to floating-point precision bugs."

### Q2: How does the frontend handle drag-and-drop network failures gracefully?
> **Answer:**  
> "In `src/pages/KanbanPage.tsx`, before dispatching `api.updateTaskPosition()`, we preserve a snapshot of the current state: `const previousTasks = [...tasks]`. We apply the state transformation optimistically so the UI feels instant. If the network call throws an error, the `catch` block restores `previousTasks` and alerts the user, preventing client-server state divergence."

### Q3: How do you prevent tasks from being orphaned if a project is deleted?
> **Answer:**  
> "In `app/models/models.py`, `Task.project_id` defines `ForeignKey('projects.id', ondelete='CASCADE')`, and the `Project.tasks` relationship is configured with `cascade='all, delete-orphan'`. When a project is deleted, the database automatically cascades deletion to all associated tasks."

### Q4: Why did you use the native HTML5 Drag and Drop API instead of a library like `@hello-pangea/dnd`?
> **Answer:**  
> "Third-party drag-and-drop packages often add 60–100KB to the JavaScript bundle and introduce complex ref-forwarding mechanics. The HTML5 Drag and Drop API (`draggable`, `onDragStart`, `onDragOver`, `onDrop`) delivers smooth native interactions with zero bundle weight and full browser support."

### Q5: How is column position index validated at the API boundary?
> **Answer:**  
> "In `app/schemas/task.py`, `TaskPositionUpdate` enforces `position: int = Field(..., ge=0)` and validates `status` against the regex pattern `^(todo|in_progress|review|done)$`. Furthermore, `KanbanService.reorder_task` clamps incoming position requests:
> ```python
> new_position = max(0, min(new_position, len(target_tasks)))
> ```
> This prevents out-of-bounds positioning if an invalid index is sent."

---

## 4. One Small Change You Should Try Yourself

**Exercise: Add a task completion badge on the card.**  
Open `frontend/src/pages/KanbanPage.tsx`. In the card rendering loop, notice how priority badges are displayed.
Try checking if `task.status === 'done'` and displaying a green checkmark beside the title:
```tsx
{task.status === 'done' && (
  <span className="text-[10px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
    ✓ Done
  </span>
)}
```
Run `npm run build` inside `frontend/` to confirm that the change compiles cleanly!
