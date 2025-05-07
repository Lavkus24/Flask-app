import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager
from .is_instagram_session_valid import is_instagram_session_valid

def setup_driver():
    chrome_options = Options()

    # Uncomment to run Chrome in headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")

    # Use a fake user agent to avoid detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    
    # Performance optimization settings
    chrome_options.page_load_strategy = 'eager'
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,  # Don't load images
            'notifications': 2,  # Disable notifications
            'popups': 2,  # Disable popups
            'geolocation': 2,  # Disable geolocation
            'auto_select_certificate': 2,  # Disable SSL selection
            'fullscreen': 2,  # Disable fullscreen
            'mouselock': 2,  # Disable mouse lock
            'mixed_script': 2,  # Disable mixed script
            'media_stream': 2,  # Disable media stream
            'media_stream_mic': 2,  # Disable mic
            'media_stream_camera': 2,  # Disable camera
            'push_messaging': 2,  # Disable push
            'ssl_cert_decisions': 2,  # Disable cert decisions
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)

    logging.basicConfig(level=logging.INFO)
    logging.info("Starting ChromeDriver...")
    
    # Set up ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logging.info("ChromeDriver started successfully")
    
    # Navigate to Instagram initially
    driver.get("https://www.instagram.com/")
    time.sleep(3)
  
    # List of session IDs to try
    session_ids = [
        '73653041961%3AOQRoxptHUfzx9R%3A15%3AAYfbxIuYC4BTsFLJh0Q_qjCoZugxuQ7Wh4WisnHzwg',
        '72526559706%3Am6c9fkbDTmhvvv%3A28%3AAYeETJ5-NGpgJlqW9fzple01ziHGRIB-8ORxlEYH1g',
        '56189549536%3AEh88ytCyRmrzkq%3A10%3AAYfEA1Gy8V1qNWDL7sGvaSHaJZhqL7oS3-rH-X3Nvw',
        '73770700193%3ATwLXB5uJ4o9lbg%3A25%3AAYfk091f3bIs4iM6WcKo_tIQnh9TEPQwH091Wk6Ceg'
        # Add other session IDs here
    ]
    
    # Try each session ID until one works
    for session_id in session_ids:
        try:
            # Check if the session ID is valid before trying to use it
            if is_instagram_session_valid(session_id):
                print("session id working")
                # Add the session ID cookie to the browser
                driver.add_cookie({
                    'name': 'sessionid',
                    'value': session_id,
                    'domain': '.instagram.com',
                    'path': '/'
                })
                
                # Refresh the page to apply the cookies
                driver.refresh()
                time.sleep(3)
                
                # Check if login was successful by looking for profile icon or home feed
                try:
                    # Look for elements that indicate successful login
                    if len(driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'profile')]")) > 0 or \
                       len(driver.find_elements(By.XPATH, "//a[contains(@href, '/direct/inbox')]")) > 0:
                        print(f"Successfully logged in with session ID: {session_id[:10]}...")
                        return driver
                except Exception as e:
                    print(f"Error checking login status with session ID {session_id[:10]}: {e}")
            else:
                print(f"Session ID {session_id[:10]}... is invalid")
        except Exception as e:
            print(f"Error with session ID {session_id[:10]}: {e}")
    
    print("All session IDs failed. Please provide new session IDs.")
    return driver