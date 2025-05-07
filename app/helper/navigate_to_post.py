import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


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
        
    time.sleep(3)