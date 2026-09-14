import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.retrieval.retriever import RetrievalService
from app.services.retrieval.schemas import RetrievalRequest, RetrievalResponse

router = APIRouter()
logger = logging.getLogger("lenny_assistant.api.retrieval")


@router.post(
    "/search",
    response_model=RetrievalResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic transcript search",
    description="Retrieve relevant transcript chunks matching the query using cosine similarity in pgvector.",
    responses={
        200: {"description": "Successful retrieval (may contain 0 results if none pass similarity threshold)"},
        400: {"description": "Invalid query or top_k parameter"},
        503: {"description": "Database or embedding service unavailable"},
    },
)
def search_transcripts(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
) -> RetrievalResponse:
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty or whitespace-only.",
        )

    if request.top_k is not None:
        if request.top_k < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="top_k must be at least 1.",
            )
        if request.top_k > settings.RETRIEVAL_MAX_TOP_K:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"top_k cannot exceed {settings.RETRIEVAL_MAX_TOP_K}.",
            )

    try:
        service = RetrievalService(db=db)
        return service.search(query=request.query, top_k=request.top_k)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        logger.error(f"Retrieval service failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Retrieval service or database is currently unavailable.",
        )
