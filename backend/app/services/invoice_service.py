from typing import List, Dict, Any, Tuple
from datetime import datetime
import io
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Invoice, InvoiceItem, Client, User

class InvoiceService:
    @staticmethod
    def calculate_totals(
        items: List[Dict[str, Any]],
        tax_rate_pct: float = 18.0
    ) -> Tuple[float, float, float]:
        """Calculates subtotal, tax amount, and total amount with 2 decimal precision."""
        subtotal = sum(float(item["quantity"]) * float(item["unit_price"]) for item in items)
        subtotal = round(subtotal, 2)
        tax_amount = round(subtotal * (float(tax_rate_pct) / 100.0), 2)
        total_amount = round(subtotal + tax_amount, 2)
        return subtotal, tax_amount, total_amount

    @staticmethod
    def generate_invoice_number(db: Session, owner_id: int) -> str:
        """Generates a sequential human-readable invoice code (e.g. INV-2026-0001)."""
        year = datetime.now().year
        count = db.query(func.count(Invoice.id)).filter(
            Invoice.owner_id == owner_id,
            Invoice.invoice_number.like(f"INV-{year}-%")
        ).scalar() or 0
        return f"INV-{year}-{(count + 1):04d}"

    @staticmethod
    def render_invoice_pdf(
        invoice: Invoice,
        client: Client,
        owner: User,
        items: List[InvoiceItem]
    ) -> bytes:
        """Renders an A4 print-ready vector PDF invoice in memory using PyMuPDF."""
        doc = fitz.open()
        try:
            page = doc.new_page(width=595, height=842) # A4 points

            # Header Top Banner
            page.draw_rect(fitz.Rect(40, 40, 555, 115), color=None, fill=(0.06, 0.09, 0.16))
            page.insert_text((60, 75), "PROJECTPILOT INVOICE", fontname="helv", fontsize=18, color=(1, 1, 1))
            page.insert_text((60, 95), f"Issued by: {owner.full_name}", fontname="helv", fontsize=10, color=(0.7, 0.75, 0.8))
            page.insert_text((400, 80), f"#{invoice.invoice_number}", fontname="helv", fontsize=14, color=(0.3, 0.7, 1.0))
            page.insert_text((400, 98), f"STATUS: {invoice.status.upper()}", fontname="helv", fontsize=10, color=(0.2, 0.8, 0.4) if invoice.status == 'paid' else (1.0, 0.8, 0.2))

            # Metadata Columns
            # Left: Client Billed To
            page.insert_text((40, 145), "BILLED TO:", fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))
            page.insert_text((40, 160), client.name, fontname="helv", fontsize=12, color=(0.1, 0.1, 0.1))
            if client.company:
                page.insert_text((40, 175), client.company, fontname="helv", fontsize=10, color=(0.3, 0.3, 0.3))
            page.insert_text((40, 190), client.email, fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))

            # Right: Dates & Terms
            page.insert_text((380, 145), "INVOICE DETAILS:", fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))
            page.insert_text((380, 160), f"Issue Date: {invoice.issue_date}", fontname="helv", fontsize=9, color=(0.2, 0.2, 0.2))
            page.insert_text((380, 175), f"Due Date:   {invoice.due_date}", fontname="helv", fontsize=9, color=(0.2, 0.2, 0.2))

            # Items Table Header
            y_table = 220
            page.draw_rect(fitz.Rect(40, y_table, 555, y_table + 25), color=None, fill=(0.94, 0.95, 0.98))
            page.insert_text((50, y_table + 16), "Description", fontname="helv", fontsize=9, color=(0.2, 0.2, 0.2))
            page.insert_text((330, y_table + 16), "Qty", fontname="helv", fontsize=9, color=(0.2, 0.2, 0.2))
            page.insert_text((390, y_table + 16), "Unit Price ($)", fontname="helv", fontsize=9, color=(0.2, 0.2, 0.2))
            page.insert_text((485, y_table + 16), "Total ($)", fontname="helv", fontsize=9, color=(0.2, 0.2, 0.2))

            # Line Items
            cur_y = y_table + 42
            for item in items:
                page.insert_text((50, cur_y), item.description, fontname="helv", fontsize=9, color=(0.1, 0.1, 0.1))
                page.insert_text((335, cur_y), f"{item.quantity:.1f}", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.3))
                page.insert_text((395, cur_y), f"{item.unit_price:.2f}", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.3))
                page.insert_text((490, cur_y), f"{item.total:.2f}", fontname="helv", fontsize=9, color=(0.1, 0.1, 0.1))
                page.draw_line(fitz.Point(40, cur_y + 8), fitz.Point(555, cur_y + 8), color=(0.9, 0.9, 0.9), width=0.5)
                cur_y += 24

            # Totals Section (Right-aligned)
            cur_y += 15
            page.draw_rect(fitz.Rect(340, cur_y, 555, cur_y + 80), color=(0.85, 0.85, 0.85), fill=(0.98, 0.99, 1.0))
            page.insert_text((355, cur_y + 20), "Subtotal:", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.3))
            page.insert_text((480, cur_y + 20), f"${invoice.subtotal:.2f}", fontname="helv", fontsize=9, color=(0.1, 0.1, 0.1))

            page.insert_text((355, cur_y + 40), f"Tax ({invoice.tax_rate_pct:.0f}%):", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.3))
            page.insert_text((480, cur_y + 40), f"${invoice.tax_amount:.2f}", fontname="helv", fontsize=9, color=(0.1, 0.1, 0.1))

            page.insert_text((355, cur_y + 65), "TOTAL DUE:", fontname="helv", fontsize=11, color=(0.0, 0.4, 0.8))
            page.insert_text((480, cur_y + 65), f"${invoice.total_amount:.2f}", fontname="helv", fontsize=11, color=(0.0, 0.4, 0.8))

            # Footer
            page.draw_line(fitz.Point(40, 780), fitz.Point(555, 780), color=(0.8, 0.8, 0.8), width=0.5)
            page.insert_text((40, 800), "Thank you for your business. Payment is due within standard invoice terms.", fontname="helv", fontsize=8, color=(0.5, 0.5, 0.5))
            page.insert_text((420, 800), "Generated via ProjectPilot SaaS", fontname="helv", fontsize=8, color=(0.6, 0.6, 0.6))

            pdf_bytes = doc.tobytes()
            return pdf_bytes
        finally:
            doc.close()
