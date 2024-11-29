# Reddit to Bluesky Bot

A Python bot that downloads content from Reddit, generates AI-powered summaries, and posts them to Bluesky. The bot operates in two parts: one script for downloading Reddit content and another for posting to Bluesky.

## Features

- Downloads Reddit posts and comments
- Generates AI summaries using OpenAI's GPT-4
- Downloads associated media files
- Posts summaries and media to Bluesky
- Configurable subreddit settings
- Organized content storage by date

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

### 1. Download Reddit Content

Run the Reddit downloader:
```bash
python reddit-main.py
```

This will:
- Create a date-based directory (YYYY-MM-DD)
- Download posts from configured subreddits
- Generate AI summaries
- Save content to the following files:
  - post-summary.txt: AI-generated summary
  - title.txt: Post title
  - url.txt: Original Reddit URL
  - media/: Downloaded images/videos

### 2. Post to Bluesky

Post the content to Bluesky:
```bash
python bluesky-main.py
```

This will:
- Login to Bluesky using app password
- Find the latest downloaded content
- Post the summary and any media to Bluesky

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
└── reddit_downloader.log
```

## Configuration Files

- `config.yaml`: Global settings
- `subreddits.yaml`: Subreddit-specific settings
- `.env`: API credentials and configuration

## Dependencies

- praw: Reddit API wrapper
- atproto: Bluesky API client
- openai: OpenAI API for summaries
- python-dotenv: Environment variable management
- PyYAML: Configuration parsing

## Notes

- Media downloads are automatic for supported formats (jpg, png, gif)
- Summaries are generated in a casual tone with emojis for Bluesky
- Content is organized by date for easy management
- Detailed logs are available in the logs directory

For more detailed information about the Reddit downloading functionality, see [reddit-readme.md](reddit-readme.md).