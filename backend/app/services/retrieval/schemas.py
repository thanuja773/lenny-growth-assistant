from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    chunk_id: UUID = Field(..., description="Unique identifier for the chunk")
    transcript_id: UUID = Field(..., description="Identifier of the parent transcript")
    transcript_title: str = Field(..., description="Title of the transcript episode")
    source_url: Optional[str] = Field(None, description="Original source URL of the transcript")
    source_type: str = Field(..., description="Type of source, e.g., podcast")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp if available")
    chunk_index: int = Field(..., description="Positional index of the chunk in the transcript")
    text: str = Field(..., description="Extracted chunk text content")
    similarity_score: float = Field(..., description="Normalized cosine similarity score between 0 and 1")


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000, description="Semantic search query string")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Maximum number of relevant chunks to retrieve")


class RetrievalResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    results: List[SearchResultItem] = Field(default_factory=list, description="Ordered list of relevant transcript chunks")
    count: int = Field(..., description="Number of results returned")
