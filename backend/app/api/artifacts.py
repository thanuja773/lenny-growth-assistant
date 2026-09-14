import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.llm.schemas import ArtifactResponse
from app.agent.artifact_manager import ArtifactManager

router = APIRouter()
logger = logging.getLogger("lenny_assistant.api.artifacts")

@router.get(
    "/{artifact_id}",
    response_model=ArtifactResponse,
    status_code=status.HTTP_200_OK,
    summary="Get an artifact by ID",
)
def get_artifact(artifact_id: uuid.UUID, db: Session = Depends(get_db)):
    manager = ArtifactManager(db)
    artifact = manager.get_artifact(artifact_id)
    
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found."
        )
        
    return ArtifactResponse(
        artifact_id=str(artifact.id),
        session_id=str(artifact.session_id),
        title=artifact.title,
        type=artifact.artifact_type,
        format=artifact.format,
        content=artifact.content,
        word_count=artifact.word_count,
        sources=artifact.sources or [],
        created_at=artifact.created_at.isoformat()
    )

@router.get(
    "/session/{session_id}",
    response_model=List[ArtifactResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all artifacts for a session",
)
def get_session_artifacts(session_id: uuid.UUID, db: Session = Depends(get_db)):
    manager = ArtifactManager(db)
    artifacts = manager.get_session_artifacts(session_id)
    
    return [
        ArtifactResponse(
            artifact_id=str(artifact.id),
            session_id=str(artifact.session_id),
            title=artifact.title,
            type=artifact.artifact_type,
            format=artifact.format,
            content=artifact.content,
            word_count=artifact.word_count,
            sources=artifact.sources or [],
            created_at=artifact.created_at.isoformat()
        ) for artifact in artifacts
    ]
