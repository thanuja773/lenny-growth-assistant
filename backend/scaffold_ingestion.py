import os

CONFIG_PY = """
import os
from pydantic_settings import BaseSettings

class IngestionSettings(BaseSettings):
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 100
    GITHUB_REPO: str = "ChatPRD/lennys-podcast-transcripts"
    DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/lenny_growth_assistant")

settings = IngestionSettings()
"""

SOURCE_PY = """
import os
import requests
import logging
from typing import List, Dict
from ingestion.config import settings

logger = logging.getLogger(__name__)

def fetch_episodes_list(limit: int = None) -> List[Dict]:
    logger.info(f"Fetching episodes list from {settings.GITHUB_REPO}...")
    url = f"https://api.github.com/repos/{settings.GITHUB_REPO}/contents/episodes"
    response = requests.get(url)
    if response.status_code == 403:
        logger.warning("GitHub API rate limit exceeded. Attempting to proceed if data is already cached locally.")
        return [] # We'll handle local fallback in pipeline
    response.raise_for_status()
    items = response.json()
    if limit:
        items = items[:limit]
    return items

def download_transcript(episode_folder: str) -> str:
    url = f"https://raw.githubusercontent.com/{settings.GITHUB_REPO}/main/episodes/{episode_folder}/transcript.md"
    target_path = os.path.join(settings.DATA_DIR, f"{episode_folder}.md")
    
    if os.path.exists(target_path):
        logger.debug(f"Using cached file: {target_path}")
        return target_path
        
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    logger.info(f"Downloading {episode_folder}...")
    response = requests.get(url)
    response.raise_for_status()
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    return target_path
"""

PARSER_PY = """
import os
from typing import Dict, Any

def parse_metadata(episode_folder: str, file_path: str) -> Dict[str, Any]:
    # Parse basic metadata from the folder name
    # e.g. "ada-chen-rekhi" -> "Ada Chen Rekhi"
    title = " ".join([word.capitalize() for word in episode_folder.split("-")])
    
    return {
        "title": title,
        "source_url": f"https://github.com/ChatPRD/lennys-podcast-transcripts/tree/main/episodes/{episode_folder}/transcript.md",
        "source_type": "podcast",
        "published_at": None,  # Not easily available from raw repo without commits
        "original_path": file_path
    }
"""

CLEANER_PY = """
import re

def clean_text(text: str) -> str:
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip leading/trailing whitespaces per line
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()
"""

CHUNKER_PY = """
import re
from typing import List
from ingestion.config import settings

def chunk_text(text: str, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP) -> List[str]:
    # We want to preserve speaker turns.
    # We can approximate token count by word count * 1.3
    # A word is roughly ~1.3 tokens in English. So 700 tokens ~ 530 words.
    target_words = int(chunk_size / 1.3)
    overlap_words = int(overlap / 1.3)
    
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for p in paragraphs:
        p_words = len(p.split())
        if current_length + p_words > target_words and current_chunk:
            # Save the current chunk
            chunks.append('\n\n'.join(current_chunk))
            
            # Start new chunk with overlap
            # We keep the last few paragraphs that fit into overlap_words
            overlap_chunk = []
            overlap_length = 0
            for prev_p in reversed(current_chunk):
                prev_words = len(prev_p.split())
                if overlap_length + prev_words <= overlap_words:
                    overlap_chunk.insert(0, prev_p)
                    overlap_length += prev_words
                else:
                    break
                    
            current_chunk = overlap_chunk + [p]
            current_length = overlap_length + p_words
        else:
            current_chunk.append(p)
            current_length += p_words
            
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
        
    return chunks
"""

EMBEDDER_PY = """
import logging
from typing import List
from ingestion.config import settings
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self):
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is not installed.")
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
"""

LOADER_PY = """
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ingestion.config import settings
from app.db.models.transcript import Transcript
from app.db.models.transcript_chunk import TranscriptChunk

logger = logging.getLogger(__name__)

def get_session():
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def load_transcript(metadata: dict, chunks: list, embeddings: list, dry_run: bool = False):
    if dry_run:
        logger.info(f"[DRY-RUN] Would save {metadata['title']} with {len(chunks)} chunks.")
        return
        
    session = get_session()
    try:
        # Check idempotency: does this transcript exist?
        existing = session.query(Transcript).filter_by(source_url=metadata['source_url']).first()
        if existing:
            logger.info(f"Transcript '{metadata['title']}' already exists. Re-ingesting...")
            # Delete old chunks
            session.query(TranscriptChunk).filter_by(transcript_id=existing.id).delete()
            transcript_id = existing.id
            # Update metadata
            existing.title = metadata['title']
        else:
            logger.info(f"Inserting new transcript: {metadata['title']}")
            new_t = Transcript(
                title=metadata['title'],
                source_url=metadata['source_url'],
                source_type=metadata['source_type']
            )
            session.add(new_t)
            session.commit()
            transcript_id = new_t.id
            
        # Insert chunks
        chunk_objects = []
        for i, (content, emb) in enumerate(zip(chunks, embeddings)):
            chunk_objects.append(TranscriptChunk(
                transcript_id=transcript_id,
                chunk_index=i,
                content=content,
                embedding=emb
            ))
            
        session.bulk_save_objects(chunk_objects)
        session.commit()
        logger.info(f"Saved {len(chunk_objects)} chunks for '{metadata['title']}'")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Database error during load: {e}")
        raise
    finally:
        session.close()
"""

PIPELINE_PY = """
import logging
import time
from typing import Optional
from ingestion.source import fetch_episodes_list, download_transcript
from ingestion.parser import parse_metadata
from ingestion.cleaner import clean_text
from ingestion.chunker import chunk_text
from ingestion.embedder import Embedder
from ingestion.loader import load_transcript

logger = logging.getLogger(__name__)

def run_pipeline(limit: Optional[int] = None, dry_run: bool = False):
    start_time = time.time()
    
    episodes = fetch_episodes_list(limit=limit)
    if not episodes:
        logger.error("No episodes found. Exiting.")
        return
        
    embedder = Embedder()
    
    stats = {
        "discovered": len(episodes),
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "chunks": 0
    }
    
    for i, ep in enumerate(episodes, 1):
        folder = ep['name']
        logger.info(f"--- Ingesting {i}/{len(episodes)}: {folder} ---")
        try:
            file_path = download_transcript(folder)
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
                
            metadata = parse_metadata(folder, file_path)
            cleaned_text = clean_text(raw_text)
            
            if not cleaned_text:
                logger.warning(f"Empty transcript for {folder}. Skipping.")
                stats["skipped"] += 1
                continue
                
            chunks = chunk_text(cleaned_text)
            embeddings = embedder.embed(chunks)
            
            load_transcript(metadata, chunks, embeddings, dry_run=dry_run)
            
            stats["success"] += 1
            stats["chunks"] += len(chunks)
            
        except Exception as e:
            logger.error(f"Failed to ingest {folder}: {e}")
            stats["failed"] += 1
            
    elapsed = time.time() - start_time
    logger.info("=== INGESTION SUMMARY ===")
    logger.info(f"Time Elapsed: {elapsed:.2f} seconds")
    logger.info(f"Discovered: {stats['discovered']}")
    logger.info(f"Success: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Skipped: {stats['skipped']}")
    logger.info(f"Total Chunks: {stats['chunks']}")
    logger.info("=========================")
"""

MAIN_PY = """
import argparse
import logging
from ingestion.pipeline import run_pipeline

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast Transcripts")
    parser.add_argument("--limit", type=int, help="Limit number of transcripts to process", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Run without database persistence")
    
    args = parser.parse_args()
    
    run_pipeline(limit=args.limit, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
"""

INIT_PY = ""

files = {
    "__init__.py": INIT_PY,
    "config.py": CONFIG_PY,
    "source.py": SOURCE_PY,
    "parser.py": PARSER_PY,
    "cleaner.py": CLEANER_PY,
    "chunker.py": CHUNKER_PY,
    "embedder.py": EMBEDDER_PY,
    "loader.py": LOADER_PY,
    "pipeline.py": PIPELINE_PY,
    "__main__.py": MAIN_PY
}

def scaffold():
    os.makedirs("ingestion", exist_ok=True)
    for fname, content in files.items():
        with open(os.path.join("ingestion", fname), "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
            
if __name__ == "__main__":
    scaffold()
