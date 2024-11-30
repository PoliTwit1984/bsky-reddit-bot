# Reddit to Bluesky Bot

A Python bot that downloads content from Reddit, generates AI-powered summaries, and posts them to Bluesky. The bot operates in two parts: one script for downloading Reddit content and another for posting to Bluesky, with a scheduler that runs both scripts periodically.

## Features

- Downloads Reddit posts and comments
- Generates AI summaries using OpenAI's GPT-4o (optimized for Bluesky's character limits)
- Downloads associated media files
- Posts summaries and media to Bluesky with proper aspect ratios
- Configurable subreddit settings
- Organized content storage by date
- Automatic scheduling of content downloads and posts

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

# Bluesky Credentials
BLUESKY_EMAIL=your.handle.bsky.social
BLUESKY_APP_PASSWORD=your-app-password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

3. Configure subreddits in `subreddits.yaml`:
```yaml
subreddits:
  - name: "subreddit_name"
    filter_type: "hot"  # hot, new, top, rising
    time_filter: "day"  # required for top posts
    limit: 5
    download_comments: true
    max_comments: 5
```

## Usage

### Running the Scheduler

Run the main scheduler which handles both Reddit downloads and Bluesky posts:
```bash
python main.py
```

This will:
1. Download content from Reddit
2. Generate AI summaries (optimized for Bluesky's 300 character limit)
3. Post content to Bluesky
4. Clean up downloaded content after successful posting

### Manual Operation

You can also run the scripts individually:

1. Download Reddit Content:
```bash
python reddit-main.py
```

2. Post to Bluesky:
```bash
python bluesky-main.py
```

## Directory Structure

```
downloads/
├── YYYY-MM-DD/
│   └── subreddit_postid/
│       ├── post-summary.txt
│       ├── title.txt
│       ├── url.txt
│       └── media/
│           └── downloaded files
logs/
├── reddit_downloader.log
├── bluesky.log
└── scheduler.log
```

## Configuration Files

- `config.yaml`: Global settings
- `subreddits.yaml`: Subreddit-specific settings
- `.env`: API credentials and configuration

## Content Processing

### Summary Generation
- Uses OpenAI's GPT-4o model
- Generates summaries under 250 characters (for Bluesky's 300 character limit)
- Includes relevant emojis
- Maintains casual, engaging tone

### Image Processing
- Automatically processes images to 16:9 aspect ratio
- Centers and crops images appropriately
- Optimizes quality for Bluesky's requirements
- Handles various input formats (jpg, png, gif)

## Dependencies

- praw: Reddit API wrapper
- atproto: Bluesky API client
- openai: OpenAI API for summaries
- python-dotenv: Environment variable management
- PyYAML: Configuration parsing
- Pillow: Image processing
- yt-dlp: Media download support

## Notes

- Media downloads are automatic for supported formats
- Summaries are optimized for Bluesky's character limits
- Images are processed to maintain proper aspect ratios
- Content is organized by date for easy management
- Detailed logs are available in the logs directory
- Automatic cleanup after successful posts

For more detailed information about the Reddit downloading functionality, see [reddit-readme.md](reddit-readme.md).
