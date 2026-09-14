import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.llm.schemas import ChatRequest, ChatResponse
from app.agent.agent import GrowthAgent

router = APIRouter()
logger = logging.getLogger("lenny_assistant.api.chat")

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate chat response",
    description="Generate a grounded chat response using retrieved transcripts and a configured LLM.",
    responses={
        200: {"description": "Successful generation"},
        400: {"description": "Invalid query or unsupported provider"},
        503: {"description": "LLM provider or retrieval service unavailable"},
    },
)
def generate_chat_response(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty or whitespace-only.",
        )

    try:
        agent = GrowthAgent(db=db)
        return agent.process_request(request)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except RuntimeError as re:
        logger.error(f"Chat generation failure: {re}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(re),
        )
    except Exception as e:
        logger.error(f"Unexpected chat generation failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat generation service is currently unavailable.",
        )
