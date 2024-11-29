class RedditBaseException(Exception):
    """Base exception class for Reddit-related errors."""
    pass

class InvalidCredentialsError(RedditBaseException):
    """Raised when Reddit API credentials are invalid."""
    pass

class SubredditNotFoundError(RedditBaseException):
    """Raised when a subreddit cannot be found or accessed."""
    pass

class InvalidFilterTypeError(RedditBaseException):
    """Raised when an invalid filter type is specified."""
    pass

class InvalidTimeFilterError(RedditBaseException):
    """Raised when an invalid time filter is specified for top posts."""
    pass

class DownloadError(RedditBaseException):
    """Raised when there's an error downloading content."""
    pass

class ValidationError(RedditBaseException):
    """Raised when configuration validation fails."""
    pass