from fastapi import FastAPI
from app.api.router import api_router
from app.core.logging import logger
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

def create_app() -> FastAPI:
    app = FastAPI(
        title="Lenny Growth Assistant API",
        version="0.1.0",
        description="Backend API for Lenny Growth Assistant"
    )

    from starlette.middleware.cors import CORSMiddleware
    from app.core.config import settings
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    import uuid
    from starlette.middleware.base import BaseHTTPMiddleware
    from app.core.logging import request_id_var

    class RequestIDMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request_id = str(uuid.uuid4())
            token = request_id_var.set(request_id)
            try:
                response = await call_next(request)
                response.headers["X-Request-ID"] = request_id
                return response
            finally:
                request_id_var.reset(token)

    app.add_middleware(RequestIDMiddleware)

    app.include_router(api_router)

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request, exc):
        logger.error(f"Database error on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=503,
            content={"detail": "Service unavailable: Database connection failed."}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."}
        )

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up Lenny Growth Assistant API")

    return app

app = create_app()
