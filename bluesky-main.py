"""Script to post content to Bluesky."""
import os
import shutil
from dotenv import load_dotenv
from atproto import Client
from post_finder import find_post_and_media

def main():
    """Main function to login to Bluesky and post content."""
    # Load environment variables
    load_dotenv()
    
    # Get Bluesky credentials
    bluesky_email = os.getenv('BLUESKY_EMAIL')
    bluesky_password = os.getenv('BLUESKY_APP_PASSWORD')
    
    if not bluesky_email or not bluesky_password:
        print("Error: Bluesky credentials not found in .env file")
        return
    
    client = Client()
    try:
        # Create session
        client.login(bluesky_email, bluesky_password)
        print(f"Successfully logged in as {bluesky_email}")
        
        # Find post content and media
        result = find_post_and_media()
        if not result:
            print("No post content found")
            return
            
        content, media_file = result
        
        if media_file:
            # Upload image and create post with it
            with open(media_file, 'rb') as f:
                img_data = f.read()
                img_upload = client.upload_blob(img_data)
                
                # Create post with embedded image
                embed = {
                    '$type': 'app.bsky.embed.images',
                    'images': [{
                        'alt': 'Post image',
                        'image': img_upload.blob
                    }]
                }
                client.send_post(text=content, embed=embed)
                print(f"Posted content with image: {media_file.name}")
        else:
            # Create text-only post
            client.send_post(text=content)
            print("Posted content without image")
            
        # Clean up downloads directory after successful post
        downloads_dir = "downloads"
        if os.path.exists(downloads_dir):
            shutil.rmtree(downloads_dir)
            os.makedirs(downloads_dir)  # Recreate empty downloads directory
            print("Cleaned up downloads directory")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()