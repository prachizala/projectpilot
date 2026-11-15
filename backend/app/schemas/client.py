from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Primary contact name")
    company: Optional[str] = Field(None, max_length=255, description="Client company or organization")
    email: EmailStr = Field(..., description="Client email address")
    phone: Optional[str] = Field(None, max_length=50, description="Contact telephone number")
    notes: Optional[str] = Field(None, description="Internal notes regarding client engagement")

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class ClientOut(ClientBase):
    id: int
    owner_id: int
    created_at: datetime
    projects_count: int = 0
    total_billed: float = 0.0

    model_config = ConfigDict(from_attributes=True)
