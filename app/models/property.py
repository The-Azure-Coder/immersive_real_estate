from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("user.id"), nullable=False) # Changed to String and table name to user
    title = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    price = Column(Float)
    land_size = Column(Float)
    image_url = Column(String)          # original image URL (S3 or local)
    model_3d_url = Column(String, nullable=True)  # GLB model URL
    is_model_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="properties")
