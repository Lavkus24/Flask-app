from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
