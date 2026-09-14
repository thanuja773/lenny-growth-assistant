import pytest
from ingestion.parser import parse_metadata
from ingestion.cleaner import clean_text
from ingestion.chunker import chunk_text
from ingestion.embedder import Embedder

def test_parse_metadata():
    metadata = parse_metadata("ada-chen-rekhi", "/path/to/transcript.md")
    assert metadata["title"] == "Ada Chen Rekhi"
    assert metadata["source_type"] == "podcast"
    assert "ada-chen-rekhi" in metadata["source_url"]

def test_clean_text():
    raw_text = "Hello\n\n\nWorld\n  Extra spaces  \n"
    cleaned = clean_text(raw_text)
    assert cleaned == "Hello\n\nWorld\nExtra spaces"

def test_chunk_text():
    text = "Word " * 600
    # ~600 words should be split because 600 words > 538 words (700 tokens)
    chunks = chunk_text(text, chunk_size=700, overlap=100)
    assert len(chunks) >= 1
    assert len(chunks[0].split()) <= 600

def test_embedder_dimension():
    embedder = Embedder()
    embeddings = embedder.embed(["Hello world", "Test sentence"])
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
