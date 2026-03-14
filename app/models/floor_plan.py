from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class FloorPlan(Base):
    __tablename__ = "floor_plans"

    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=False)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    sqft = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    style = Column(String)  # e.g., Modern, Traditional
    image_url = Column(String)
    file_url = Column(String)  # PDF/DWG file URL
    created_at = Column(DateTime, server_default=func.now())

    professional = relationship("Professional")
