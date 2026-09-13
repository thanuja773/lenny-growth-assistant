from fastapi import FastAPI
from app.api.router import api_router
from app.core.logging import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title="Lenny Growth Assistant API",
        version="0.1.0",
        description="Backend API for Lenny Growth Assistant"
    )

    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up Lenny Growth Assistant API")

    return app

app = create_app()
