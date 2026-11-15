import datetime
import pytest

def get_auth_token(client, email):
    resp = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": "password123",
        "full_name": "Invoice Admin",
        "role": "owner"
    })
    return resp.json()["access_token"]

def test_invoice_crud_and_pdf_streaming(client):
    token = get_auth_token(client, "billing_admin@agency.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Setup Client
    r_client = client.post("/api/v1/clients", json={"name": "Globex", "email": "billing@globex.com"}, headers=headers)
    client_id = r_client.json()["id"]

    # 1. Create Invoice with 2 line items and 18% tax
    inv_payload = {
        "client_id": client_id,
        "issue_date": str(datetime.date.today()),
        "due_date": str(datetime.date.today() + datetime.timedelta(days=15)),
        "tax_rate_pct": 18.0,
        "notes": "Payment via bank wire",
        "items": [
            {"description": "Backend API Development", "quantity": 10.0, "unit_price": 100.0},
            {"description": "React Dashboard UI", "quantity": 5.0, "unit_price": 80.0}
        ]
    }
    r_create = client.post("/api/v1/invoices", json=inv_payload, headers=headers)
    assert r_create.status_code == 201
    data = r_create.json()
    invoice_id = data["id"]

    # Verify math: (10 * 100) + (5 * 80) = 1000 + 400 = 1400 subtotal
    # 18% of 1400 = 252 tax
    # Total = 1652
    assert data["subtotal"] == 1400.0
    assert data["tax_amount"] == 252.0
    assert data["total_amount"] == 1652.0
    assert data["status"] == "draft"
    assert len(data["items"]) == 2

    # 2. Update status to 'paid'
    r_status = client.patch(f"/api/v1/invoices/{invoice_id}/status", json={"status": "paid"}, headers=headers)
    assert r_status.status_code == 200
    assert r_status.json()["status"] == "paid"

    # 3. Stream Vector PDF
    r_pdf = client.get(f"/api/v1/invoices/{invoice_id}/pdf", headers=headers)
    assert r_pdf.status_code == 200
    assert r_pdf.headers["Content-Type"] == "application/pdf"
    assert "attachment; filename=" in r_pdf.headers["Content-Disposition"]
    assert len(r_pdf.content) > 500  # Non-empty valid PDF bytes

    # 4. List Invoices
    r_list = client.get("/api/v1/invoices", headers=headers)
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 1
