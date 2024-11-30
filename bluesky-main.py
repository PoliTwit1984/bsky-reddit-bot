"""Script to post content to Bluesky."""
import os
import sys
import shutil
import logging
from dotenv import load_dotenv
from atproto import Client
from post_finder import find_post_and_media
from PIL import Image
from io import BytesIO

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bluesky.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

def process_image(image_path):
    """Process image for Bluesky upload."""
    try:
        logger.info(f"Processing image: {image_path}")
        with Image.open(image_path) as img:
            # Convert to RGB mode if needed
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Calculate dimensions to maintain 16:9 aspect ratio
            target_width = 1200  # Bluesky recommended width
            target_height = int(target_width * (9/16))  # 16:9 ratio

            # Create new image with correct aspect ratio
            new_img = Image.new('RGB', (target_width, target_height), 'white')

            # Resize original image while maintaining aspect ratio
            if img.width / img.height > 16/9:  # Image is wider than 16:9
                new_height = int(target_width / (img.width / img.height))
                resized = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
                y_offset = (target_height - new_height) // 2
                new_img.paste(resized, (0, y_offset))
            else:  # Image is taller than 16:9
                new_width = int(target_height * (img.width / img.height))
                resized = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                x_offset = (target_width - new_width) // 2
                new_img.paste(resized, (x_offset, 0))

            # Convert to bytes
            img_byte_arr = BytesIO()
            new_img.save(img_byte_arr, format='JPEG', quality=85)
            logger.info("Successfully processed image")
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return None

def cleanup_downloads():
    """Clean up downloads directory."""
    try:
        downloads_dir = "downloads"
        if os.path.exists(downloads_dir):
            shutil.rmtree(downloads_dir)
            os.makedirs(downloads_dir)  # Recreate empty downloads directory
            logger.info("Cleaned up downloads directory")
    except Exception as e:
        logger.error(f"Error cleaning up downloads directory: {str(e)}")
        raise  # Re-raise the exception to ensure it's logged in the scheduler

def main():
    """Main function to login to Bluesky and post content."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get Bluesky credentials
        bluesky_email = os.getenv('BLUESKY_EMAIL')
        bluesky_password = os.getenv('BLUESKY_APP_PASSWORD')
        
        if not bluesky_email or not bluesky_password:
            logger.error("Bluesky credentials not found in .env file")
            raise ValueError("Missing Bluesky credentials")
        
        client = Client()
        try:
            # Create session
            client.login(bluesky_email, bluesky_password)
            logger.info(f"Successfully logged in as {bluesky_email}")
            
            # Find post content and media
            result = find_post_and_media()
            if not result:
                logger.info("No post content found")
                return
                
            content, media_file = result
            logger.info(f"Found content and media: {bool(media_file)}")
            
            if media_file:
                logger.info(f"Processing image: {media_file.name}")
                
                # Process the image
                img_data = process_image(media_file)
                if not img_data:
                    logger.error("Failed to process image")
                    raise RuntimeError("Image processing failed")

                try:
                    # Upload image - fixed to use correct API
                    img_upload = client.upload_blob(img_data)
                    logger.info("Successfully uploaded image")

                    # Create post with image
                    embed = {
                        '$type': 'app.bsky.embed.images',
                        'images': [{
                            'alt': 'Post image',
                            'image': img_upload.blob,
                            'aspectRatio': {
                                'width': 1200,
                                'height': 675
                            }
                        }]
                    }
                    
                    # Attempt to create post
                    response = client.send_post(text=content, embed=embed)
                    if response and hasattr(response, 'uri'):
                        logger.info(f"Successfully created post: {response.uri}")
                    else:
                        logger.error("Failed to create post - no URI in response")
                        raise RuntimeError("Post creation failed")
                except Exception as e:
                    logger.error(f"Error creating post: {str(e)}")
                    raise
            else:
                # Create text-only post
                try:
                    response = client.send_post(text=content)
                    if response and hasattr(response, 'uri'):
                        logger.info(f"Successfully created text post: {response.uri}")
                    else:
                        logger.error("Failed to create text post - no URI in response")
                        raise RuntimeError("Text post creation failed")
                except Exception as e:
                    logger.error(f"Error creating text post: {str(e)}")
                    raise
            
            # Clean up downloads directory after successful post
            cleanup_downloads()
            
        except Exception as e:
            logger.error(f"Error during Bluesky operations: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise  # Re-raise to ensure the scheduler sees the error

if __name__ == '__main__':
    main()
