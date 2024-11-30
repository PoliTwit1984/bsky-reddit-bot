# Reddit Content Downloader

A powerful Python-based tool for downloading content from Reddit, including media files and comments, with AI-powered summaries optimized for Bluesky's character limits.

## Features

### Media Downloads
- Supports multiple media sources:
  - Direct image/video files (jpg, jpeg, png, gif, mp4, webm)
  - YouTube videos (both youtube.com and youtu.be links)
  - Imgur content (single images and albums)
  - Redgifs content (both watch and direct links)
- Automatic media type detection and handling
- Date-based directory organization (YYYY-MM-DD)
- Skip posts without media (configurable)
- Downloads stored in configurable output directory
- Configurable file size limits and type restrictions
- Image processing for Bluesky's aspect ratio requirements

### Comment Handling
- Fetches top comments for each post (configurable per subreddit)
- Comments sorted by score (highest first)
- Skips stickied comments
- Configurable number of comments per post
- Includes:
  - Comment author
  - Comment body
  - Comment score
  - Creation timestamp
- Comment length truncation for readability

### AI-Powered Summaries
- Generates concise summaries using OpenAI's GPT-4o
- Strictly limited to 250 characters for Bluesky compatibility
- Casual tone with emojis
- Summarizes both post title and comments
- 1-2 sentence format for brevity
- Fallback to truncated title if summary generation fails

### Subreddit Configuration
Configuration is managed through `subreddits.yaml`:

```yaml
subreddits:
  - name: "dataisbeautiful"
    filter_type: "hot"
    time_filter: "day"
    limit: 5
    download_comments: true
    max_comments: 5  # Number of top comments to download
    skip_no_media: true  # Skip posts without media
    batch_size: 5
    timeout: 30
```

### Global Settings
Global settings are managed through `config.yaml`:
- Output directory configuration
- Logging settings
- Batch processing options
- Retry mechanisms
- Timeout configurations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
Create a `.env` file with:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
OPENAI_API_KEY=your_openai_api_key
```

3. Configure subreddits:
Edit `subreddits.yaml` to specify which subreddits to monitor and their settings.

## Usage

1. Run the bot:
```bash
python main.py
```

The bot will:
1. Create a date-based directory (YYYY-MM-DD)
2. Fetch posts from configured subreddits
3. Download associated media (images, videos, etc.)
4. Collect specified number of top comments
5. Generate AI-powered summaries (optimized for Bluesky)
6. Store everything in the date-based directory

## Configuration Options

### Subreddit Settings
- `name`: Subreddit name (without r/)
- `filter_type`: How to sort posts (hot, new, top, rising)
- `time_filter`: Time filter for 'top' posts (required for top posts)
- `limit`: Number of posts to fetch
- `download_comments`: Whether to download comments
- `max_comments`: Number of top comments to download
- `skip_no_media`: Skip posts without media
- `batch_size`: Batch processing size
- `timeout`: Operation timeout in seconds

### Media Download Settings
- Supported formats:
  - Images: jpg, jpeg, png, gif
  - Videos: mp4, webm
  - Platform-specific: YouTube, Imgur, Redgifs
- Configurable file size limits
- Automatic file naming based on post ID
- Image processing for Bluesky compatibility

### Comment Settings
- Configurable number of comments per subreddit
- Comments sorted by score (highest first)
- Skip stickied comments
- Customizable comment formatting

### Summary Settings
- Maximum length: 250 characters
- Casual tone with emojis
- 1-2 sentence format
- Fallback to truncated title
- Token limit for OpenAI API

## Output Structure

```
downloads/
├── YYYY-MM-DD/
│   ├── subreddit_postid1/
│   │   ├── post_info.txt
│   │   ├── title.txt
│   │   ├── url.txt
│   │   ├── post-summary.txt
│   │   ├── comments.txt
│   │   └── media/
│   │       └── downloaded files
│   └── subreddit_postid2/
│       ├── post_info.txt
│       ├── title.txt
│       ├── url.txt
│       ├── post-summary.txt
│       ├── comments.txt
│       └── media/
│           └── downloaded files
└── YYYY-MM-DD/
    └── ...

logs/
├── reddit_downloader.log
├── bluesky.log
└── scheduler.log
```

### Output Files
- `post_info.txt`: Contains comprehensive post information
- `title.txt`: Contains only the post title
- `url.txt`: Contains the original Reddit post URL
- `post-summary.txt`: AI-generated summary (250 char max)
- `comments.txt`: Top comments from the post
- `media/`: Directory containing downloaded media files

## Error Handling

- Robust error handling for network issues
- Retry mechanism for failed downloads
- Detailed logging of all operations
- Skip mechanism for problematic posts
- Automatic cleanup of empty directories
- Fallback mechanisms for summary generation
- Character limit enforcement

## Dependencies

- praw: Reddit API wrapper
- yt-dlp: Media download support (YouTube, Imgur, Redgifs)
- python-dotenv: Environment variable management
- PyYAML: Configuration file parsing
- requests: HTTP requests
- typing-extensions: Type hint support
- python-json-logger: Enhanced logging
- openai: OpenAI API integration for summaries
- Pillow: Image processing

## Notes

- Media downloads are handled automatically based on URL type
- Comments are sorted by score and limited to configured amount
- Date-based organization for better content management
- Skip posts without media (configurable)
- All operations are logged for monitoring
- Configuration can be updated without code changes
- Supports both direct media files and platform-specific content
- AI summaries are optimized for Bluesky's character limits
- Images are processed to maintain proper aspect ratios
- Automatic cleanup after successful Bluesky posts
