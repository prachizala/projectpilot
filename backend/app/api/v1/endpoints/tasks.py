from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User, Project, Task
from app.schemas.task import TaskCreate, TaskPositionUpdate, TaskUpdate, TaskOut
from app.services.auth_service import get_current_user, require_role
from app.services.kanban_service import KanbanService

router = APIRouter(tags=["Tasks"])

def verify_project_access(project_id: int, user: User, db: Session) -> Project:
    query = db.query(Project).filter(Project.id == project_id)
    if user.role == "client":
        query = query.filter(Project.client_id == user.client_id)
    else:
        query = query.filter(Project.owner_id == user.id)
    project = query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or inaccessible."
        )
    return project

@router.get("/projects/{project_id}/tasks", response_model=List[TaskOut])
def list_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all tasks for a project ordered by column and position index."""
    verify_project_access(project_id, current_user, db)
    tasks = db.query(Task).filter(
        Task.project_id == project_id
    ).order_by(Task.status.asc(), Task.position.asc()).all()
    return tasks

@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "member"))
):
    """Creates a new task in a project column with automatic rank positioning."""
    project = verify_project_access(project_id, current_user, db)
    task = KanbanService.append_task(
        db=db,
        project_id=project.id,
        owner_id=project.owner_id,
        data=task_in.model_dump()
    )
    return task

@router.patch("/tasks/{task_id}/position", response_model=TaskOut)
def update_task_position(
    task_id: int,
    pos_in: TaskPositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "member"))
):
    """Updates a task's Kanban column and position, automatically shifting adjacent cards."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

    updated = KanbanService.reorder_task(
        db=db,
        task=task,
        new_status=pos_in.status,
        new_position=pos_in.position
    )
    return updated

@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task_details(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "member"))
):
    """Updates task metadata (title, description, priority, due date)."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

    if task_in.title is not None:
        task.title = task_in.title.strip()
    if task_in.description is not None:
        task.description = task_in.description.strip() if task_in.description else None
    if task_in.priority is not None:
        task.priority = task_in.priority
    if task_in.due_date is not None:
        task.due_date = task_in.due_date

    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "member"))
):
    """Deletes a task and closes the position gap in its column."""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

    # Rebalance positions of tasks below the deleted task
    db.query(Task).filter(
        Task.project_id == task.project_id,
        Task.status == task.status,
        Task.position > task.position
    ).update({Task.position: Task.position - 1}, synchronize_session="fetch")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully.", "task_id": task_id}
