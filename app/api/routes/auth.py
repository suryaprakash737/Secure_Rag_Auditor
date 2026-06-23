from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter()


@router.post("/register")
def register_user(
    request: RegisterRequest,
    session: Session = Depends(get_session),
):
    existing_user = session.exec(
        select(User).where(User.username == request.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(
        username=request.username,
        hashed_password=get_password_hash(request.password),
        role="analyst",
        clearance_level=1,
        is_active=True,
    )
    session.add(user)
    session.commit()

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login_user(
    request: LoginRequest,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == request.username)).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
    }
