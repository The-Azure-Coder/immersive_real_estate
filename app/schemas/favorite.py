from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.property import PropertyOut

class FavoriteBase(BaseModel):
    property_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteOut(BaseModel):
    id: int
    user_id: int
    property_id: int
    created_at: datetime
    property: Optional[PropertyOut] = None

    class Config:
        from_attributes = True
