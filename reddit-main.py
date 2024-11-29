import os
import yaml
import logging
import logging.config
from typing import Dict, Any
from dotenv import load_dotenv

from src.reddit.config import RedditCredentials, SubredditConfig, GlobalConfig
from src.reddit.handler import RedditHandler
from src.reddit.exceptions import ValidationError

def load_config(config_path: str = "config.yaml", subreddits_path: str = "subreddits.yaml") -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load configuration from YAML files.
    
    Returns:
        tuple: (global_config_data, subreddits_config_data)
    """
    # Load global configuration
    with open(config_path, 'r') as f:
        global_config = yaml.safe_load(f)
    
    # Load subreddit configurations
    with open(subreddits_path, 'r') as f:
        subreddits_config = yaml.safe_load(f)
    
    return global_config, subreddits_config

def setup_logging(config: GlobalConfig) -> None:
    """Set up logging configuration."""
    os.makedirs('logs', exist_ok=True)
    logging.config.dictConfig(config.logging_config)

def main() -> None:
    """Main entry point for the Reddit content downloader."""
    # Load environment variables
    load_dotenv()
    
    # Initialize logging with basic configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger()
    logger.info("Starting Reddit content downloader")
    
    try:
        # Load configurations
        logger.info("Loading configuration")
        global_config_data, subreddits_config = load_config()
        
        # Create and validate global configuration
        global_config = GlobalConfig(**global_config_data.get('settings', {}))
        global_config.validate()
        
        # Set up logging with full configuration
        setup_logging(global_config)
        
        # Create and validate Reddit credentials
        credentials = RedditCredentials(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'Python:ContentDownloader:v1.0')
        )
        credentials.validate()
        
        # Initialize Reddit handler
        logger.info("Initializing Reddit handler")
        handler = RedditHandler()
        
        # Process each subreddit configuration
        logger.info("Validating configuration")
        subreddits = []
        for subreddit_data in subreddits_config.get('subreddits', []):
            try:
                logger.info(f"Validating configuration for subreddit: {subreddit_data.get('name')}")
                subreddit_config = SubredditConfig(**subreddit_data)
                subreddit_config.validate()
                subreddits.append(subreddit_config)
                logger.info(f"Configuration for subreddit {subreddit_data.get('name')} is valid")
            except ValidationError as e:
                logger.error(f"Invalid configuration for subreddit {subreddit_data.get('name')}: {str(e)}")
                continue
        
        # Process each subreddit
        for config in subreddits:
            logger.info(f"Processing subreddit: r/{config.name}")
            logger.info(f"Filter: {config.filter_type}, Time Filter: {config.time_filter}, Limit: {config.limit}")
            
            try:
                # Get posts
                posts = handler.get_subreddit_posts(config)
                logger.info(f"Found {len(posts)} posts")
                
                # Download content for each post
                for i, post in enumerate(posts, 1):
                    logger.info(f"Processing post {i}/{len(posts)}: {post.title[:50]}...")
                    try:
                        # Pass both post and config to download_content
                        result = handler.download_content(post, global_config.output_dir, config)
                        if result.success:
                            if result.downloaded_files:
                                logger.info(f"Successfully downloaded {len(result.downloaded_files)} files")
                                for file in result.downloaded_files:
                                    logger.debug(f"Downloaded: {file}")
                            else:
                                logger.info("No files to download")
                        else:
                            logger.warning("Errors occurred while downloading:")
                            for error in result.errors:
                                logger.error(f"  {error}")
                    except Exception as e:
                        logger.error(f"Error downloading content: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"Error processing subreddit r/{config.name}: {str(e)}")
                continue
        
        logger.info("Download completed!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()