import datetime
from app.models.models import User, Client, Project, Task, Invoice, InvoiceItem, Proposal

def test_entity_relationships(db_session):
    # 1. Create Owner User
    owner = User(
        email="founder@agency.com",
        hashed_password="hashed_pw_test",
        full_name="Agency Founder",
        role="owner"
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    assert owner.id is not None

    # 2. Create Client
    client = Client(
        owner_id=owner.id,
        name="Acme Corp",
        company="Acme Global Inc.",
        email="billing@acme.com",
        phone="+1234567890",
        notes="High-priority enterprise client"
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    assert client.id is not None

    # 3. Create Project linked to Client
    project = Project(
        owner_id=owner.id,
        client_id=client.id,
        title="Web Platform Overhaul",
        description="Redesigning client web portal",
        status="in_progress",
        budget=12500.0,
        deadline=datetime.date.today() + datetime.timedelta(days=30)
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    assert project.id is not None
    assert project.client.name == "Acme Corp"

    # 4. Create Task linked to Project
    task = Task(
        project_id=project.id,
        owner_id=owner.id,
        title="Setup Auth Schemas",
        status="todo",
        position=0,
        priority="high"
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    assert task.id is not None
    assert len(project.tasks) == 1

    # 5. Create Invoice & InvoiceItems
    invoice = Invoice(
        owner_id=owner.id,
        client_id=client.id,
        project_id=project.id,
        invoice_number="INV-2026-001",
        issue_date=datetime.date.today(),
        due_date=datetime.date.today() + datetime.timedelta(days=15),
        status="draft",
        subtotal=1000.0,
        tax_rate_pct=18.0,
        tax_amount=180.0,
        total_amount=1180.0
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)

    item = InvoiceItem(
        invoice_id=invoice.id,
        description="Milestone 1 Discovery",
        quantity=1.0,
        unit_price=1000.0,
        total=1000.0
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(invoice)
    assert len(invoice.items) == 1
    assert invoice.items[0].total == 1000.0

    # 6. Create Proposal
    proposal = Proposal(
        owner_id=owner.id,
        client_id=client.id,
        title="SEO Strategy Proposal",
        raw_requirements="Client needs monthly SEO optimization and technical audit",
        scope_summary="Technical audit, keyword analysis, backlinks",
        estimated_budget=2500.0,
        status="draft"
    )
    db_session.add(proposal)
    db_session.commit()
    db_session.refresh(proposal)
    assert proposal.id is not None
