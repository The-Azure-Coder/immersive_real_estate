from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid
from typing import List
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.models.user import User, Session as UserSession, Account
from app.schemas.user import UserCreate, UserOut, UserSessionResponse, Token, UserLogin
from app.api.v1.endpoints.deps import get_current_user, require_role

router = APIRouter()

@router.post("/register", response_model=UserSessionResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = uuid.uuid4().hex
    hashed_password = get_password_hash(user.password)
    
    # 1. Create User
    new_user = User(
        id=user_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        image=user.image,
    )
    db.add(new_user)
    
    # 2. Create Account
    new_account = Account(
        id=uuid.uuid4().hex,
        user_id=user_id,
        account_id=user.email,
        provider_id="credential",
        password=hashed_password
    )
    db.add(new_account)
    
    # 3. Create initial session
    session_id = uuid.uuid4().hex
    session_token = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    new_session = UserSession(
        id=session_id,
        token=session_token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(new_session)
    
    db.commit()
    db.refresh(new_user)
    db.refresh(new_session)
    
    return {
        "user": new_user,
        "session": new_session
    }

@router.post("/login", response_model=UserSessionResponse)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    account = db.query(Account).filter(Account.user_id == user.id, Account.provider_id == "credential").first()
    if not account or not verify_password(form_data.password, account.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    session_id = uuid.uuid4().hex
    session_token = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    new_session = UserSession(
        id=session_id,
        token=session_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    response.set_cookie(
        key="better-auth.session_token",
        value=session_token,
        expires=expires_at,
        httponly=True,
        samesite="lax",
        secure=False
    )
    
    return {
        "user": user,
        "session": new_session
    }

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Authenticated route to get current user details"""
    return current_user

@router.get("/users", response_model=List[UserOut])
async def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Admin-only route to list all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Authenticated route to logout"""
    response.delete_cookie("better-auth.session_token")
    # Optional: Delete session from DB
    return {"message": "Successfully logged out"}
