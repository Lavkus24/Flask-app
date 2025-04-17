from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import random
import requests
from opensearchpy import OpenSearch, helpers
import re
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
import os

user_name = os.getenv("USER_NAME")
user_password = os.getenv("PASSWORD")
host_url = os.getenv("HOST_URL")

client1 = OpenSearch(
    hosts=[host_url],
    http_auth=(user_name, user_password),
)

def is_instagram_session_valid(session_id):
    """Check if an Instagram session ID is valid"""
    try:
        cookies = {
            'sessionid': session_id
        }
        # Make a request to Instagram to verify if the session is valid
        response = requests.get('https://www.instagram.com/', cookies=cookies, allow_redirects=False)
        
        # If the session is valid, Instagram should not redirect us to the login page
        is_valid = response.status_code == 200 and 'login' not in response.url
        return is_valid
    except Exception as e:
        print(f"Error checking session validity: {e}")
        return False

def setup_driver():
    """Set up and configure the Chrome WebDriver with session ID authentication"""
    chrome_options = Options()
    # Uncomment the line below if you want to run Chrome in headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    # Use a fake user agent to avoid detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    
    # Add performance optimization options
    chrome_options.page_load_strategy = 'eager'
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,  # Don't load images
            'plugins': 2,  # Disable plugins
            'popups': 2,  # Disable popups
            'geolocation': 2,  # Disable geolocation
            'notifications': 2,  # Disable notifications
            'auto_select_certificate': 2,  # Disable SSL selection
            'fullscreen': 2,  # Disable fullscreen
            'mouselock': 2,  # Disable mouse lock
            'mixed_script': 2,  # Disable mixed script
            'media_stream': 2,  # Disable media stream
            'media_stream_mic': 2,  # Disable mic
            'media_stream_camera': 2,  # Disable camera
            'protocol_handlers': 2,  # Disable protocol handlers
            'ppapi_broker': 2,  # Disable broker
            'automatic_downloads': 2,  # Disable auto downloads
            'midi_sysex': 2,  # Disable midi
            'push_messaging': 2,  # Disable push
            'ssl_cert_decisions': 2,  # Disable cert decisions
            'metro_switch_to_desktop': 2,  # Disable metro switch
            'protected_media_identifier': 2,  # Disable media identifier
            'app_banner': 2,  # Disable app banner
            'site_engagement': 2,  # Disable engagement
            'durable_storage': 2  # Disable durable storage
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Navigate to Instagram initially
    driver.get("https://www.instagram.com/")
    time.sleep(3)
  
    # List of session IDs to try
    session_ids = [
        '73653041961%3AOQRoxptHUfzx9R%3A15%3AAYfbxIuYC4BTsFLJh0Q_qjCoZugxuQ7Wh4WisnHzwg',

        # '73178258443%3Aded9QXpecC67g1%3A8%3AAYfUWXEHpzL4LkPDvIW3cfIiLI9i7Oxp_dJTZBeBGA',
        # '73770700193%3Ausm8P5QMNAFmp3%3A22%3AAYeH0OZAOtOkIBV8d07lOB-gFlrJJ9KSShMJ6wAguw',
        # '72526559706%3ATTGNNZ39L1u7xD%3A7%3AAYfXxfQQJD7puXgw_HIT3JVfBHauX1qEKn3IVfz8PFw',
        # '73561734336%3ATgcP6lHHGKUJyn%3A24%3AAYfy8gI3TDgH-oUiC6Anc4_rA3zPv44Bnw5ITUZ9bQ',
        # '72491420302%3AVGm3WUTFCa92MB%3A3%3AAYcRFnw9MNzBUWeQ-FYCg_ceEDcVy_Z-hqIHBm-S5w',
        # '73565872976%3An5JPsfYkvVyplm%3A3%3AAYeBvW_C16GNHlJNdwl5N8uybgSQh_GDMWhWt6GBMQ',
        # '73708908925%3AwsE6xq5mzV4AHy%3A13%3AAYcH8_gI5RIri0Mlf9pTX_64pb0pMYWpgE8rTcXjKw',
        # '72730890572%3AM6BOWTpnaRXUZn%3A9%3AAYetHKr1vbHkCmYuuH1hgnA5KupvTQ8Uv8mJ41SwBA',
        # '51317686193%3AAHvdnOhUK9JxH1%3A2%3AAYeudiq6ASkuapFrgWffY7dFPIZIhrThB3nAIvC7Ug',
        # '73565872976%3An5JPsfYkvVyplm%3A3%3AAYeos8FvRSeA7xVtIkTSZG88V7JTIckfvZyrsUFZXw',
        # '73518940261%3ALd4hXprOVmf58E%3A25%3AAYdPeW9PtKUYPfKwORYGNq9HvTJHJmMi5vksJVS62A',
        # '72491420302%3AVGm3WUTFCa92MB%3A3%3AAYdmmRz0k0rzd_Z0eb9QqbPYiFcpgWAE_bxMVhboIA',
        # '51317686193%3AAHvdnOhUK9JxH1%3A2%3AAYcFV_SzP1eSpyBLi0ZW3pfIZlmsDx6PQ4xe11ajQg',
    ]
    
    # Try each session ID until one works
    for session_id in session_ids:
        try:
            # Check if the session ID is valid before trying to use it
            if is_instagram_session_valid(session_id):
                # Add the session ID cookie to the browser
                driver.add_cookie({
                    'name': 'sessionid',
                    'value': session_id,
                    'domain': '.instagram.com',
                    'path': '/'
                })
                
                # Refresh the page to apply the cookies
                driver.refresh()
                
                # Wait briefly to verify login worked
                time.sleep(3)
                
                # Check if login was successful by looking for profile icon or home feed
                try:
                    # Look for elements that indicate successful login
                    if len(driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'profile')]")) > 0 or \
                       len(driver.find_elements(By.XPATH, "//a[contains(@href, '/direct/inbox')]")) > 0:
                        print(f"Successfully logged in with session ID: {session_id[:10]}...")
                        return driver
                except:
                    print(f"Session ID {session_id[:10]}... failed verification check")
            else:
                print(f"Session ID {session_id[:10]}... is invalid")
        except Exception as e:
            print(f"Error with session ID {session_id[:10]}...: {e}")
    
    print("All session IDs failed. Please provide new session IDs.")
    return driver

def navigate_to_post(driver, post_url):
    """Navigate to the Instagram post"""
    print(f"Navigating to: {post_url}")
    driver.get(post_url)
    
    # Wait for the post to load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//article"))
        )
        print("Post loaded successfully")
    except TimeoutException:
        print("Warning: Timeout while waiting for post to load completely")
        
    time.sleep(3)  # Additional wait to ensure content is loaded

def get_comments_container_with_exact_xpath(driver):
    """Get the comments container using multiple approaches"""
    print("Attempting to find comments container...")
    
    # Try multiple selectors to find the comments container
    selectors = [
        # Try the original XPath approach first
        {"type": "xpath", "value": "//*[starts-with(@id, 'mount_')]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]"},
        # Common Instagram comment section CSS selectors
        {"type": "css", "value": "article ul"},
        {"type": "css", "value": "section main ul"},
        {"type": "css", "value": "div._aao9"},  # Instagram class for comments container
        {"type": "css", "value": "article div:nth-child(2) > div:nth-child(2)"},
        # Try to find scrollable containers
        {"type": "js", "value": "return document.querySelector('ul, div').closest('[style*=\"overflow\"]')"}
    ]
    
    for selector in selectors:
        try:
            if selector["type"] == "xpath":
                container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector["value"]))
                )
            elif selector["type"] == "css":
                container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector["value"]))
                )
            elif selector["type"] == "js":
                container = driver.execute_script(selector["value"])
                
            if container and container.is_displayed():
                # Verify this is likely a comments container by checking for common patterns
                container_html = container.get_attribute('outerHTML')
                # Look for common Instagram comment section features
                if ('comment' in container_html.lower() or 
                    'reply' in container_html.lower() or
                    container.tag_name == 'ul' or
                    len(container.find_elements(By.CSS_SELECTOR, "li")) > 2):
                    print(f"Found comments container using selector: {selector['value']}")
                    return container
        except:
            continue
    
    # Last resort: find anything that looks like a comment container
    try:
        # Find all ULs that contain multiple LIs
        uls = driver.find_elements(By.TAG_NAME, "ul")
        for ul in uls:
            lis = ul.find_elements(By.TAG_NAME, "li")
            if len(lis) > 3:  # If UL has multiple LIs, it's likely comments
                print("Found potential comments container (ul with multiple li)")
                return ul
    except:
        pass
    
    print("Could not find comments container with any method")
    return None

def scroll_comments_container(driver, container, max_scrolls=1):
    """Scroll only the comments container, not the entire page"""
    print("Scrolling the comments container...")
    
    # Get initial scroll height
    scroll_height = driver.execute_script("return arguments[0].scrollHeight", container)
    print(f"Initial scroll height: {scroll_height}")
    
    # Track previous scroll positions to detect when we stop moving
    previous_position = 0
    stuck_count = 0
    
    for i in range(max_scrolls):
        # Scroll down slowly
        driver.execute_script("""
            arguments[0].scrollTop += 500;
        """, container)
        
        print(f"Scroll attempt {i+1}/{max_scrolls}")
        time.sleep(2)  # Wait for content to load
        
        # Check current position
        current_position = driver.execute_script("return arguments[0].scrollTop;", container)
        current_height = driver.execute_script("return arguments[0].scrollHeight;", container)
        
        print(f"Position: {current_position}, Height: {current_height}")
        
        # If we're not moving anymore, we might be at the bottom or stuck
        if current_position == previous_position:
            stuck_count += 1
            print(f"Scroll position unchanged (attempt {stuck_count}/3)")
            if stuck_count >= 3:  # If stuck 3 times, try a different approach or break
                print("Scroll appears stuck, trying a different approach...")
                # Try to click "Load more comments" button if exists
                try:
                    load_buttons = driver.find_elements(By.XPATH, 
                        "//span[contains(text(), 'Load more comments') or contains(text(), 'View more comments')]")
                    for button in load_buttons:
                        if button.is_displayed():
                            button.click()
                            print("Clicked 'Load more comments' button")
                            time.sleep(2)
                            stuck_count = 0  # Reset stuck counter
                except:
                    print("No 'Load more comments' button found")
                    break  # Exit loop if we can't scroll or find buttons
        else:
            # Reset stuck counter if we moved
            stuck_count = 0
            previous_position = current_position
    
    print("Finished scrolling comments container")
    return True


def convert_relative_time(relative_str):
    """
    Convert relative time strings like '2d', '5h', '1w' to an actual UTC datetime string.
    Returns ISO 8601 format: '2025-04-14T15:40:00+00:00'
    """
    if not relative_str:
        return None

    match = re.match(r"(\d+)([smhdw])", relative_str.strip().lower())
    if not match:
        return None

    value, unit = match.groups()
    value = int(value)
    now = datetime.now(timezone.utc)

    if unit == 's':  # seconds
        delta = timedelta(seconds=value)
    elif unit == 'm':  # minutes
        delta = timedelta(minutes=value)
    elif unit == 'h':  # hours
        delta = timedelta(hours=value)
    elif unit == 'd':  # days
        delta = timedelta(days=value)
    elif unit == 'w':  # weeks
        delta = timedelta(weeks=value)
    else:
        return None

    timestamp = now - delta
    return timestamp.isoformat()

def extract_comments_from_container(driver, container):
    """Extract comments using more specific Instagram selectors"""
    print("Extracting comments with improved selectors...")
    comments = []
    
    # Try different approaches to find comment elements
    approaches = [
        # Approach 1: Direct selector for comment li elements
        lambda: container.find_elements(By.CSS_SELECTOR, "ul > li"),
        
        # Approach 2: Look for comments by text content structure
        lambda: driver.find_elements(By.XPATH, "//div[contains(@role, 'button') and .//span]"),
        
        # Approach 3: Find elements with username and text structure
        lambda: driver.find_elements(By.CSS_SELECTOR, "span._aacl._aaco._aacu._aacx._aad7._aade")
    ]
    
    # Try each approach until we find comments
    for approach_func in approaches:
        try:
            comment_elements = approach_func()
            print(f"Found {len(comment_elements)} potential comment elements")
            
            if comment_elements and len(comment_elements) > 0:
                # Use a more specific extraction approach using JavaScript
                for i, comment_elem in enumerate(comment_elements[:200]):  # Limit to 200 to prevent long runtime
                    try:
                        # Use JavaScript to extract data in a more flexible way
                        comment_data = driver.execute_script("""
                            const el = arguments[0];
                            
                            // Instagram specific approach
                            // Try to find the username element using Instagram's specific structure
                            let usernameEl = el.querySelector('a span, a h2, h2 a, h3, a, span a');
                            if (!usernameEl && el.querySelector('a')) {
                                usernameEl = el.querySelector('a'); // Fallback to any link
                            }
                            
                            // Get username text
                            const username = usernameEl ? usernameEl.textContent.trim() : '';
                            
                            // Extract all text to find the comment
                            let fullText = el.textContent.trim();
                            
                            // Get main comment text (skip username part if found)
                            let commentText = fullText;
                            if (username && fullText.includes(username)) {
                                commentText = fullText.substring(fullText.indexOf(username) + username.length).trim();
                            }
                            
                            // Clean up common patterns in comment text
                            const patterns = ['Reply', 'Like', 'Report', 'View replies', 'See translation'];
                            patterns.forEach(pattern => {
                                if (commentText.includes(pattern)) {
                                    commentText = commentText.replace(pattern, '').trim();
                                }
                            });
                            
                            // Try to extract timestamp
                            let timestamp = '';
                            const timeElements = el.querySelectorAll('time, a[href*="comments"]');
                            for (const elem of timeElements) {
                                const text = elem.textContent.trim();
                                if (/^\\d+[dwmhy]$|^\\d+ [a-z]+$/.test(text)) {
                                    timestamp = text;
                                    break;
                                }
                            }
                            
                            // Look for like count
                            let likes = '';
                            const likeElements = el.querySelectorAll('span, div');
                            for (const elem of likeElements) {
                                const text = elem.textContent.trim();
                                if (/^\\d+ likes?$|^\\d+ like this$/.test(text)) {
                                    likes = text;
                                    break;
                                }
                            }
                            
                            return {
                                username: username || '',
                                comment: commentText || '',
                                timestamp: timestamp || '',
                                likes: likes || ''
                            };
                        """, comment_elem)
                        
                        # Add to comments if both username and comment are present
                        if comment_data and comment_data['username'] and comment_data['comment']:
                            # Further clean up the comment
                            comment_text = comment_data['comment']
                            
                            # Remove timestamp if it appears within the comment
                            if comment_data['timestamp'] in comment_text:
                                comment_text = comment_text.replace(comment_data['timestamp'], '').strip()
                                
                            # Remove username if it appears again in the comment
                            if comment_data['username'] in comment_text:
                                comment_text = comment_text.replace(comment_data['username'], '').strip()
                                
                            # Update with cleaned text
                            comment_data['comment'] = comment_text
                            
                            # Only add if comment is not empty after cleaning
                            if len(comment_data['comment']) > 0:
                                comments.append(comment_data)
                                if len(comments) % 10 == 0:
                                    print(f"Extracted {len(comments)} comments so far...")
                    except Exception as e:
                        print(f"Error processing comment #{i}: {e}")
                        continue
                
                # Break out of approaches loop if we found comments
                if len(comments) > 0:
                    break
        except Exception as e:
            print(f"Error with extraction approach: {e}")
            continue
    
    # If we still have no comments, try a more aggressive approach with XPath
    if len(comments) == 0:
        print("Trying direct XPath targeting...")
        try:
            # Looking specifically for comment structures with any approach
            xpath_comments = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'comment') or .//a[contains(@href, '/p/')]]")
            
            for comment_elem in xpath_comments:
                try:
                    text = comment_elem.text.strip()
                    if text and len(text) > 5:  # Only process non-empty text with reasonable length
                        # Basic split on first line break to separate username and comment
                        parts = text.split('\n', 1)
                        username = parts[0].strip() if len(parts) > 0 else ""
                        comment_text = parts[1].strip() if len(parts) > 1 else text
                        
                        # Only add if we have both username and comment
                        if username and comment_text and username != comment_text:
                            comments.append({
                                'username': username,
                                'comment': comment_text,
                                'timestamp': '',
                                'likes': ''
                            })
                except:
                    continue
        except Exception as e:
            print(f"XPath approach failed: {e}")
    
    print(f"Successfully extracted {len(comments)} comments")
    return comments

def save_comments_to_file(comments, filename="instagram_comments.json"):
    """Clean, parse, and save comments to a structured JSON file"""
    try:
        all_cleaned_comments = []
        seen_comments = set()  # Track unique (username, comment) pairs
        
        for comment_block in comments:
            # Process each raw comment block
            if "comment" in comment_block and isinstance(comment_block["comment"], str):
                # First, try to extract just the main comment from the block
                raw_text = comment_block["comment"]
                
                # First try to get just the main comment by looking for patterns
                lines = raw_text.split('\n')
                
                # Basic structure: possible timestamp, comment text, likes count
                if len(lines) >= 3:
                    username = comment_block.get("username", "")
                    
                    # First line might be timestamp (e.g., "9w")
                    timestamp = ""
                    if len(lines[0]) <= 3 and any(char in lines[0] for char in "wdhms"):
                        timestamp = lines[0].strip()
                        # Remove timestamp line
                        lines = lines[1:]
                    
                    # Extract likes if present in a line
                    likes = ""
                    for i, line in enumerate(lines):
                        if "likes" in line and any(c.isdigit() for c in line):
                            likes_text = line.strip()
                            # Extract just the number from likes
                            import re
                            likes_match = re.search(r'(\d+)\s*likes', likes_text)
                            if likes_match:
                                likes = likes_match.group(1)
                            # Remove likes line
                            lines.pop(i)
                            break
                    
                    # Remaining lines before "Reply" are the comment text
                    comment_text = ""
                    for i, line in enumerate(lines):
                        if line.strip() == "Reply" or "View all" in line:
                            break
                        comment_text += line + " "
                    
                    comment_text = comment_text.strip()
                    
                    # Only add if we have valid comment text
                    if comment_text and username:
                        # Create a unique identifier for deduplication
                        unique_id = (username, comment_text)
                        if unique_id not in seen_comments:
                            seen_comments.add(unique_id)
                            all_cleaned_comments.append({
                                "username": username,
                                "comment": comment_text,
                                "likes": likes,
                                "timestamp" : convert_relative_time(timestamp)
                            })
        
        # Now also process the raw text to extract nested replies
        for comment_block in comments:
            if "comment" in comment_block and isinstance(comment_block["comment"], str):
                raw_text = comment_block["comment"]
                lines = raw_text.split('\n')
                
                # Process multiline text to find replies
                i = 0
                while i < len(lines):
                    # Look for username followed by timestamp pattern
                    if i+1 < len(lines) and len(lines[i].strip()) > 0:
                        potential_username = lines[i].strip()
                        # Check if next line could be a timestamp
                        if i+1 < len(lines) and re.match(r'^\s*\d+[wdhms]\s*$', lines[i+1]):
                            timestamp = lines[i+1].strip()
                            comment_start = i + 2
                            
                            # Look for the end of this comment (next username or end)
                            comment_end = comment_start
                            while comment_end < len(lines):
                                if "likes" in lines[comment_end] or "Reply" in lines[comment_end]:
                                    break
                                comment_end += 1
                            
                            # Extract the comment text
                            comment_lines = lines[comment_start:comment_end]
                            if comment_lines:
                                comment_text = ' '.join(comment_lines).strip()
                                
                                # Extract likes if present
                                likes = ""
                                if comment_end < len(lines) and "likes" in lines[comment_end]:
                                    likes_text = lines[comment_end]
                                    likes_match = re.search(r'(\d+)\s*likes', likes_text)
                                    if likes_match:
                                        likes = likes_match.group(1)
                                
                                # Only add if we have valid data
                                if potential_username and comment_text:
                                    unique_id = (potential_username, comment_text)
                                    if unique_id not in seen_comments:
                                        seen_comments.add(unique_id)
                                        all_cleaned_comments.append({
                                            "username": potential_username,
                                            "comment": comment_text,
                                            "timestamp": timestamp,
                                            "likes": likes
                                        })
                    i += 1
        
        # Remove duplicates again (just to be safe)
        final_comments = []
        seen = set()
        for comment in all_cleaned_comments:
            unique_id = (comment["username"], comment["comment"])
            if unique_id not in seen:
                seen.add(unique_id)
                final_comments.append(comment)
        
        # with open(filename, 'w', encoding='utf-8') as f:
        #     json.dump(final_comments, f, ensure_ascii=False, indent=4)
        # print(f"Comments successfully saved to {filename}")
        
        # Print sample of structured comments for verification
        # if final_comments:
        #     print("\nSample of extracted comments:")
        #     for i, comment in enumerate(final_comments[:5]):
        #         print(f"{i+1}. User: {comment['username']}")
        #         print(f"   Comment: {comment['comment']}")
        #         print(f"   Time: {comment.get('timestamp', 'N/A')}")
        #         print(f"   Likes: {comment.get('likes', 'N/A')}")
        #         print("---")
         
        post_id = '123'
        try:
            actions = [
                {
                    "_index": "posts_comments_index",
                    "_source": {
                        "post_id": post_id,
                        **comment
                    }
                }
                for comment in final_comments
            ]

            
            response = helpers.bulk(client1, actions, request_timeout=60)
        except Exception as e:
            print(f"Error in saving data in database {e}")
        
      
        return final_comments
    except Exception as e:
        print(f"Error saving comments to file: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    # URL of the Instagram post you want to scrape
    post_url = "https://www.instagram.com/p/DIdccyrJmnR/?hl=en"  # Replace with your target post URL

    match = re.search(r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)", post_url)
    post_id = match.group(1) if match else None

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
                comments_data = save_comments_to_file(comments)

                
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

if __name__ == "__main__":
    main()