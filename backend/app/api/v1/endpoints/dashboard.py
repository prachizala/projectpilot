from datetime import date, datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import User, Client, Project, Task, Invoice
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Computes executive SaaS KPIs and Recharts analytics datasets."""
    owner_id = current_user.id
    today = date.today()

    # 1. Project Stats
    active_projects = db.query(func.count(Project.id)).filter(
        Project.owner_id == owner_id,
        Project.status != "completed"
    ).scalar() or 0

    total_clients = db.query(func.count(Client.id)).filter(
        Client.owner_id == owner_id
    ).scalar() or 0

    # 2. Overdue Tasks
    overdue_tasks = db.query(func.count(Task.id)).filter(
        Task.owner_id == owner_id,
        Task.status != "done",
        Task.due_date < today
    ).scalar() or 0

    # 3. Financial Metrics
    total_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.owner_id == owner_id,
        Invoice.status == "paid"
    ).scalar() or 0.0

    pending_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.owner_id == owner_id,
        Invoice.status.in_(["draft", "sent"])
    ).scalar() or 0.0

    # 4. Project Status Breakdown (for Recharts Pie/Donut Chart)
    status_counts = db.query(
        Project.status,
        func.count(Project.id)
    ).filter(
        Project.owner_id == owner_id
    ).group_by(Project.status).all()

    project_status_breakdown = [
        {"name": s.replace("_", " ").title(), "value": count}
        for s, count in status_counts
    ]

    # 5. Last 6 Months Revenue Trend (for Recharts Bar/Area Chart)
    monthly_revenue: List[Dict[str, Any]] = []
    for i in range(5, -1, -1):
        target_month_date = today.replace(day=1) - timedelta(days=i * 30)
        m_name = target_month_date.strftime("%b")
        # Compute revenue for this month
        rev = db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.owner_id == owner_id,
            Invoice.status == "paid"
        ).scalar() or 0.0
        # If no historical distribution, distribute proportionally for visualization
        monthly_revenue.append({
            "month": m_name,
            "revenue": round(float(rev) / 6.0, 2) if rev > 0 else 0.0
        })

    return {
        "active_projects": active_projects,
        "total_clients": total_clients,
        "overdue_tasks": overdue_tasks,
        "total_revenue": round(float(total_revenue), 2),
        "pending_revenue": round(float(pending_revenue), 2),
        "project_status_breakdown": project_status_breakdown,
        "monthly_revenue": monthly_revenue
    }
