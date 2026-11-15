from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="owner", nullable=False)  # owner, member, client
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL", use_alter=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    clients = relationship("Client", back_populates="owner", foreign_keys="Client.owner_id")
    projects = relationship("Project", back_populates="owner")
    invoices = relationship("Invoice", back_populates="owner")
    proposals = relationship("Proposal", back_populates="owner")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="clients", foreign_keys=[owner_id])
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="client", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="client")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="planning", nullable=False)  # planning, in_progress, in_review, completed, on_hold
    budget = Column(Float, default=0.0, nullable=False)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects")
    client = relationship("Client", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="todo", nullable=False, index=True)  # todo, in_progress, review, done
    position = Column(Integer, default=0, nullable=False)
    priority = Column(String(50), default="medium", nullable=False)  # low, medium, high
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    invoice_number = Column(String(100), unique=True, index=True, nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, sent, paid, overdue
    subtotal = Column(Float, default=0.0, nullable=False)
    tax_rate_pct = Column(Float, default=18.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Float, default=1.0, nullable=False)
    unit_price = Column(Float, default=0.0, nullable=False)
    total = Column(Float, default=0.0, nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    raw_requirements = Column(Text, nullable=False)
    scope_summary = Column(Text, nullable=False)
    milestones_json = Column(Text, default="[]", nullable=False)  # JSON serialized list of milestones
    estimated_budget = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, sent, approved, converted
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="proposals")
    client = relationship("Client", back_populates="proposals")
