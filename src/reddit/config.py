from dataclasses import dataclass
from typing import Optional, List
from .exceptions import ValidationError

@dataclass
class RedditCredentials:
    """Reddit API credentials configuration."""
    client_id: str
    client_secret: str
    user_agent: str = "Python:ContentDownloader:v1.0"

    def validate(self) -> None:
        """Validate Reddit credentials."""
        if not self.client_id:
            raise ValidationError("Reddit client ID is required")
        if not self.client_secret:
            raise ValidationError("Reddit client secret is required")
        if not self.user_agent:
            raise ValidationError("Reddit user agent is required")

@dataclass
class SubredditConfig:
    """Configuration for a subreddit download operation."""
    name: str  # Changed from subreddit_name to match YAML
    filter_type: str  # 'hot', 'new', 'top', 'rising'
    time_filter: Optional[str] = None  # 'all', 'day', 'hour', 'month', 'week', 'year'
    limit: int = 10
    download_media: bool = True
    download_comments: bool = False
    max_comments: int = 5  # Number of top comments to download, sorted by score
    skip_no_media: bool = True  # Skip posts without media or delete their folders
    batch_size: int = 5
    timeout: int = 30

    def validate(self) -> None:
        """Validate subreddit configuration."""
        if not self.name:
            raise ValidationError("Subreddit name is required")
        
        valid_filter_types = ['hot', 'new', 'top', 'rising']
        if self.filter_type not in valid_filter_types:
            raise ValidationError(f"Invalid filter type. Must be one of: {', '.join(valid_filter_types)}")
        
        if self.filter_type == 'top':
            valid_time_filters = ['all', 'day', 'hour', 'month', 'week', 'year']
            if not self.time_filter or self.time_filter not in valid_time_filters:
                raise ValidationError(f"Time filter is required for top posts. Must be one of: {', '.join(valid_time_filters)}")
        
        if self.limit < 1:
            raise ValidationError("Limit must be greater than 0")
        
        if self.batch_size < 1:
            raise ValidationError("Batch size must be greater than 0")
        
        if self.timeout < 1:
            raise ValidationError("Timeout must be greater than 0")
            
        if self.max_comments < 0:
            raise ValidationError("Max comments must be greater than or equal to 0")

@dataclass
class GlobalConfig:
    """Global configuration settings."""
    output_dir: str = "downloads"
    logging_config: dict = None
    default_batch_size: int = 5
    default_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5

    def __post_init__(self):
        """Set default logging configuration if none provided."""
        if self.logging_config is None:
            self.logging_config = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s - %(levelname)s - %(message)s'
                    },
                },
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'standard',
                        'level': 'INFO',
                    },
                    'file': {
                        'class': 'logging.handlers.RotatingFileHandler',
                        'filename': 'logs/reddit_downloader.log',
                        'formatter': 'standard',
                        'level': 'INFO',
                        'maxBytes': 10485760,  # 10MB
                        'backupCount': 5,
                    },
                },
                'loggers': {
                    '': {
                        'handlers': ['console', 'file'],
                        'level': 'INFO',
                        'propagate': True
                    }
                }
            }

    def validate(self) -> None:
        """Validate global configuration."""
        if not self.output_dir:
            raise ValidationError("Output directory is required")
        if self.default_batch_size < 1:
            raise ValidationError("Default batch size must be greater than 0")
        if self.default_timeout < 1:
            raise ValidationError("Default timeout must be greater than 0")
        if self.max_retries < 0:
            raise ValidationError("Max retries must be greater than or equal to 0")
        if self.retry_delay < 0:
            raise ValidationError("Retry delay must be greater than or equal to 0")