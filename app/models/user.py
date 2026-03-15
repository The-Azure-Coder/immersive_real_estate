from sqlalchemy import Column, String, Boolean, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    BUYER = "buyer"
    OWNER = "owner"
    ARCHITECT = "architect"
    MASON = "mason"
    CARPENTER = "carpenter"
    CONTRACTOR = "contractor"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "user" # Better Auth defaults to "user" (singular)

    id = Column(String, primary_key=True) # Better Auth uses strings for IDs usually
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    email_verified = Column(Boolean, default=False)
    image = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.BUYER)
    is_active = Column(Boolean, default=True)
    
    # Better Auth standard fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    properties = relationship("Property", back_populates="owner")
    professional_profile = relationship("Professional", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "session"

    id = Column(String, primary_key=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="sessions")

class Account(Base):
    __tablename__ = "account"

    id = Column(String, primary_key=True)
    account_id = Column(String, nullable=False)
    provider_id = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    id_token = Column(Text, nullable=True)
    access_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    refresh_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    scope = Column(Text, nullable=True)
    password = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="accounts")
