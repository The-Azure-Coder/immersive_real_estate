from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid
from typing import List
from jose import JWTError

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User, Session as UserSession, Account
from app.schemas.user import UserCreate, UserOut, Token, TokenRefreshRequest, UserLogin, SessionOut
from app.api.v1.endpoints.deps import get_current_user, require_role
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationMetadata
from app.core.config import settings

router = APIRouter()

def _create_user_tokens(db: Session, user: User):
    """Internal helper to create tokens and session record"""
    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id)
    
    # We use the session table to track refresh tokens for revocation
    session_id = uuid.uuid4().hex
    # We store the refresh token itself or a hash of it. 
    # For simplicity and revocation, we'll store the refresh token string as the 'token'
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    new_session = UserSession(
        id=session_id,
        token=refresh_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(new_session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user)
    }

@router.post("/register", response_model=BaseResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "EMAIL_EXISTS",
                    "message": "Email is already registered"
                }
            }
        )

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
    db.commit()
    db.refresh(new_user)

    # 3. Create Tokens
    token_data = _create_user_tokens(db, new_user)

    return BaseResponse(
        success=True,
        message="User registered successfully",
        data=token_data
    )

@router.post("/login", response_model=BaseResponse)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Incorrect email or password"
                }
            }
        )

    account = db.query(Account).filter(Account.user_id == user.id, Account.provider_id == "credential").first()
    if not account or not verify_password(form_data.password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Incorrect email or password"
                }
            }
        )

    token_data = _create_user_tokens(db, user)

    # Optionally set the refresh token in an HttpOnly cookie for extra security
    response.set_cookie(
        key="refresh_token",
        value=token_data["refresh_token"],
        expires=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
        secure=False # Set to True in production
    )

    return BaseResponse(
        success=True,
        message="Login successful",
        data=token_data
    )

@router.post("/refresh", response_model=BaseResponse)
def refresh_token(
    refresh_req: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Issue a new access token using a valid refresh token.
    """
    try:
        payload = decode_token(refresh_req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Check if session exists in DB (not revoked)
    db_session = db.query(UserSession).filter(UserSession.token == refresh_req.refresh_token).first()
    if not db_session:
        raise HTTPException(status_code=401, detail="Refresh token revoked or expired")
    
    if db_session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        db.delete(db_session)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Issue new access token
    new_access_token = create_access_token(subject=user.id, role=user.role.value)
    
    return BaseResponse(
        success=True,
        data={
            "access_token": new_access_token,
            "refresh_token": refresh_req.refresh_token, # Reuse same refresh token or rotate
            "token_type": "bearer",
            "user": UserOut.model_validate(user)
        }
    )

@router.get("/me", response_model=BaseResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Authenticated route to get current user details"""
    return BaseResponse(
        success=True,
        data={"user": UserOut.model_validate(current_user)}
    )

@router.post("/logout", response_model=BaseResponse)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Revoke the current session/refresh token"""
    # Try to get refresh token from cookie or body
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        db_session = db.query(UserSession).filter(UserSession.token == refresh_token).first()
        if db_session:
            db.delete(db_session)
            db.commit()
    
    response.delete_cookie("refresh_token")
    return BaseResponse(
        success=True,
        message="Logged out successfully"
    )
