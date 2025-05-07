import time
import random
from selenium.webdriver.common.by import By  
from selenium.webdriver.common.keys import Keys
from .scrape_post_data import scrap_post_data

def scrape_instagram_posts(existing_urls=[], driver=None):
    # Initialize scroll tracking
    last_height = driver.execute_script("return document.body.scrollHeight") 
    post_links = []
    posts_data = []
    scroll_count = 0
    scroll_pause_time = random.uniform(1,3)
    caption_list = []
    hashtag_list = []
    mentions_list = []
    max_scrolls = 1

    while scroll_count < max_scrolls:  
        try: 
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END) 
            scroll_count += 1
            time.sleep(scroll_pause_time)

            posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/") or contains(@href, "/reel/")]')
            fg = True
            
            for post in posts:
                link = post.get_attribute('href')
                if link is None:
                    continue
                if link in existing_urls:
                    return posts_data
                if link not in post_links:
                    fg, post_data = scrap_post_data(link)
                    if post_data is None:
                        continue
                    if not fg:
                        return posts_data
                    else:
                        post_links.append(link)
                        posts_data.append(post_data)

                        caption = post_data.get('caption', 'No caption')
                        hashtags = post_data.get('hashtags', [])
                        mentions = post_data.get('mentions', [])

                        if caption:
                            caption_list.append(caption)
                        hashtag_list.extend(hashtags)  # FIXED: Extend instead of append
                        mentions_list.extend(mentions)  # FIXED: Populate mentions

            new_height = driver.execute_script("return document.body.scrollHeight") 
            if new_height == last_height:
                break
            last_height = new_height  

        except Exception as e:
            print(f"Error: {e}")
            break
    
  
    return  posts_data