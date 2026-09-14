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
