from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.retrieval.retriever import RetrievalService
from app.services.llm.schemas import SourceCitation

class SearchTranscriptsTool:
    def __init__(self, db: Session):
        self.retrieval_service = RetrievalService(db)

    def execute(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        retrieval_results = self.retrieval_service.search(query=query)
        chunks = retrieval_results.results[:top_k]
        
        results = []
        sources = []
        for i, chunk in enumerate(chunks, 1):
            source = SourceCitation(
                transcript_title=chunk.transcript_title,
                source_url=chunk.source_url,
                chunk_index=chunk.chunk_index,
                similarity_score=chunk.similarity_score
            )
            sources.append(source)
            results.append({
                "title": chunk.transcript_title,
                "source_url": chunk.source_url,
                "chunk_index": chunk.chunk_index,
                "similarity_score": chunk.similarity_score,
                "text": chunk.text
            })
            
        return {
            "chunks": results,
            "sources": sources
        }
