import instaloader
import re
import os
import shutil



def get_profile_picture(username):
    try:
        print("Profile Picture")
        # Clean username
        if username.startswith('@'):
            username = username[1:]
        
        if '/' in username or '.' in username:
            username_match = re.search(r'instagram\.com/([^/]+)/?', username)
            if username_match:
                username = username_match.group(1)

        print(f"Downloading profile picture for username: {username}")
        
        # Initialize instaloader
        L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

        temp_dir = "temp_instagram_download"
        os.makedirs(temp_dir, exist_ok=True)
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            profile = instaloader.Profile.from_username(L.context, username)
            L.download_profilepic(profile)
            print(f"Successfully downloaded profile picture for {username}")
            success = True
        except Exception as e:
            print(f"Error downloading profile picture: {e}")
            success = False

        os.chdir(original_dir)

        if success:
            # Recursively walk through downloaded files
            all_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(('.jpg', '.jpeg', '.png')):
                        full_path = os.path.join(root, file)
                        all_files.append(full_path)

            print("Found profile pics:", all_files)

            # Sort files by last modified time (latest first)
            if all_files:
                sorted_files = sorted(all_files, key=os.path.getmtime, reverse=True)
                source_path = sorted_files[0]

                output_path = f"{username}_profile_pic.jpg"
                shutil.copy2(source_path, output_path)
                print(f"Profile picture saved as {output_path}")

                shutil.rmtree(temp_dir)
                return output_path  # ✅ Return full path to the copied image
            else:
                print("Could not find downloaded profile picture")
                shutil.rmtree(temp_dir)
                return None

        return None

    except Exception as e:
        print(f"Error processing Instagram profile: {e}")
        return None