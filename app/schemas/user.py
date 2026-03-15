from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List
from app.models.user import UserRole
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: UserRole = UserRole.BUYER
    image: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
    email_verified: bool = Field(False, alias="emailVerified")
    is_active: bool = Field(True, alias="isActive")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class SessionOut(BaseModel):
    id: str
    token: str
    expires_at: datetime = Field(..., alias="expiresAt")
    user_id: str = Field(..., alias="userId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class UserSessionResponse(BaseModel):
    user: UserOut
    session: SessionOut
    
    model_config = ConfigDict(populate_by_name=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
