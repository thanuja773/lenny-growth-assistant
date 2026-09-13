import uuid
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    source_url = Column(String(1024), nullable=True)
    source_type = Column(String(50), nullable=False) # 'podcast', 'newsletter'
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())\n