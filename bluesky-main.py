"""Script to post content to Bluesky."""
import os
import shutil
from dotenv import load_dotenv
from atproto import Client
from post_finder import find_post_and_media
from PIL import Image
from io import BytesIO




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
            print(f"\n=== Processing image: {media_file.name} ===")

            with Image.open(media_file) as img:
                # Convert to RGB mode if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # Calculate dimensions to maintain 16:9 aspect ratio
                target_width = 1200  # Bluesky recommended width
                target_height = int(target_width * (9/16))  # 16:9 ratio

                # Create new image with correct aspect ratio
                new_img = Image.new('RGB', (target_width, target_height), 'white')

                # Resize original image while maintaining aspect ratio
                if img.width > target_width:
                    ratio = target_width / img.width
                    new_size = (target_width, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Center the image in the 16:9 frame
                x_offset = (target_width - img.width) // 2
                y_offset = (target_height - img.height) // 2
                new_img.paste(img, (x_offset, y_offset))

                # Convert to bytes
                img_byte_arr = BytesIO()
                new_img.save(img_byte_arr, format='JPEG', quality=85)
                img_data = img_byte_arr.getvalue()

                # Upload and create post
                img_upload = client.upload_blob(img_data)
                embed = {
                    '$type': 'app.bsky.embed.images',
                    'images': [{
                        'alt': 'Post image',
                        'image': img_upload.blob,
                        'aspectRatio': {
                            'width': 1200,  # recommended width
                            'height': 675   # 16:9 ratio
                        }
                    }]
                }
                # embed = {
                #     '$type': 'app.bsky.embed.images',
                #     'images': [{
                #         'alt': 'Post image',
                #         'image': img_upload.blob
                #     }]
                # }
                client.send_post(text=content, embed=embed)
            
        # Clean up downloads directory after successful post
        downloads_dir = "downloads"
        if os.path.exists(downloads_dir):
            shutil.rmtree(downloads_dir)
            os.makedirs(downloads_dir)  # Recreate empty downloads directory
            print("Cleaned up downloads directory")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error occurred during image processing")

if __name__ == "__main__":
    main()
