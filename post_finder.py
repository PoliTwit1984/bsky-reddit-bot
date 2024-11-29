"""Script to find post summaries and media files in the downloads directory."""
import os
from pathlib import Path
from typing import Optional, Tuple

def find_post_and_media() -> Optional[Tuple[str, Optional[Path]]]:
    """Recursively find post-summary.txt and associated media files.
    
    Returns:
        Tuple containing the post content and path to media file (if exists)
        or None if no post summary is found
    """
    downloads_dir = Path("downloads")
    
    if not downloads_dir.exists():
        print("Downloads directory not found")
        return None
    
    # Walk through all subdirectories in downloads
    for root, dirs, files in os.walk(downloads_dir):
        root_path = Path(root)
        
        # Check if post-summary.txt exists in current directory
        summary_file = root_path / "post-summary.txt"
        if summary_file.exists():
            try:
                # Read the summary content
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_content = f.read().strip()
                
                # Look for media file
                media_file = None
                media_dir = root_path / "media"
                if media_dir.exists() and media_dir.is_dir():
                    media_files = list(media_dir.glob('*'))
                    if media_files:
                        media_file = media_files[0]  # Get the first media file
                
                return summary_content, media_file
                
            except Exception as e:
                print(f"Error reading {summary_file}: {str(e)}")
                return None
    
    return None

if __name__ == "__main__":
    result = find_post_and_media()
    if result:
        content, media = result
        print("\nFound post summary:")
        print("Content:", content)
        if media:
            print("\nFound media file:", media.name)
        print("\n" + "="*50 + "\n")
    else:
        print("No post summary found")