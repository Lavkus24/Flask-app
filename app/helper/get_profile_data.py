import re
import os
import time
import random
import logging
import asyncio
from bs4 import BeautifulSoup
from .find_category import find_category
from app.utils.setup_driver import setup_driver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .scrape_instagram_posts import scrape_instagram_posts
from .get_profile_picture import get_profile_picture
from app.utils.aws import update_instagram_profiles
from app.utils.aws import store_post_data_in_opensearch

def convert_to_int(value):
    value = value.strip().lower().replace(',', '')

    if value.endswith('k'):
        return int(float(value[:-1]) * 1_000)
    elif value.endswith('m'):
        return int(float(value[:-1]) * 1_000_000)
    else:
        return int(float(value))

def get_profile_data(username):
    driver=setup_driver()
    
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
    


# Instagram categories can appear under business profiles  # May vary
    
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
    pattern_with_k = r'(\d+(?:[.,]?\d*)([KMW])?)\s*Followers,\s*' \
                 r'(\d+(?:,\d+)*)\s*Following,\s*' \
                 r'(\d+(?:,\d+)*)\s*Posts\s+-\s+See Instagram photos and videos from (.*?) \(@'
    match = re.search(pattern_with_k , content)
    profile_image_tag = soup.find('meta', property='og:image')
    profile_image_url = profile_image_tag['content'] if profile_image_tag else ''
    
    posts_data = scrape_instagram_posts([],driver)

    mentions = []
    hashtags = []
    captions=[]
    likes=0
    comments=0

    for post in posts_data:
        mentions.extend(post.get('mentions', []))  # Use `.get()` to avoid KeyError
        hashtags.extend(post.get('hashtags', []))
        l1 = convert_to_int(post.get('likes', 0))
        c1 = convert_to_int(post.get('comments', 0))
        print(f"likes : {l1} , comments : {c1} ,  url : {post.get('url' , '')}")
        if isinstance(l1, int):
                likes += int(l1)
        if isinstance(c1, int):
                comments += int(c1)

    category = find_category(captions,hashtags,mentions)
    engagement = (likes + comments) / 10
    total_followers = convert_to_int(match.group(1))
    total_following=convert_to_int(match.group(3))
    er = round(engagement / total_followers, 2) if total_followers > 0 else 0
    views = round(engagement / er, 2) if er > 0 else 0
    reach = round(views * .97, 2)

    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    email_match = re.search(email_regex, bio)
    has_email = bool(email_match)



    if match:
        profile_pic_path = get_profile_picture(username)
        user_data = {
                "connector":"instagram",
                "handle": username,
                "image_link": profile_pic_path,
                "handle_link":f"https://www.instagram.com/{username}/",
                "followers": total_followers,
                "following": total_following,
                "engagement":engagement,
                "posts": match.group(4),
                "category":category,
                "full_name":match.group(5),
                "average_views":reach,
                "gender":None,
                "age_group":None,
                "effective_follower_rate":er,
                "interests":"",
                "location" : country,
                "hasEmail":has_email,
                "bio"  : bio,
                "mentions" : mentions,
                "hashtags": hashtags,
            }
       
       
        asyncio.run(update_instagram_profiles(user_data))
        asyncio.run(store_post_data_in_opensearch(posts_data))
        # await update_instagram_profiles(user_data)
        # await store_post_data_in_opensearch(posts_data)
        if profile_pic_path and os.path.exists(profile_pic_path):
            os.remove(profile_pic_path)
            print(f"Deleted temporary profile picture: {profile_pic_path}")
        
        return  {"user_data" :  user_data }
    else:
        return "Data not found in the meta description."