import argparse
import logging
import os
import time
from typing import Optional
from ingestion.config import settings
from ingestion.source import fetch_episodes_list, download_transcript
from ingestion.parser import parse_metadata
from ingestion.cleaner import clean_text
from ingestion.chunker import chunk_text
from ingestion.embedder import Embedder
from ingestion.loader import load_transcript

logger = logging.getLogger(__name__)

def run_pipeline(limit: Optional[int] = None, dry_run: bool = False, force: bool = False):
    start_time = time.time()
    
    episodes = fetch_episodes_list(limit=limit)
    if not episodes:
        if os.path.exists(settings.DATA_DIR):
            cached_files = [f[:-3] for f in sorted(os.listdir(settings.DATA_DIR)) if f.endswith(".md")]
            if cached_files:
                logger.info(f"Using {len(cached_files)} locally cached transcripts from {settings.DATA_DIR}")
                episodes = [{"name": name} for name in cached_files]
                if limit:
                    episodes = episodes[:limit]
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
            
            load_transcript(metadata, chunks, embeddings, dry_run=dry_run, force=force)
            
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

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast Transcripts")
    parser.add_argument("--limit", type=int, help="Limit number of transcripts to process", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Run without database persistence")
    parser.add_argument("--force", action="store_true", help="Force re-ingestion even if previously ingested")
    
    args = parser.parse_args()
    
    run_pipeline(limit=args.limit, dry_run=args.dry_run, force=args.force)

if __name__ == "__main__":
    main()
