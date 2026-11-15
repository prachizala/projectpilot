from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.models.models import User, Client, Project, Invoice
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/clients", tags=["Clients"])

def build_client_response(client: Client, db: Session) -> ClientOut:
    """Computes real-time project counts and total billed amounts for a client."""
    projects_count = db.query(func.count(Project.id)).filter(Project.client_id == client.id).scalar() or 0
    total_billed = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.client_id == client.id,
        Invoice.status == "paid"
    ).scalar() or 0.0

    client_dict = {
        "id": client.id,
        "owner_id": client.owner_id,
        "name": client.name,
        "company": client.company,
        "email": client.email,
        "phone": client.phone,
        "notes": client.notes,
        "created_at": client.created_at,
        "projects_count": projects_count,
        "total_billed": round(float(total_billed), 2)
    }
    return ClientOut.model_validate(client_dict)

@router.get("", response_model=List[ClientOut])
def list_clients(
    q: Optional[str] = Query(None, description="Search by name, company, or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all clients owned by the authenticated agency user."""
    # Enforce tenant isolation
    query = db.query(Client).filter(Client.owner_id == current_user.id)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Client.name.ilike(search_pattern),
                Client.company.ilike(search_pattern),
                Client.email.ilike(search_pattern)
            )
        )

    clients = query.order_by(Client.created_at.desc()).all()
    return [build_client_response(c, db) for c in clients]

@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Registers a new client profile under the current agency owner."""
    existing = db.query(Client).filter(
        Client.owner_id == current_user.id,
        Client.email == client_in.email.lower()
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A client with this email address already exists for your account."
        )

    client = Client(
        owner_id=current_user.id,
        name=client_in.name.strip(),
        company=client_in.company.strip() if client_in.company else None,
        email=client_in.email.lower(),
        phone=client_in.phone.strip() if client_in.phone else None,
        notes=client_in.notes
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return build_client_response(client, db)

@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves client details with aggregated financial and project metrics."""
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found."
        )
    return build_client_response(client, db)

@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Updates client profile fields."""
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found."
        )

    # Check email uniqueness if changing email
    if client_in.email and client_in.email.lower() != client.email:
        conflict = db.query(Client).filter(
            Client.owner_id == current_user.id,
            Client.email == client_in.email.lower()
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another client with this email already exists."
            )
        client.email = client_in.email.lower()

    if client_in.name is not None:
        client.name = client_in.name.strip()
    if client_in.company is not None:
        client.company = client_in.company.strip() if client_in.company else None
    if client_in.phone is not None:
        client.phone = client_in.phone.strip() if client_in.phone else None
    if client_in.notes is not None:
        client.notes = client_in.notes

    db.commit()
    db.refresh(client)
    return build_client_response(client, db)

@router.delete("/{client_id}", status_code=status.HTTP_200_OK)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Deletes a client profile and cascades deletion to associated records."""
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found."
        )

    db.delete(client)
    db.commit()
    return {"message": "Client deleted successfully.", "client_id": client_id}
