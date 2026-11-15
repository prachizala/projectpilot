from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models.models import User, Client, Project, Task, Invoice, InvoiceItem, Proposal

def seed_demo_data(db: Session) -> dict:
    """Populates realistic, clearly-labeled demo data for product demonstration."""
    # 1. Clean existing demo data if present
    existing_owner = db.query(User).filter(User.email == "demo@projectpilot.local").first()
    if existing_owner:
        db.delete(existing_owner)
        db.commit()

    # 2. Agency Owner
    owner = User(
        email="demo@projectpilot.local",
        hashed_password=hash_password("demo123456"),
        full_name="Alex Mercer (Demo Agency)",
        role="owner",
        is_active=True
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    # 3. Agency Member
    member = User(
        email="member@projectpilot.local",
        hashed_password=hash_password("member123456"),
        full_name="Jordan Lee (Designer)",
        role="member",
        is_active=True
    )
    db.add(member)
    db.commit()

    # 4. Clients
    c1 = Client(
        owner_id=owner.id,
        name="Sarah Jenkins",
        company="Apex Media Lab",
        email="sarah@apexmedialab.demo",
        phone="+1 (555) 234-5678",
        notes="High-touch creative agency. Prefers net-15 payment terms."
    )
    c2 = Client(
        owner_id=owner.id,
        name="Marcus Vance",
        company="Nexus Digital LLC",
        email="marcus@nexusdigital.demo",
        phone="+1 (555) 876-5432",
        notes="Monthly recurring SEO and marketing retainer."
    )
    c3 = Client(
        owner_id=owner.id,
        name="Elena Rostova",
        company="CloudScale Networks",
        email="elena@cloudscale.demo",
        phone="+1 (555) 432-1098",
        notes="Enterprise cloud migration contract."
    )
    db.add_all([c1, c2, c3])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(c3)

    # 5. Client Portal User
    client_user = User(
        email="client@apex.demo",
        hashed_password=hash_password("client123456"),
        full_name="Sarah Jenkins (Client Portal)",
        role="client",
        client_id=c1.id,
        is_active=True
    )
    db.add(client_user)
    db.commit()

    # 6. Projects
    today = date.today()
    p1 = Project(
        owner_id=owner.id,
        client_id=c1.id,
        title="E-Commerce Re-platforming",
        description="Headless storefront migration with automated inventory sync.",
        status="in_progress",
        budget=18500.0,
        deadline=today + timedelta(days=25)
    )
    p2 = Project(
        owner_id=owner.id,
        client_id=c1.id,
        title="Brand Identity & Design System",
        description="Comprehensive vector typography, component library, and guidelines.",
        status="completed",
        budget=7500.0,
        deadline=today - timedelta(days=5)
    )
    p3 = Project(
        owner_id=owner.id,
        client_id=c2.id,
        title="Q3 Growth Marketing & SEO Sprint",
        description="Technical audit, core web vitals optimization, and backlink outreach.",
        status="in_progress",
        budget=6000.0,
        deadline=today + timedelta(days=40)
    )
    p4 = Project(
        owner_id=owner.id,
        client_id=c3.id,
        title="Cloud Infrastructure Migration",
        description="Containerized microservices orchestration on Kubernetes with automated CI/CD.",
        status="in_review",
        budget=25000.0,
        deadline=today + timedelta(days=15)
    )
    db.add_all([p1, p2, p3, p4])
    db.commit()
    db.refresh(p1)
    db.refresh(p2)
    db.refresh(p3)
    db.refresh(p4)

    # 7. Tasks for Project 1 (Kanban demo)
    tasks = [
        Task(project_id=p1.id, owner_id=owner.id, title="Configure Stripe Webhook Listeners", status="todo", position=0, priority="high", due_date=today + timedelta(days=5)),
        Task(project_id=p1.id, owner_id=owner.id, title="Implement Redis Cart Session Caching", status="todo", position=1, priority="medium", due_date=today + timedelta(days=7)),
        Task(project_id=p1.id, owner_id=owner.id, title="Integrate GraphQL Product Catalog Query", status="in_progress", position=0, priority="high", due_date=today + timedelta(days=2)),
        Task(project_id=p1.id, owner_id=owner.id, title="Build Responsive Checkout Modal", status="in_progress", position=1, priority="medium", due_date=today + timedelta(days=4)),
        Task(project_id=p1.id, owner_id=owner.id, title="Perform Lighthouse Performance Audit", status="review", position=0, priority="medium", due_date=today + timedelta(days=1)),
        Task(project_id=p1.id, owner_id=owner.id, title="Setup Staging Postgres Cluster", status="done", position=0, priority="low", due_date=today - timedelta(days=3)),
        Task(project_id=p1.id, owner_id=owner.id, title="Draft Architecture Design Document", status="done", position=1, priority="high", due_date=today - timedelta(days=10))
    ]
    db.add_all(tasks)
    db.commit()

    # 8. Invoices
    inv1 = Invoice(
        owner_id=owner.id,
        client_id=c1.id,
        project_id=p2.id,
        invoice_number="INV-2026-0001",
        issue_date=today - timedelta(days=14),
        due_date=today - timedelta(days=1),
        status="paid",
        subtotal=7500.0,
        tax_rate_pct=18.0,
        tax_amount=1350.0,
        total_amount=8850.0,
        notes="Brand Identity deliverables completed and transferred."
    )
    inv2 = Invoice(
        owner_id=owner.id,
        client_id=c1.id,
        project_id=p1.id,
        invoice_number="INV-2026-0002",
        issue_date=today - timedelta(days=3),
        due_date=today + timedelta(days=12),
        status="sent",
        subtotal=9250.0,
        tax_rate_pct=18.0,
        tax_amount=1665.0,
        total_amount=10915.0,
        notes="Milestone 1 Discovery & Core Frontend Scaffolding."
    )
    inv3 = Invoice(
        owner_id=owner.id,
        client_id=c2.id,
        project_id=p3.id,
        invoice_number="INV-2026-0003",
        issue_date=today,
        due_date=today + timedelta(days=15),
        status="draft",
        subtotal=3000.0,
        tax_rate_pct=18.0,
        tax_amount=540.0,
        total_amount=3540.0,
        notes="Monthly marketing sprint advance retainer."
    )
    db.add_all([inv1, inv2, inv3])
    db.commit()
    db.refresh(inv1)
    db.refresh(inv2)
    db.refresh(inv3)

    items = [
        InvoiceItem(invoice_id=inv1.id, description="Brand Identity Exploration & Discovery", quantity=1.0, unit_price=3500.0, total=3500.0),
        InvoiceItem(invoice_id=inv1.id, description="Design System Component Tokens & Guidelines", quantity=1.0, unit_price=4000.0, total=4000.0),
        InvoiceItem(invoice_id=inv2.id, description="E-Commerce Architecture & GraphQL Gateway", quantity=1.0, unit_price=5250.0, total=5250.0),
        InvoiceItem(invoice_id=inv2.id, description="Storefront UI Prototyping & Cart Flow", quantity=1.0, unit_price=4000.0, total=4000.0),
        InvoiceItem(invoice_id=inv3.id, description="SEO Content Audit & Technical Remediation", quantity=1.0, unit_price=3000.0, total=3000.0)
    ]
    db.add_all(items)
    db.commit()

    # 9. Proposals
    prop1 = Proposal(
        owner_id=owner.id,
        client_id=c3.id,
        title="Enterprise Kubernetes Migration Proposal",
        raw_requirements="Client migrating 14 legacy VM workloads to multi-region Kubernetes cluster with zero downtime.",
        scope_summary="Full migration, zero-downtime blue/green deployment strategy, Prometheus telemetry.",
        milestones_json='[{"title":"Phase 1: Architecture Audit","estimated_days":10,"budget":6250.0,"tasks":["Infrastructure audit","Helm chart specifications"]},{"title":"Phase 2: Cluster Provisioning & Pipeline","estimated_days":20,"budget":12500.0,"tasks":["Terraform staging setup","ArgoCD GitOps integration"]},{"title":"Phase 3: Traffic Cutover & Monitoring","estimated_days":10,"budget":6250.0,"tasks":["DNS blue-green switch","Prometheus alerting validation"]}]',
        estimated_budget=25000.0,
        status="sent"
    )
    db.add(prop1)
    db.commit()

    return {
        "status": "success",
        "owner_email": "demo@projectpilot.local",
        "owner_password": "demo123456",
        "client_portal_email": "client@apex.demo",
        "client_portal_password": "client123456"
    }

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        res = seed_demo_data(db)
        print("Demo data seeded successfully:", res)
    finally:
        db.close()
