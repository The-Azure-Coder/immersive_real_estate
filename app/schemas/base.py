from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime, timezone

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: datetime = datetime.now(timezone.utc)

class PaginationMetadata(BaseModel):
    page: int
    limit: int
    totalPages: int
    totalItems: int
    hasNext: bool
    hasPrev: bool

class PaginatedResponse(BaseResponse):
    pagination: Optional[PaginationMetadata] = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[List[Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    timestamp: datetime = datetime.now(timezone.utc)
    path: Optional[str] = None
