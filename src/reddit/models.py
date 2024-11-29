from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class RedditComment:
    """Model representing a Reddit comment."""
    id: str
    author: str
    body: str
    created_utc: datetime
    score: int
    parent_id: str
    is_submitter: bool

@dataclass
class RedditMedia:
    """Model representing media content from a Reddit post."""
    url: str
    type: str  # 'image', 'video', 'gallery'
    filename: str
    media_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

@dataclass
class RedditPost:
    """Model representing a Reddit post."""
    id: str
    title: str
    author: str
    created_utc: datetime
    score: int
    url: Optional[str]
    selftext: str
    subreddit: str
    comments: List[Dict[str, Any]]
    is_gallery: bool
    gallery_data: Optional[Dict[str, Any]]

@dataclass
class DownloadResult:
    """Model representing the result of a download operation."""
    success: bool
    downloaded_files: List[str]
    errors: List[str]