from selenium import webdriver
import time 
import datetime
import re
import random
import logging  
import requests
import asyncio
import json
from bs4 import BeautifulSoup
import openpyxl
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.service import Service  
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys 

import sys
import os
from datetime import timedelta
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timedelta
import logging
import aws
def is_within_last_year(date_str):
    if not date_str:
        return False
        
    try:
        # Try to parse the date with different formats
        date_formats = [
            '%B %d, %Y',    # May 11, 2023
            '%d %B %Y',     # 11 May 2023
            '%Y-%m-%d',     # 2023-05-11
            '%B %d,%Y'      # May 11,2023 (no space)
        ]
        
        parsed_date = None
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), date_format)
                # print(parsed_date)
                break
            except ValueError:
                continue
                
        if not parsed_date:
            logging.warning(f"Could not parse date: {date_str}")
            return False
            
        one_year_ago = datetime.now() - timedelta(days=365)
        # print("one")
        # print(one_year_ago)
        return parsed_date >= one_year_ago
        
    except Exception as e:
        logging.error(f"Error processing date {date_str}: {str(e)}")
        return False
    
def scrap_post_data(url): 
    response = requests.get(url)
    
    time.sleep(random.uniform(2,3))
    data = response.text
    soup = BeautifulSoup(data, 'lxml')
    meta_content = soup.find('meta', property="og:description")
    if not meta_content:
        logging.warning(f"No meta description found for {url}")
        return False, None

    meta_content = meta_content['content']
    
    is_shared = "Shared post" in meta_content or "shared a post" in meta_content
    
    # Regular expressions with modifications to handle shared posts
    likes_regex = r'(\d+\s?[KMW]?)\slikes'  
    comments_regex = r'(\d+\s?[KMW]?)\scomments'  
    date_regex = r'on\s([^:]+)(?::|$)'  # Modified to handle cases without colon
    caption_regex = r'"([^"]*?)"'
    
    # For shared posts, try alternate patterns
    if is_shared:
        # Try to find the original post date and content
        alt_date_regex = r'Posted on\s([^•]+)'
        alt_caption_regex = r'Posted[^"]*"([^"]*)"'
        
        date_match = re.search(alt_date_regex, meta_content)
        caption_match = re.search(alt_caption_regex, meta_content)
    else:
        date_match = re.search(date_regex, meta_content)
        caption_match = re.search(caption_regex, meta_content)
    
    # Extract data
    likes_match = re.search(likes_regex, meta_content)  
    comments_match = re.search(comments_regex, meta_content)  
    
    likes = likes_match.group(1) if likes_match else None  
    comments = comments_match.group(1) if comments_match else None  
    date = date_match.group(1).strip() if date_match else None
    
    if date and not is_within_last_year(date):
        return False, None
        
    caption = caption_match.group(1).strip() if caption_match else None

    if caption:
        caption = re.sub(r'@\w+', '', caption)
        caption = re.sub(r'#\w+', '', caption)
        caption = caption.strip()
    
    mentions = re.findall(r'@(\w+)', meta_content)
    hashtags = re.findall(r'#(\w+)', meta_content)
    
    extracted_data = {
        "url" : url,
        "likes": likes,
        "comments": comments,
        "date": date,
        "caption": caption,
        "mentions": mentions,
        "hashtags": hashtags,
        "is_shared": is_shared,
    }
    
    return True, extracted_data

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



def get_profile_data(username, driver):
    
    driver.get(f"https://www.instagram.com/{username}/")
    
    time.sleep(random.uniform(2,3))
    options_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Options"]'))
    )
    options_button.click()
    time.sleep(random.uniform(2,3))
    try:
        about_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[text()="About this account"]'))
        )
    except:
        about_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "About this account")]'))
        )
    about_button.click()
    time.sleep(random.uniform(2,3))
    
    country = 'N/A'
        # Wait for the modal to appear and extract location
    try:
        # Look for the section containing account info
        account_info = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Account based in')]/following-sibling::div"))
        )
        country = account_info.text.strip()
    except:
        try:
                # Alternative method using the modal structure
            location_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[role="dialog"] span'))
            )
            # Find all spans and look for the one after "Account based in"
            spans = driver.find_elements(By.CSS_SELECTOR, '[role="dialog"] span')
            for i, span in enumerate(spans):
                if span.text.strip() == "Account based in":
                    country = spans[i + 1].text.strip()
                    break
            else:
                country = None
        except:
                logging.error("Could not find location information")
                country = None

    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'lxml')
    meta_tag = soup.find('meta', property='og:description')
    content = meta_tag['content']
    
    bio_element = soup.select_one('div._aa_c')  # This selector might need updating
    bio = bio_element.text.strip() if bio_element else ''

    if not bio:
        # Look for the pattern that typically appears before follower count
        follower_pattern = r'(\d+(?:[.,]?\d*)(?:[KMW])?)\s*Followers'
        follower_match = re.search(follower_pattern, content)
        if follower_match:
            start_pos = follower_match.start()
            bio = content[:start_pos].strip()
        
        
    pattern = r'(\d+(?:,\d+)*)\s*Followers,\s*(\d+(?:,\d+)*)\s*Following,\s*(\d+(?:,\d+)*)\s*Posts'
    pattern_with_k = r'(\d+(?:[.,]?\d*)([KMW])?)\s*Followers,\s*(\d+(?:,\d+)*)\s*Following,\s*(\d+(?:,\d+)*)\s*Posts'
    match = re.search(pattern_with_k , content)
    profile_image_tag = soup.find('meta', property='og:image')
    profile_image_url = profile_image_tag['content'] if profile_image_tag else ''
    
    posts_data = scrape_instagram_posts([],driver)

    mentions = []
    hashtags = []

    for post in posts_data:
        mentions.extend(post.get('mentions', []))  # Use `.get()` to avoid KeyError
        hashtags.extend(post.get('hashtags', []))
    if match:
        user_data = {
                "username": username,
                "bio"  : bio,
                "followers": match.group(1),
                "following": match.group(3),
                "posts_count": match.group(4),
                "profile_image_url": profile_image_url,
                "location" : country,
                "mentions" : mentions,
                "hashtags": hashtags,
            }
       
       
        asyncio.run(aws.update_instagram_profiles(user_data))
        asyncio.run(aws.store_post_data_in_opensearch(posts_data))
        
        return  {"user_data" :  user_data }
    else:
        return "Data not found in the meta description."

def create_Driver():
    driver_path = "C:/Program Files/chromedriver-win64/chromedriver.exe"
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service)
    
    
    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    
    driver.get("https://www.instagram.com/")

    cookiesList = [
        {'name': 'sessionid', 'value': '72526559706%3Am6c9fkbDTmhvvv%3A28%3AAYeETJ5-NGpgJlqW9fzple01ziHGRIB-8ORxlEYH1g'},  
        {'name': 'sessionid', 'value': '72376088787%3AMIceO8FObfB1dE%3A19%3AAYeWs0yCYVjT74HsmClJA4EoD7YRZYvl09LwPRuEZw'},    
        {'name': 'sessionid', 'value': '72376088787%3AMIceO8FObfB1dE%3A19%3AAYcIx3mF_yM8cufzywqw4M8N6RFZXrTjv5SM1MGNaA'}, 
        {'name': 'sessionid', 'value': '56189549536%3ALaUdlCEKvhE7id%3A16%3AAYd9vANxiBdWRfHloWb6lMX0B1rUFLJZIKcRfFdISg'}, 
        {'name': 'sessionid', 'value': '56189549536%3AEh88ytCyRmrzkq%3A10%3AAYfEA1Gy8V1qNWDL7sGvaSHaJZhqL7oS3-rH-X3Nvw'},   
        
         
        {'name': 'sessionid', 'value': '72730890572%3ARZYugd08Jv45QD%3A18%3AAYcOPgizoGuIWk9lrcv9YdVOo2oPTCX4dIkSrJYvjg'},   
         
        {'name': 'sessionid', 'value': '51317686193%3AAHvdnOhUK9JxH1%3A2%3AAYcqyAPD8CryFMIdsVvusUQjw9Mov3TKr2goMmNyHw'},  
          
        {'name': 'sessionid', 'value': '72376088787%3AMIceO8FObfB1dE%3A19%3AAYcuW-neTjO494aJUDbDZpI8eAn_i29vtNwtoI7M6mI'}, 
    ]
    
    tempList = cookiesList.copy()  # Create a temporary list
    
    for cookie in tempList[:]:  # Iterate over a copy of tempList
        driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)  # Wait for Instagram to process the session
        try:
            driver.find_element(By.XPATH, "//input[@name='username']")  # Login field appears => failed login
            # print(f"Session ID {cookie['value']} failed, removing from tempList...")
            tempList.remove(cookie)  # Remove invalid session ID
        except:
            return driver  # Exit function if login is successful
    
    print("All session IDs failed to log in.")
    driver.quit()
    return None    

def scrap_data(batch) :
    driver = create_Driver()
    print(f"Batchsc : {batch}")
    profile_data = get_profile_data(batch, driver)
    print(json.dumps(profile_data))
    driver.quit()
    
