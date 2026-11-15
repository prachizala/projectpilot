from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import User, Client, Project, Task
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/projects", tags=["Projects"])

def build_project_response(project: Project, db: Session) -> ProjectOut:
    """Enriches project entity with client name and task count."""
    client = db.query(Client).filter(Client.id == project.client_id).first()
    tasks_count = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0

    project_dict = {
        "id": project.id,
        "owner_id": project.owner_id,
        "client_id": project.client_id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "budget": project.budget,
        "deadline": project.deadline,
        "created_at": project.created_at,
        "client_name": client.name if client else "Unknown Client",
        "tasks_count": tasks_count
    }
    return ProjectOut.model_validate(project_dict)

@router.get("", response_model=List[ProjectOut])
def list_projects(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves accessible projects based on role:
    - Agency Owners and Members see all projects under the owner tenant.
    - Client users see only projects tied to their client_id.
    """
    if current_user.role == "client":
        if not current_user.client_id:
            return []
        query = db.query(Project).filter(Project.client_id == current_user.client_id)
    else:
        query = db.query(Project).filter(Project.owner_id == current_user.id)

    if status_filter:
        query = query.filter(Project.status == status_filter.lower())
    if client_id and current_user.role != "client":
        query = query.filter(Project.client_id == client_id)

    projects = query.order_by(Project.created_at.desc()).all()
    return [build_project_response(p, db) for p in projects]

@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Creates a new project linked to a verified client owned by the current user."""
    client = db.query(Client).filter(
        Client.id == project_in.client_id,
        Client.owner_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified client does not exist or does not belong to your account."
        )

    project = Project(
        owner_id=current_user.id,
        client_id=project_in.client_id,
        title=project_in.title.strip(),
        description=project_in.description.strip() if project_in.description else None,
        status=project_in.status,
        budget=float(project_in.budget),
        deadline=project_in.deadline
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return build_project_response(project, db)

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves project details with role-based access validation."""
    query = db.query(Project).filter(Project.id == project_id)
    if current_user.role == "client":
        query = query.filter(Project.client_id == current_user.client_id)
    else:
        query = query.filter(Project.owner_id == current_user.id)

    project = query.first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    return build_project_response(project, db)

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "member"))
):
    """Updates project scope, status, or deadlines."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    if project_in.client_id is not None and project_in.client_id != project.client_id:
        client = db.query(Client).filter(
            Client.id == project_in.client_id,
            Client.owner_id == current_user.id
        ).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target client not found."
            )
        project.client_id = project_in.client_id

    if project_in.title is not None:
        project.title = project_in.title.strip()
    if project_in.description is not None:
        project.description = project_in.description.strip() if project_in.description else None
    if project_in.status is not None:
        project.status = project_in.status
    if project_in.budget is not None:
        project.budget = float(project_in.budget)
    if project_in.deadline is not None:
        project.deadline = project_in.deadline

    db.commit()
    db.refresh(project)
    return build_project_response(project, db)

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Deletes a project and cascades deletion to tasks and associated records."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully.", "project_id": project_id}
