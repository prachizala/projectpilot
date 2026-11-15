from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class MilestoneItem(BaseModel):
    title: str
    description: str
    estimated_days: int = 14
    budget: float = 0.0
    tasks: List[str] = []

class ProposalGenerateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    raw_requirements: str = Field(..., min_length=10)
    client_id: Optional[int] = None
    target_budget: Optional[float] = Field(None, ge=0.0)

class ProposalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    raw_requirements: str
    scope_summary: str
    milestones_json: str = "[]"
    estimated_budget: float = 0.0
    client_id: Optional[int] = None

class ProposalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    scope_summary: Optional[str] = None
    milestones_json: Optional[str] = None
    estimated_budget: Optional[float] = Field(None, ge=0.0)
    status: Optional[str] = Field(None, pattern="^(draft|sent|approved|converted)$")

class ProposalOut(BaseModel):
    id: int
    owner_id: int
    client_id: Optional[int] = None
    title: str
    raw_requirements: str
    scope_summary: str
    milestones_json: str
    estimated_budget: float
    status: str
    created_at: datetime
    client_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
