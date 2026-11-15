from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.schemas.auth import (
    UserCreate, UserLogin, TokenResponse, TokenRefreshRequest, UserOut
)
from app.services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user account and returns an authenticated JWT token pair."""
    user = AuthService.register_user(db, user_in)
    return AuthService.create_tokens_for_user(user)

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticates credentials and returns access and refresh JWT tokens."""
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    return AuthService.create_tokens_for_user(user)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Exchanges a valid refresh token for a newly signed access token."""
    return AuthService.refresh_access_token(db, payload.refresh_token)

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated profile of the current user."""
    return current_user
