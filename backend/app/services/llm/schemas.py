from typing import List, Optional
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    transcript_title: str = Field(..., description="Title of the transcript episode")
    source_url: Optional[str] = Field(None, description="Original source URL of the transcript")
    chunk_index: int = Field(..., description="Positional index of the chunk in the transcript")
    similarity_score: float = Field(..., description="Normalized cosine similarity score between 0 and 1")

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's question to answer")
    provider: Optional[str] = Field(None, description="Optional LLM provider to use (e.g., 'ollama', 'anthropic')")
    session_id: Optional[str] = Field(None, description="Optional UUID string for conversation session tracking")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The generated grounded answer")
    sources: List[SourceCitation] = Field(default_factory=list, description="Sources used to generate the answer")
    provider: Optional[str] = Field(None, description="The LLM provider that generated the response")
    model: Optional[str] = Field(None, description="The specific model used")
    retrieval_count: int = Field(..., description="Number of retrieved chunks provided as context")
    session_id: Optional[str] = Field(None, description="The UUID of the session for conversation context")
    tool_used: Optional[str] = Field(None, description="The specific tool executed by the agent, if any")
    word_count: Optional[int] = Field(None, description="Number of words generated (primarily for content generation tasks)")
