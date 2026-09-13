import logging
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("lenny_assistant")
    return logger

logger = setup_logging()\n