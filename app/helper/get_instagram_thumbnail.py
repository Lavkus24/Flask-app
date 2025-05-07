import re
import os
import shutil
import instaloader

def get_instagram_thumbnail(post_url):
    try:
        # Extract shortcode from URL
        shortcode_match = re.search(r'/p/([^/]+)/', post_url)
        if not shortcode_match:
            print("Could not extract post shortcode from URL")
            return False
            
        shortcode = shortcode_match.group(1)
        print(f"Extracted post shortcode: {shortcode}")
            
        # Initialize instaloader
        L = instaloader.Instaloader(
            download_pictures=True,
            download_videos=False,
            download_video_thumbnails=True,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            filename_pattern="{shortcode}"
        )
            
        # Download the post by shortcode
        post = instaloader.Post.from_shortcode(L.context, shortcode)
            
        # Create a temporary directory for the download
        temp_dir = "temp_instagram_download"
        os.makedirs(temp_dir, exist_ok=True)
            
        # Change to the temporary directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
            
        # Download only the post
        try:
            L.download_post(post, target=shortcode)
            print(f"Successfully downloaded thumbnail for post {shortcode}")
            success = True
        except Exception as e:
            print(f"Error downloading post: {e}")
            success = False
            
        # Change back to the original directory
        os.chdir(original_dir)
            
        if success:
            # Find the downloaded image file
            downloaded_files = os.listdir(os.path.join(temp_dir, shortcode))
            image_files = [f for f in downloaded_files if f.endswith(('.jpg', '.jpeg', '.png'))]
                
            if image_files:
                source_path = os.path.join(temp_dir, shortcode, image_files[0])
                output_path = f"{shortcode}_thumbnail.jpg"
                            
                # Copy the file to the desired location
                shutil.copy2(source_path, output_path)
                print(f"Thumbnail saved as {output_path}")
                            
                # Clean up temporary directory
                shutil.rmtree(temp_dir)
                return True
            else:
                print("Could not find downloaded image files")
                return False
                
        return success
        
    except Exception as e:
        print(f"Error processing Instagram post: {e}")
        return False