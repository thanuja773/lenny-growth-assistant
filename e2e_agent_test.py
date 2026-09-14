import sys
import os
sys.path.insert(0, os.path.abspath('backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.agent.agent import GrowthAgent
from app.services.llm.schemas import ChatRequest

def run_e2e():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    agent = GrowthAgent(db)
    
    print("--- Turn 1 ---")
    req1 = ChatRequest(query="What advice is given about growth?", provider="ollama")
    resp1 = agent.process_request(req1)
    print(f"Session ID: {resp1.session_id}")
    print(f"Tool Used: {resp1.tool_used}")
    print(f"Retrieval Count: {resp1.retrieval_count}")
    print(f"Answer: {resp1.answer}\n")
    
    print("--- Turn 2 ---")
    req2 = ChatRequest(query="Which part of that advice is most relevant to startups?", provider="ollama", session_id=resp1.session_id)
    resp2 = agent.process_request(req2)
    print(f"Session ID: {resp2.session_id}")
    print(f"Tool Used: {resp2.tool_used}")
    print(f"Retrieval Count: {resp2.retrieval_count}")
    print(f"Answer: {resp2.answer}\n")
    
    print("--- Turn 3 (Ship 30) ---")
    req3 = ChatRequest(query="Turn the discussion into a Ship 30 for 30 essay.", provider="ollama", session_id=resp1.session_id)
    resp3 = agent.process_request(req3)
    print(f"Session ID: {resp3.session_id}")
    print(f"Tool Used: {resp3.tool_used}")
    print(f"Retrieval Count: {resp3.retrieval_count}")
    print(f"Word Count: {resp3.word_count}")
    print(f"Answer: {resp3.answer}\n")
    
if __name__ == "__main__":
    run_e2e()
