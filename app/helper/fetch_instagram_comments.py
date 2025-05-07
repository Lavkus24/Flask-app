
import time
from app.utils.setup_driver import setup_driver
from .navigate_to_post import navigate_to_post
from .get_comment_container_with_exact_xpath import get_comments_container_with_exact_xpath
from .scroll_comments_container import scroll_comments_container
from .extract_comment_from_container import extract_comments_from_container
from .save_comments_to_file import save_comments_to_file






def fetch_instagram_comments(post_id):
    # URL of the Instagram post you want to scrape
    post_url = f"https://www.instagram.com/p/{post_id}"  # Replace with your target post URL

    # match = re.search(r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)", post_url)
    # post_id = match.group(1) if match else None

    print(f"post_id : {post_id}")
    
    driver = None
    try:
        # Setup driver with session ID login
        driver = setup_driver()
        
        if driver:
            # Navigate to the post
            navigate_to_post(driver, post_url)
            
            # Wait a bit longer to ensure the page is fully loaded
            print("Waiting for page to fully load...")
            time.sleep(5)
            
            # Get the comments container
            container = get_comments_container_with_exact_xpath(driver)
            
            if container:
                # Scroll the comments container to load more comments
                scroll_comments_container(driver, container)
                
                # Extract comments from the container
                comments = extract_comments_from_container(driver, container)
                
                # Save comments to file
                comments_data = save_comments_to_file(comments,post_id)

                print(comments_data)

                return comments_data

                
            else:
                print("Could not find comments container, cannot proceed")
                
                # Take a screenshot to help debug
                screenshot_path = "instagram_debug.png"
                driver.save_screenshot(screenshot_path)
                print(f"Saved debug screenshot to {screenshot_path}")
        else:
            print("Failed to set up driver. Check session IDs and try again.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
        # Take a screenshot on error for debugging
        try:
            driver.save_screenshot("instagram_error.png")
            print("Saved error screenshot to instagram_error.png")
        except:
            pass
    
    finally:
        # Always close the driver
        if driver:
            print("Closing browser...")
            driver.quit()