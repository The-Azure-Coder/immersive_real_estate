from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid
from typing import List

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, Account
from app.schemas.user import UserCreate, UserOut
from app.api.v1.endpoints.deps import get_current_user, require_role
from app.schemas.base import BaseResponse, PaginatedResponse, PaginationMetadata
from app.core.config import settings

router = APIRouter()

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

    # 2. Create Account (for credentials)
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

    # 3. Create Token
    access_token = create_access_token(subject=new_user.id, role=new_user.role.value)

    return BaseResponse(
        success=True,
        message="User registered successfully",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserOut.model_validate(new_user)
        }
    )

@router.post("/login", response_model=BaseResponse)
def login(
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

    access_token = create_access_token(subject=user.id, role=user.role.value)

    return BaseResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token,
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
