from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

VALID_PROJECT_STATUSES = "planning|in_progress|in_review|completed|on_hold"

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: Optional[str] = Field(None, description="Detailed project scope description")
    status: str = Field("planning", pattern=f"^({VALID_PROJECT_STATUSES})$")
    budget: float = Field(0.0, ge=0.0, description="Allocated budget amount")
    deadline: Optional[date] = Field(None, description="Target delivery completion date")
    client_id: int = Field(..., description="Foreign key of the associated client")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=f"^({VALID_PROJECT_STATUSES})$")
    budget: Optional[float] = Field(None, ge=0.0)
    deadline: Optional[date] = None
    client_id: Optional[int] = None

class ProjectOut(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    client_name: Optional[str] = None
    tasks_count: int = 0

    model_config = ConfigDict(from_attributes=True)
