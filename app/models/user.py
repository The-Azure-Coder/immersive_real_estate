from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
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
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.BUYER)
    is_active = Column(Boolean, default=True)

    # Relationships
    properties = relationship("Property", back_populates="owner")
    professional_profile = relationship("Professional", back_populates="user", uselist=False)
