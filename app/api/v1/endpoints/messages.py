from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from app.api.v1.endpoints.deps import get_db, get_current_user
from app.models.user import User
from app.models.message import Conversation, Message
from app.schemas.message import ConversationCreate, ConversationOut, MessageCreate, MessageOut

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = db.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id
        )
    ).all()
    
    results = []
    for conv in conversations:
        other_user_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        last_msg = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.desc()).first()
        unread_count = db.query(Message).filter(
            and_(
                Message.conversation_id == conv.id,
                Message.sender_id != current_user.id,
                Message.is_read == False
            )
        ).count()
        
        results.append({
            "id": conv.id,
            "user1_id": conv.user1_id,
            "user2_id": conv.user2_id,
            "created_at": conv.created_at,
            "other_user": other_user,
            "last_message": last_msg.content if last_msg else None,
            "unread_count": unread_count
        })
        
    return results

@router.post("/conversations", response_model=ConversationOut)
def start_conversation(
    conv_in: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if receiver exists
    receiver = db.query(User).filter(User.id == conv_in.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Check if conversation already exists
    existing = db.query(Conversation).filter(
        or_(
            and_(Conversation.user1_id == current_user.id, Conversation.user2_id == conv_in.receiver_id),
            and_(Conversation.user1_id == conv_in.receiver_id, Conversation.user2_id == current_user.id)
        )
    ).first()
    
    if existing:
        # Add initial message to existing
        msg = Message(conversation_id=existing.id, sender_id=current_user.id, content=conv_in.initial_message)
        db.add(msg)
        db.commit()
        return {
            "id": existing.id,
            "user1_id": existing.user1_id,
            "user2_id": existing.user2_id,
            "created_at": existing.created_at,
            "other_user": receiver,
            "last_message": conv_in.initial_message,
            "unread_count": 0
        }

    conv = Conversation(user1_id=current_user.id, user2_id=conv_in.receiver_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    msg = Message(conversation_id=conv.id, sender_id=current_user.id, content=conv_in.initial_message)
    db.add(msg)
    db.commit()
    
    return {
        "id": conv.id,
        "user1_id": conv.user1_id,
        "user2_id": conv.user2_id,
        "created_at": conv.created_at,
        "other_user": receiver,
        "last_message": conv_in.initial_message,
        "unread_count": 0
    }

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageOut])
def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv or (conv.user1_id != current_user.id and conv.user2_id != current_user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    
    # Mark others' messages as read
    db.query(Message).filter(
        and_(
            Message.conversation_id == conversation_id,
            Message.sender_id != current_user.id,
            Message.is_read == False
        )
    ).update({"is_read": True})
    db.commit()
    
    for m in messages:
        m.is_own = m.sender_id == current_user.id
        
    return messages

@router.post("/conversations/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int,
    msg_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv or (conv.user1_id != current_user.id and conv.user2_id != current_user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    msg = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=msg_in.content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    msg.is_own = True
    return msg
