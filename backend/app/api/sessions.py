import uuid
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.agent.session_manager import SessionManager

router = APIRouter()

class SessionResponse(BaseModel):
    session_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(db: Session = Depends(get_db)):
    manager = SessionManager(db)
    session = manager.create_session()
    return SessionResponse(
        session_id=session.id,
        created_at=session.created_at,
        updated_at=session.updated_at
    )

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: uuid.UUID, db: Session = Depends(get_db)):
    manager = SessionManager(db)
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        session_id=session.id,
        created_at=session.created_at,
        updated_at=session.updated_at
    )

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: uuid.UUID, db: Session = Depends(get_db)):
    manager = SessionManager(db)
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = manager.get_session_messages(session_id)
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]
