from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from jose import JWTError
from app.core.database import get_db
from app.models.user import User
from app.core.security import decode_token
from typing import Optional

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    # 1. Get access token from Authorization header (standard)
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Optional fallback to cookie if needed (e.g. for some browser direct calls)
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Look up session in database
    # Note: Using UserSession which is aliased to Session model in app/models/user.py
    session_record = db.query(UserSession).filter(UserSession.token == session_token).first()
    
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Get user from DB (to ensure they still exist and are active)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    return user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        # current_user.role is an enum, we check its value
        if current_user.role.value != required_role and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Insufficient permissions. Required: {required_role}"
            )
        return current_user
    return role_checker
