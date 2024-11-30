"""Script to find post summaries and media files in the downloads directory."""
import os
import logging
from pathlib import Path
from typing import Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('post_finder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def find_post_and_media() -> Optional[Tuple[str, Optional[Path]]]:
    """Recursively find post-summary.txt and associated media files.
    
    Returns:
        Tuple containing the post content and path to media file (if exists)
        or None if no post summary is found
    """
    downloads_dir = Path("downloads")
    
    if not downloads_dir.exists():
        logger.error("Downloads directory not found")
        return None
    
    logger.info(f"Searching for content in {downloads_dir}")
    
    # Walk through all subdirectories in downloads
    for root, dirs, files in os.walk(downloads_dir):
        root_path = Path(root)
        logger.debug(f"Checking directory: {root_path}")
        
        # Check if post-summary.txt exists in current directory
        summary_file = root_path / "post-summary.txt"
        if summary_file.exists():
            try:
                # Read the summary content
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_content = f.read().strip()
                
                if not summary_content:
                    logger.warning(f"Empty content in {summary_file}")
                    continue
                
                logger.info(f"Found post summary in {summary_file}")
                
                # Look for media file
                media_file = None
                media_dir = root_path / "media"
                if media_dir.exists() and media_dir.is_dir():
                    media_files = list(media_dir.glob('*'))
                    if media_files:
                        media_file = media_files[0]  # Get the first media file
                        logger.info(f"Found media file: {media_file.name}")
                    else:
                        logger.info("No media files found in media directory")
                else:
                    logger.info("No media directory found")
                
                # Verify the media file exists and is readable
                if media_file and not media_file.exists():
                    logger.error(f"Media file {media_file} no longer exists")
                    media_file = None
                
                return summary_content, media_file
                
            except Exception as e:
                logger.error(f"Error reading {summary_file}: {str(e)}")
                return None
    
    logger.warning("No post summary found in any subdirectory")
    return None

if __name__ == "__main__":
    result = find_post_and_media()
    if result:
        content, media = result
        logger.info("\nFound post summary:")
        logger.info(f"Content: {content}")
        if media:
            logger.info(f"\nFound media file: {media.name}")
        logger.info("\n" + "="*50 + "\n")
    else:
        logger.warning("No post summary found")
