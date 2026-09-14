import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models.artifact import Artifact
from app.services.llm.schemas import SourceCitation

logger = logging.getLogger("lenny_assistant.agent.artifact_manager")

class ArtifactManager:
    def __init__(self, db: Session):
        self.db = db

    def create_artifact(
        self,
        session_id: uuid.UUID,
        artifact_type: str,
        title: str,
        content: str,
        format: str = "markdown",
        word_count: Optional[int] = None,
        sources: Optional[List[SourceCitation]] = None
    ) -> Artifact:
        try:
            formatted_sources = []
            if sources:
                for s in sources:
                    if hasattr(s, "dict"):
                        formatted_sources.append(s.dict())
                    elif isinstance(s, dict):
                        formatted_sources.append(s)
                    else:
                        formatted_sources.append(s)
            
            artifact = Artifact(
                session_id=session_id,
                artifact_type=artifact_type,
                title=title,
                content=content,
                format=format,
                word_count=word_count,
                sources=formatted_sources
            )
            self.db.add(artifact)
            self.db.commit()
            self.db.refresh(artifact)
            return artifact
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create artifact: {e}")
            raise RuntimeError(f"Database error while saving artifact: {str(e)}")

    def get_artifact(self, artifact_id: uuid.UUID) -> Optional[Artifact]:
        return self.db.query(Artifact).filter(Artifact.id == artifact_id).first()

    def get_session_artifacts(self, session_id: uuid.UUID) -> List[Artifact]:
        return self.db.query(Artifact).filter(Artifact.session_id == session_id).order_by(Artifact.created_at.desc()).all()
