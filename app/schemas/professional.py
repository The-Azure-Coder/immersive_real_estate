from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProfessionalBase(BaseModel):
    profession: str
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    hourly_rate: Optional[float] = None

class ProfessionalCreate(ProfessionalBase):
    pass

class ProfessionalOut(ProfessionalBase):
    id: int
    user_id: str
    model_config = ConfigDict(from_attributes=True)
