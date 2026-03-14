from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    profession = Column(String)   # e.g., architect, mason
    bio = Column(Text)
    portfolio_url = Column(String, nullable=True)
    hourly_rate = Column(Float, nullable=True)

    user = relationship("User", back_populates="professional_profile")
