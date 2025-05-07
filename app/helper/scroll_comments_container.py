import time
from selenium.webdriver.common.by import By

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