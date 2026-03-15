from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FloorPlanBase(BaseModel):
    title: str
    description: str
    price: float
    sqft: int
    bedrooms: int
    bathrooms: float
    style: str

class FloorPlanCreate(FloorPlanBase):
    professional_id: int
    image_url: str
    file_url: str

class FloorPlanOut(FloorPlanBase):
    id: int
    professional_id: int
    image_url: str
    file_url: str
    created_at: datetime
    architect_name: Optional[str] = None

    class Config:
        from_attributes = True
