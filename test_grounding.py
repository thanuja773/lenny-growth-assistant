import sys
import os
sys.path.insert(0, os.path.abspath('backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.llm.service import LLMService
from app.services.llm.schemas import ChatRequest

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

service = LLMService(db)
try:
    req = ChatRequest(query='What advice is given about growth?', provider='ollama')
    resp = service.generate_chat_response(req)
    print(resp.answer)
    print('retrieval_count:', resp.retrieval_count)
except Exception as e:
    import traceback
    traceback.print_exc()
