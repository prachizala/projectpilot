from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

VALID_TASK_STATUSES = "todo|in_progress|review|done"
VALID_TASK_PRIORITIES = "low|medium|high"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field("todo", pattern=f"^({VALID_TASK_STATUSES})$")
    priority: str = Field("medium", pattern=f"^({VALID_TASK_PRIORITIES})$")
    due_date: Optional[date] = None

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field("todo", pattern=f"^({VALID_TASK_STATUSES})$")
    priority: Optional[str] = Field("medium", pattern=f"^({VALID_TASK_PRIORITIES})$")
    due_date: Optional[date] = None

class TaskPositionUpdate(BaseModel):
    status: str = Field(..., pattern=f"^({VALID_TASK_STATUSES})$")
    position: int = Field(..., ge=0)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=f"^({VALID_TASK_STATUSES})$")
    priority: Optional[str] = Field(None, pattern=f"^({VALID_TASK_PRIORITIES})$")
    due_date: Optional[date] = None

class TaskOut(TaskBase):
    id: int
    project_id: int
    owner_id: int
    position: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
