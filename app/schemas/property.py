from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    price: float
    land_size: float

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(PropertyBase):
    title: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = None
    land_size: Optional[float] = None

class PropertyOut(PropertyBase):
    id: int
    owner_id: int
    image_url: str
    model_3d_url: Optional[str] = None
    is_model_generated: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
