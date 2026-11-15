from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.seed import seed_demo_data

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check():
    """Health check probe returning system status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.post("/seed", tags=["System"])
def seed_database(db: Session = Depends(get_db)):
    """Seeds or resets realistic demonstration data for reviewers and demo exploration."""
    return seed_demo_data(db)
