import os
import re
from typing import Optional
from src.reddit.exceptions import ValidationError

def validate_subreddit_name(name: str) -> None:
    """Validate subreddit name format."""
    if not name:
        raise ValidationError("Subreddit name is required")
    
    # Reddit subreddit naming rules
    if not re.match(r'^[A-Za-z0-9][A-Za-z0-9_]{2,20}$', name):
        raise ValidationError(
            "Invalid subreddit name. Must be 3-21 characters, "
            "start with letter/number, and contain only letters, numbers, or underscores"
        )

def validate_filter_type(filter_type: str) -> None:
    """Validate post filter type."""
    valid_types = ['hot', 'new', 'top', 'rising']
    if filter_type not in valid_types:
        raise ValidationError(f"Invalid filter type. Must be one of: {', '.join(valid_types)}")

def validate_time_filter(time_filter: Optional[str], filter_type: str) -> None:
    """Validate time filter for top posts."""
    if filter_type == 'top':
        if not time_filter:
            raise ValidationError("Time filter is required for top posts")
        
        valid_filters = ['all', 'day', 'hour', 'month', 'week', 'year']
        if time_filter not in valid_filters:
            raise ValidationError(f"Invalid time filter. Must be one of: {', '.join(valid_filters)}")

def validate_limit(limit: int) -> None:
    """Validate post limit."""
    if not isinstance(limit, int):
        raise ValidationError("Limit must be an integer")
    if limit < 1:
        raise ValidationError("Limit must be at least 1")
    if limit > 100:
        raise ValidationError("Limit cannot exceed 100 posts")

def validate_output_directory(path: str) -> None:
    """Validate output directory path."""
    if not path:
        raise ValidationError("Output directory path is required")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Check if directory is writable
        test_file = os.path.join(path, '.test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except (IOError, OSError) as e:
            raise ValidationError(f"Output directory is not writable: {str(e)}")
            
    except Exception as e:
        raise ValidationError(f"Invalid output directory: {str(e)}")

def validate_batch_size(batch_size: int) -> None:
    """Validate comment processing batch size."""
    if not isinstance(batch_size, int):
        raise ValidationError("Batch size must be an integer")
    if batch_size < 1:
        raise ValidationError("Batch size must be at least 1")
    if batch_size > 100:
        raise ValidationError("Batch size cannot exceed 100")

def validate_timeout(timeout: int) -> None:
    """Validate operation timeout."""
    if not isinstance(timeout, int):
        raise ValidationError("Timeout must be an integer")
    if timeout < 1:
        raise ValidationError("Timeout must be at least 1 second")
    if timeout > 300:  # 5 minutes max
        raise ValidationError("Timeout cannot exceed 300 seconds (5 minutes)")

def validate_file_path(path: str) -> None:
    """Validate file path for writing."""
    if not path:
        raise ValidationError("File path is required")
    
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        # Check if path is writable
        try:
            with open(path, 'a') as f:
                pass
        except (IOError, OSError) as e:
            raise ValidationError(f"File path is not writable: {str(e)}")
            
    except Exception as e:
        raise ValidationError(f"Invalid file path: {str(e)}")

def validate_media_type(content_type: str) -> None:
    """Validate media content type."""
    valid_types = [
        'image/jpeg', 'image/png', 'image/gif',
        'video/mp4', 'video/webm',
        'application/octet-stream'  # For unknown types
    ]
    
    if content_type and content_type.lower() not in valid_types:
        raise ValidationError(f"Invalid media type: {content_type}")

def validate_url(url: str) -> None:
    """Validate URL format."""
    if not url:
        raise ValidationError("URL is required")
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        raise ValidationError("Invalid URL format")