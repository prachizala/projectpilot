from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User, Client, Project, Invoice, InvoiceItem
from app.schemas.invoice import InvoiceCreate, InvoiceStatusUpdate, InvoiceOut
from app.services.auth_service import get_current_user, require_role
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])

def build_invoice_response(inv: Invoice, db: Session) -> InvoiceOut:
    client = db.query(Client).filter(Client.id == inv.client_id).first()
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == inv.id).all()
    inv_dict = {
        "id": inv.id,
        "owner_id": inv.owner_id,
        "client_id": inv.client_id,
        "project_id": inv.project_id,
        "invoice_number": inv.invoice_number,
        "issue_date": inv.issue_date,
        "due_date": inv.due_date,
        "status": inv.status,
        "subtotal": inv.subtotal,
        "tax_rate_pct": inv.tax_rate_pct,
        "tax_amount": inv.tax_amount,
        "total_amount": inv.total_amount,
        "notes": inv.notes,
        "created_at": inv.created_at,
        "client_name": client.name if client else "Unknown Client",
        "items": items
    }
    return InvoiceOut.model_validate(inv_dict)

@router.get("", response_model=List[InvoiceOut])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists invoices with role-based visibility."""
    if current_user.role == "client":
        if not current_user.client_id:
            return []
        invoices = db.query(Invoice).filter(
            Invoice.client_id == current_user.client_id
        ).order_by(Invoice.created_at.desc()).all()
    else:
        invoices = db.query(Invoice).filter(
            Invoice.owner_id == current_user.id
        ).order_by(Invoice.created_at.desc()).all()

    return [build_invoice_response(inv, db) for inv in invoices]

@router.post("", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(
    inv_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Creates a new tax invoice with line items, calculating totals automatically."""
    client = db.query(Client).filter(
        Client.id == inv_in.client_id,
        Client.owner_id == current_user.id
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found or does not belong to your account."
        )

    # Calculate item totals and overall invoice financials
    raw_items = [item.model_dump() for item in inv_in.items]
    subtotal, tax_amount, total_amount = InvoiceService.calculate_totals(raw_items, inv_in.tax_rate_pct)
    inv_number = InvoiceService.generate_invoice_number(db, current_user.id)

    invoice = Invoice(
        owner_id=current_user.id,
        client_id=client.id,
        project_id=inv_in.project_id,
        invoice_number=inv_number,
        issue_date=inv_in.issue_date,
        due_date=inv_in.due_date,
        status="draft",
        subtotal=subtotal,
        tax_rate_pct=inv_in.tax_rate_pct,
        tax_amount=tax_amount,
        total_amount=total_amount,
        notes=inv_in.notes
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Insert line items
    for item in raw_items:
        line_total = round(float(item["quantity"]) * float(item["unit_price"]), 2)
        inv_item = InvoiceItem(
            invoice_id=invoice.id,
            description=item["description"].strip(),
            quantity=float(item["quantity"]),
            unit_price=float(item["unit_price"]),
            total=line_total
        )
        db.add(inv_item)

    db.commit()
    db.refresh(invoice)
    return build_invoice_response(invoice, db)

@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves invoice details."""
    query = db.query(Invoice).filter(Invoice.id == invoice_id)
    if current_user.role == "client":
        query = query.filter(Invoice.client_id == current_user.client_id)
    else:
        query = query.filter(Invoice.owner_id == current_user.id)

    inv = query.first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return build_invoice_response(inv, db)

@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Streams a dynamically generated vector PDF invoice rendered via PyMuPDF."""
    query = db.query(Invoice).filter(Invoice.id == invoice_id)
    if current_user.role == "client":
        query = query.filter(Invoice.client_id == current_user.client_id)
    else:
        query = query.filter(Invoice.owner_id == current_user.id)

    inv = query.first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    client = db.query(Client).filter(Client.id == inv.client_id).first()
    owner = db.query(User).filter(User.id == inv.owner_id).first()
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == inv.id).all()

    pdf_bytes = InvoiceService.render_invoice_pdf(inv, client, owner, items)

    headers = {
        "Content-Disposition": f'attachment; filename="Invoice-{inv.invoice_number}.pdf"',
        "Content-Type": "application/pdf"
    }
    return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")

@router.patch("/{invoice_id}/status", response_model=InvoiceOut)
def update_invoice_status(
    invoice_id: int,
    status_in: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Updates invoice payment and delivery status."""
    inv = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.owner_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    inv.status = status_in.status
    db.commit()
    db.refresh(inv)
    return build_invoice_response(inv, db)

@router.delete("/{invoice_id}", status_code=status.HTTP_200_OK)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("owner"))
):
    """Deletes an invoice and associated line items."""
    inv = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.owner_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    db.delete(inv)
    db.commit()
    return {"message": "Invoice deleted successfully.", "invoice_id": invoice_id}
