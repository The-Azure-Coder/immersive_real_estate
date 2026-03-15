from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.user import User, Session as UserSession
from typing import Optional

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    # 1. Get session token from cookie or Authorization header
    session_token = request.cookies.get("better-auth.session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Look up session in database
    # Note: Using UserSession which is aliased to Session model in app/models/user.py
    session_record = db.query(UserSession).filter(UserSession.token == session_token).first()
    
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
        )

    # 3. Check if session is expired
    if session_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    # 4. Get user
    user = db.query(User).filter(User.id == session_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
