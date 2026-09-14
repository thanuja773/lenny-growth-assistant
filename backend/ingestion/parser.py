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
