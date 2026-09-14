import logging
from app.core.config import settings
import contextvars

request_id_var = contextvars.ContextVar("request_id", default="-")

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

def setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - [req_id=%(request_id)s] - %(message)s",
    )
    logger = logging.getLogger("lenny_assistant")
    
    # Add filter to all existing handlers
    for handler in logging.root.handlers:
        handler.addFilter(RequestIdFilter())
        
    return logger

logger = setup_logging()
