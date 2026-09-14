from fastapi import APIRouter
from app.api import health, retrieval, chat, sessions, artifacts

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(retrieval.router, prefix="/api/retrieval", tags=["retrieval"])
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["retrieval"], include_in_schema=False)
api_router.include_router(chat.router, prefix="/api/chat", tags=["chat"])
api_router.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
api_router.include_router(artifacts.router, prefix="/api/artifacts", tags=["artifacts"])

