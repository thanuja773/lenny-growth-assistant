import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.session import Session as SessionModel
from app.db.models.message import Message as MessageModel
from app.db.models.user import User

class SessionManager:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_default_user(self) -> uuid.UUID:
        user = self.db.query(User).first()
        if not user:
            user = User()
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user.id

    def create_session(self, user_id: Optional[uuid.UUID] = None) -> SessionModel:
        if not user_id:
            user_id = self._get_or_create_default_user()
        
        new_session = SessionModel(user_id=user_id)
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def get_session(self, session_id: uuid.UUID) -> Optional[SessionModel]:
        return self.db.query(SessionModel).filter(SessionModel.id == session_id).first()

    def get_session_messages(self, session_id: uuid.UUID, limit: int = 50) -> List[MessageModel]:
        return self.db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(MessageModel.created_at.asc()).limit(limit).all()

    def add_message(self, session_id: uuid.UUID, role: str, content: str) -> MessageModel:
        message = MessageModel(
            session_id=session_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
