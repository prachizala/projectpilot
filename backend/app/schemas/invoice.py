from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

VALID_INVOICE_STATUSES = "draft|sent|paid|overdue"

class InvoiceItemBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(1.0, gt=0.0)
    unit_price: float = Field(0.0, ge=0.0)

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemOut(InvoiceItemBase):
    id: int
    invoice_id: int
    total: float

    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(BaseModel):
    client_id: int
    project_id: Optional[int] = None
    issue_date: date
    due_date: date
    tax_rate_pct: float = Field(18.0, ge=0.0, le=100.0)
    notes: Optional[str] = None
    items: List[InvoiceItemCreate] = Field(..., min_length=1)

class InvoiceStatusUpdate(BaseModel):
    status: str = Field(..., pattern=f"^({VALID_INVOICE_STATUSES})$")

class InvoiceOut(BaseModel):
    id: int
    owner_id: int
    client_id: int
    project_id: Optional[int] = None
    invoice_number: str
    issue_date: date
    due_date: date
    status: str
    subtotal: float
    tax_rate_pct: float
    tax_amount: float
    total_amount: float
    notes: Optional[str] = None
    created_at: datetime
    client_name: Optional[str] = None
    items: List[InvoiceItemOut] = []

    model_config = ConfigDict(from_attributes=True)
