"""Reddit client for fetching posts."""
from typing import List, Optional, Dict, Any
import os
import re
import requests
import shutil
import logging
from datetime import datetime
from urllib.parse import urlparse
import praw
import yt_dlp
from openai import OpenAI

from .config import RedditCredentials, SubredditConfig, GlobalConfig
from .models import RedditPost, DownloadResult
from .exceptions import (
    InvalidCredentialsError,
    SubredditNotFoundError,
    InvalidFilterTypeError,
    InvalidTimeFilterError,
    DownloadError
)

class RedditHandler:
    """Handler for Reddit content downloading operations."""
    
    def __init__(self):
        """Initialize the Reddit handler with credentials from environment."""
        self.logger = logging.getLogger('reddit_handler')
        self.logger.info("Initializing Reddit API connection")
        
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'Python:ContentDownloader:v1.0')
            )
            self.logger.info("Successfully initialized Reddit API connection")
            
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.logger.info("Successfully initialized OpenAI client")
            
            # Configure yt-dlp
            self.ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit: {str(e)}")
            raise InvalidCredentialsError(f"Failed to initialize Reddit: {str(e)}")

    def _generate_summary(self, title: str, comments: str) -> str:
        """Generate a summary of the post using OpenAI."""
        try:
            # Modified prompt to ensure shorter output
            prompt = f"""Write a very brief 1-2 sentence summary (max 250 characters) of this reddit post and its comments. 
            Add 1-2 relevant emojis at the end. Keep it casual and engaging.
            Don't mention reddit or subreddits.

            Title: {title}

            Comments: {comments}"""
            
            completion = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes very concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100  # Limit token count to ensure shorter response
            )
            
            summary = completion.choices[0].message.content.strip()
            # Ensure summary is within Bluesky's limit
            if len(summary) > 250:
                summary = summary[:247] + "..."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            # Return truncated title as fallback
            return f"{title[:247]}..." if len(title) > 250 else title

    def _get_date_based_dir(self, base_dir: str) -> str:
        """Get date-based directory path."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        date_dir = os.path.join(base_dir, current_date)
        os.makedirs(date_dir, exist_ok=True)
        return date_dir

    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is from YouTube."""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+'
        ]
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    def _is_imgur_url(self, url: str) -> bool:
        """Check if URL is from Imgur."""
        return 'imgur.com' in url
    
    def _is_redgifs_url(self, url: str) -> bool:
        """Check if URL is from Redgifs."""
        redgifs_patterns = [
            r'(?:https?://)?(?:www\.)?redgifs\.com/watch/[\w-]+',
            r'(?:https?://)?(?:www\.)?redgifs\.com/i/[\w-]+'
        ]
        return any(re.match(pattern, url) for pattern in redgifs_patterns) or 'redgifs.com' in url

    def _download_with_yt_dlp(self, url: str, output_dir: str, post_id: str) -> Optional[str]:
        """Download media using yt-dlp."""
        try:
            output_template = os.path.join(output_dir, f"{post_id}.%(ext)s")
            ydl_opts = {
                **self.ydl_opts,
                'outtmpl': output_template
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info.get('ext'):
                    filename = f"{post_id}.{info['ext']}"
                    return os.path.join(output_dir, filename)
        except Exception as e:
            self.logger.error(f"Error downloading with yt-dlp: {str(e)}")
        return None

    def get_subreddit_posts(self, config: SubredditConfig) -> List[RedditPost]:
        """Get posts from a subreddit based on configuration."""
        self.logger.info(f"Fetching posts from r/{config.name}")
        
        try:
            subreddit = self.reddit.subreddit(config.name)
            
            # Get posts based on filter type
            if config.filter_type == 'hot':
                posts = subreddit.hot(limit=config.limit)
            elif config.filter_type == 'new':
                posts = subreddit.new(limit=config.limit)
            elif config.filter_type == 'top':
                if not config.time_filter:
                    raise InvalidTimeFilterError("Time filter is required for top posts")
                posts = subreddit.top(time_filter=config.time_filter, limit=config.limit)
            elif config.filter_type == 'rising':
                posts = subreddit.rising(limit=config.limit)
            else:
                raise InvalidFilterTypeError(f"Invalid filter type: {config.filter_type}")
            
            # Convert PRAW submissions to our RedditPost model
            reddit_posts = []
            for post in posts:
                self.logger.info(f"Converting submission {post.id}")
                reddit_post = self._convert_submission_to_post(post, config)
                reddit_posts.append(reddit_post)
            
            self.logger.info(f"Found {len(reddit_posts)} posts")
            return reddit_posts
            
        except praw.exceptions.PRAWException as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            raise SubredditNotFoundError(f"Error accessing subreddit: {str(e)}")

    def download_content(self, post: RedditPost, output_dir: str, config: SubredditConfig) -> DownloadResult:
        """Download post content including media and comments."""
        # Create date-based directory
        date_dir = self._get_date_based_dir(output_dir)
        post_dir = os.path.join(date_dir, f"{post.subreddit}_{post.id}")
        os.makedirs(post_dir, exist_ok=True)
        
        downloaded_files = []
        errors = []
        has_media = False
        
        try:
            # Save post information
            post_info_path = os.path.join(post_dir, "post_info.txt")
            with open(post_info_path, 'w', encoding='utf-8') as f:
                f.write(f"Title: {post.title}\n")
                f.write(f"Author: {post.author}\n")
                f.write(f"Created: {post.created_utc}\n")
                f.write(f"Score: {post.score}\n")
                f.write(f"URL: {post.url}\n\n")
                if post.selftext:
                    f.write("Content:\n")
                    f.write(post.selftext)
            downloaded_files.append(post_info_path)
            
            # Save title to separate file
            title_path = os.path.join(post_dir, "title.txt")
            with open(title_path, 'w', encoding='utf-8') as f:
                f.write(post.title)
            downloaded_files.append(title_path)
            
            # Save URL to separate file
            url_path = os.path.join(post_dir, "url.txt")
            with open(url_path, 'w', encoding='utf-8') as f:
                f.write(post.url)
            downloaded_files.append(url_path)
            
            # Save comments if enabled
            if config.download_comments and post.comments:
                comments_path = os.path.join(post_dir, "comments.txt")
                comments_content = ""
                with open(comments_path, 'w', encoding='utf-8') as f:
                    for comment in post.comments:
                        comment_text = f"Author: {comment['author']}\n"
                        comment_text += f"Created: {comment['created_utc']}\n"
                        comment_text += f"Score: {comment['score']}\n"
                        comment_text += "Content:\n"
                        comment_text += comment['body']
                        comment_text += "\n\n" + "-"*80 + "\n\n"
                        f.write(comment_text)
                        comments_content += comment_text
                downloaded_files.append(comments_path)
                
                # Generate and save summary using OpenAI
                summary = self._generate_summary(post.title, comments_content)
                summary_path = os.path.join(post_dir, "post-summary.txt")
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                downloaded_files.append(summary_path)
            
            # Download media if present
            if post.url:
                media_dir = os.path.join(post_dir, "media")
                os.makedirs(media_dir, exist_ok=True)
                
                try:
                    # Handle special media types first
                    if (self._is_youtube_url(post.url) or 
                        self._is_imgur_url(post.url) or 
                        self._is_redgifs_url(post.url)):
                        file_path = self._download_with_yt_dlp(post.url, media_dir, post.id)
                        if file_path:
                            downloaded_files.append(file_path)
                            has_media = True
                    # Handle standard media types
                    elif self._is_image_url(post.url):
                        file_path = self._download_image(post.url, media_dir, post.id)
                        if file_path:
                            downloaded_files.append(file_path)
                            has_media = True
                    elif self._is_gallery(post):
                        gallery_files = self._download_gallery(post, media_dir)
                        if gallery_files:
                            downloaded_files.extend(gallery_files)
                            has_media = True
                    elif self._is_video(post.url):
                        file_path = self._download_video(post.url, media_dir, post.id)
                        if file_path:
                            downloaded_files.append(file_path)
                            has_media = True
                except Exception as e:
                    self.logger.error(f"Error downloading media: {str(e)}")
                    errors.append(f"Media download error: {str(e)}")
            
            # Handle skip_no_media flag
            if config.skip_no_media and not has_media:
                self.logger.info(f"No media found for post {post.id}, removing directory")
                shutil.rmtree(post_dir)
                return DownloadResult(success=True, downloaded_files=[], errors=[])
            
            return DownloadResult(success=True, downloaded_files=downloaded_files, errors=errors)
            
        except Exception as e:
            self.logger.error(f"Error downloading content: {str(e)}")
            # Clean up directory if no media and skip_no_media is True
            if config.skip_no_media and not has_media and os.path.exists(post_dir):
                shutil.rmtree(post_dir)
            return DownloadResult(success=False, downloaded_files=downloaded_files, errors=[str(e)])

    def _convert_submission_to_post(self, submission: Any, config: SubredditConfig) -> RedditPost:
        """Convert a PRAW submission to our RedditPost model."""
        self.logger.info(f"Processing submission {submission.id}")
        
        # Process comments only if enabled and max_comments > 0
        comments = []
        if config.download_comments and config.max_comments > 0:
            self.logger.info(f"Processing comments for submission {submission.id}")
            submission.comments.replace_more(limit=0)  # Remove MoreComments objects
            
            # Get all top-level comments and sort by score
            all_comments = [
                comment for comment in submission.comments.list()
                if not comment.stickied  # Skip stickied comments
            ]
            all_comments.sort(key=lambda x: x.score, reverse=True)  # Sort by score descending
            
            # Take only the top N comments
            top_comments = all_comments[:config.max_comments]
            self.logger.info(f"Processing {len(top_comments)} top comments")
            
            for comment in top_comments:
                try:
                    comments.append({
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'score': comment.score
                    })
                except Exception as e:
                    self.logger.error(f"Error processing comment: {str(e)}")
            
            self.logger.info(f"Processed {len(comments)} comments")
        
        return RedditPost(
            id=submission.id,
            title=submission.title,
            author=str(submission.author) if submission.author else '[deleted]',
            created_utc=datetime.fromtimestamp(submission.created_utc),
            score=submission.score,
            url=submission.url,
            selftext=submission.selftext,
            subreddit=submission.subreddit.display_name,
            comments=comments,
            is_gallery=hasattr(submission, 'is_gallery') and submission.is_gallery,
            gallery_data=submission.gallery_data if hasattr(submission, 'gallery_data') else None
        )

    def _is_image_url(self, url: str) -> bool:
        """Check if URL points to an image."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        parsed_url = urlparse(url)
        return any(parsed_url.path.lower().endswith(ext) for ext in image_extensions)

    def _is_gallery(self, post: RedditPost) -> bool:
        """Check if post is a gallery."""
        return post.is_gallery and post.gallery_data is not None

    def _is_video(self, url: str) -> bool:
        """Check if URL points to a video."""
        video_extensions = ['.mp4', '.webm', '.mov']
        parsed_url = urlparse(url)
        return any(parsed_url.path.lower().endswith(ext) for ext in video_extensions)

    def _download_image(self, url: str, output_dir: str, post_id: str) -> Optional[str]:
        """Download an image file."""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                ext = self._get_extension_from_content_type(content_type)
                if not ext:
                    ext = os.path.splitext(urlparse(url).path)[1]
                if not ext:
                    ext = '.jpg'
                
                filename = f"{post_id}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                return filepath
        except Exception as e:
            self.logger.error(f"Error downloading image: {str(e)}")
        return None

    def _download_gallery(self, post: RedditPost, output_dir: str) -> List[str]:
        """Download all images from a gallery post."""
        downloaded_files = []
        try:
            if post.gallery_data:
                for item in post.gallery_data['items']:
                    media_id = item['media_id']
                    url = f"https://i.redd.it/{media_id}.jpg"
                    file_path = self._download_image(url, output_dir, f"{post.id}_{media_id}")
                    if file_path:
                        downloaded_files.append(file_path)
        except Exception as e:
            self.logger.error(f"Error downloading gallery: {str(e)}")
        return downloaded_files

    def _download_video(self, url: str, output_dir: str, post_id: str) -> Optional[str]:
        """Download a video file."""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                ext = os.path.splitext(urlparse(url).path)[1]
                if not ext:
                    ext = '.mp4'
                
                filename = f"{post_id}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                return filepath
        except Exception as e:
            self.logger.error(f"Error downloading video: {str(e)}")
        return None

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type."""
        content_type = content_type.lower()
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'
        elif 'mp4' in content_type:
            return '.mp4'
        elif 'webm' in content_type:
            return '.webm'
        return ''
