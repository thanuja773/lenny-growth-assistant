from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
import logging

router = APIRouter()
logger = logging.getLogger("lenny_assistant.health")

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to check db connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )\n