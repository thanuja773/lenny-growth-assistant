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

def load_transcript(metadata: dict, chunks: list, embeddings: list, dry_run: bool = False, force: bool = False):
    if dry_run:
        logger.info(f"[DRY-RUN] Would save {metadata['title']} with {len(chunks)} chunks.")
        return
        
    session = get_session()
    try:
        # Check idempotency: does this transcript exist?
        existing = session.query(Transcript).filter_by(source_url=metadata['source_url']).first()
        if existing:
            logger.info(f"Transcript '{metadata['title']}' already exists. {'Force re-ingesting' if force else 'Re-ingesting'}...")
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
