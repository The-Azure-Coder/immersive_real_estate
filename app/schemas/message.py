from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.schemas.user import UserOut

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    conversation_id: int
    sender_id: int
    is_read: bool = False
    created_at: datetime
    is_own: Optional[bool] = None

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    receiver_id: int
    initial_message: str

class ConversationOut(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    other_user: Optional[UserOut] = None
    last_message: Optional[str] = None
    unread_count: int = 0

    class Config:
        from_attributes = True
