from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User, Client, Proposal, Project
from app.schemas.proposal import (
    ProposalGenerateRequest, ProposalCreate, ProposalUpdate, ProposalOut
)
from app.schemas.project import ProjectOut
from app.api.v1.endpoints.projects import build_project_response
from app.services.auth_service import get_current_user, require_role
from app.services.proposal_service import ProposalService

router = APIRouter(prefix="/proposals", tags=["Proposals"])

def build_proposal_response(prop: Proposal, db: Session) -> ProposalOut:
    client = db.query(Client).filter(Client.id == prop.client_id).first() if prop.client_id else None
    prop_dict = {
        "id": prop.id,
        "owner_id": prop.owner_id,
        "client_id": prop.client_id,
        "title": prop.title,
        "raw_requirements": prop.raw_requirements,
        "scope_summary": prop.scope_summary,
        "milestones_json": prop.milestones_json,
        "estimated_budget": prop.estimated_budget,
        "status": prop.status,
        "created_at": prop.created_at,
        "client_name": client.name if client else None
    }
    return ProposalOut.model_validate(prop_dict)

@router.get("", response_model=List[ProposalOut])
def list_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "member"))
):
    """Retrieves all proposals owned by the agency."""
    proposals = db.query(Proposal).filter(
        Proposal.owner_id == current_user.id
    ).order_by(Proposal.created_at.desc()).all()
    return [build_proposal_response(p, db) for p in proposals]

@router.post("/generate", response_model=ProposalOut, status_code=status.HTTP_201_CREATED)
def generate_proposal(
    req: ProposalGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """
    AI Service: Scaffolds a complete project proposal from raw client text.
    Extracts deliverables, milestones, budgets, and actionable tasks.
    """
    structured = ProposalService.generate_proposal_structure(
        title=req.title,
        raw_text=req.raw_requirements,
        target_budget=req.target_budget
    )

    proposal = Proposal(
        owner_id=current_user.id,
        client_id=req.client_id,
        title=req.title.strip(),
        raw_requirements=req.raw_requirements.strip(),
        scope_summary=structured["scope_summary"],
        milestones_json=structured["milestones_json"],
        estimated_budget=structured["estimated_budget"],
        status="draft"
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return build_proposal_response(proposal, db)

@router.get("/{proposal_id}", response_model=ProposalOut)
def get_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner", "member"))
):
    """Retrieves proposal details."""
    prop = db.query(Proposal).filter(
        Proposal.id == proposal_id,
        Proposal.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return build_proposal_response(prop, db)

@router.post("/{proposal_id}/convert", response_model=ProjectOut)
def convert_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """
    Converts an approved proposal into an active Project with pre-populated Tasks.
    """
    prop = db.query(Proposal).filter(
        Proposal.id == proposal_id,
        Proposal.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found.")

    project = ProposalService.convert_to_project(db, prop, current_user)
    return build_project_response(project, db)

@router.delete("/{proposal_id}", status_code=status.HTTP_200_OK)
def delete_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Deletes a proposal draft."""
    prop = db.query(Proposal).filter(
        Proposal.id == proposal_id,
        Proposal.owner_id == current_user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found.")

    db.delete(prop)
    db.commit()
    return {"message": "Proposal deleted successfully.", "proposal_id": proposal_id}
