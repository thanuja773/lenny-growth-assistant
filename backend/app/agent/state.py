import uuid
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from app.services.llm.schemas import SourceCitation

class AgentState(BaseModel):
    session_id: uuid.UUID
    query: str
    provider: str
    recent_history: List[dict] = Field(default_factory=list)
    retrieved_context: List[dict] = Field(default_factory=list)
    selected_tool: Optional[str] = None
    final_answer: Optional[str] = None
    sources: List[SourceCitation] = Field(default_factory=list)
    word_count: Optional[int] = None
