from selenium import webdriver
import time 
import datetime
import re
import random
import logging  
import requests
import asyncio
import json
<<<<<<< HEAD
from flask import jsonify
=======
>>>>>>> 545368e94f890cf7ac229226e8815e91b3669134
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
<<<<<<< HEAD
from sendEmail import send_email_aws_ses
import sys
import os
=======

import sys
import os
from datetime import timedelta
from datetime import datetime
>>>>>>> 545368e94f890cf7ac229226e8815e91b3669134
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timedelta
import logging
import aws
<<<<<<< HEAD
import json
import httpx
from findCategory import find_category
from opensearchpy import OpenSearch, helpers, NotFoundError
from filterBotAccount import analyze_account
from dotenv import load_dotenv
load_dotenv()

client = httpx.Client(
    headers={
        "x-ig-app-id": "936619743392459",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

user_name = os.getenv("USER_NAME")
user_password = os.getenv("PASSWORD")
host_url = os.getenv("HOST_URL")

client1 = OpenSearch(
    hosts=[host_url],
    http_auth=(user_name, user_password),
)

=======
>>>>>>> 545368e94f890cf7ac229226e8815e91b3669134
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
<<<<<<< HEAD
    
=======

>>>>>>> 545368e94f890cf7ac229226e8815e91b3669134
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
<<<<<<< HEAD
    max_scrolls = 12
    
=======
    max_scrolls = 1

>>>>>>> 545368e94f890cf7ac229226e8815e91b3669134
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
<<<<<<< HEAD
            print(f"Error in scraping post data: {e}")
            break
    return  posts_data


def convert_to_int(value):
    if value is None:  
        return 0  # Treat None as 0
    
    if isinstance(value, str):  
        value = value.strip().lower()  # Remove spaces & convert to lowercase
        
        value = re.sub(r'^0+(\d+)', r'\1', value)
        
        if value.isdigit():  # Handles '012' -> 12
            return int(value)
        
        if 'k' in value:  # Convert '100k' to 100000
            return int(float(value.replace('k', '')) * 1000)
        elif 'm' in value:  # Convert '2.5m' to 2500000
            return int(float(value.replace('m', '')) * 1000000)
        elif 'b' in value:  # Convert '1.2b' to 1200000000
            return int(float(value.replace('b', '')) * 1000000000)
    
    try:
        return int(value)  # Convert other valid numbers
    except (ValueError, TypeError):
        return 0  
    
def get_profile_data(username, driver):
    
    try : 
        
        print(f"username : {username}")
        driver.get(f"https://www.instagram.com/{username}/")
        
        time.sleep(random.uniform(2,3))
        try:
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
            try:
                xpath = '//span[text()="Date joined"]/following-sibling::span[1]'
                
                date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                text = date_element.text.strip()
                date_joined = text if text else "N/A"
            except Exception:
                date_joined = "N/A"
            
            joined_year = int(date_joined.split()[-1])

            if date_joined != "N/A":
                current_year = datetime.now().year
                result = (current_year - joined_year) + 16
                print(f"result : {result}")
            
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
        except Exception as e:
            return "Error in finding the country"
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
                
        full_name = None
        is_verified = None
        bio = None
        category = "NA"

        try:
            result = client.get(
                f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
            )
            
            if result.status_code == 200:  # Ensure successful response
                data = json.loads(result.content)
                user_data = data.get("data", {}).get("user", {})

                bio = user_data.get("biography", "")
                is_verified = user_data.get("is_verified", False)  # Defaults to False
                full_name = user_data.get("full_name", "")
                category = user_data.get("category", "NA")  # Default to "NA" if missing
            else:
                print(f"API Request Failed! Status Code: {result.status_code}")

        except Exception as e:
            print(f"Error fetching Instagram profile: {e}")
              
        pattern = r'(\d+(?:,\d+)*)\s*Followers,\s*(\d+(?:,\d+)*)\s*Following,\s*(\d+(?:,\d+)*)\s*Posts'
        pattern_with_k = r'(\d+(?:[.,]?\d*)([KMW])?)\s*Followers,\s*(\d+(?:,\d+)*)\s*Following,\s*(\d+(?:,\d+)*)\s*Posts'
        match = re.search(pattern_with_k , content)
        profile_image_tag = soup.find('meta', property='og:image')
        profile_image_url = profile_image_tag['content'] if profile_image_tag else ''
        
        posts_data = scrape_instagram_posts([],driver)
     
        mentions = []
        hashtags = []
        likes = 0
        comments = 0
        handle_list = []
        for post in posts_data:
            mentions.extend(post.get('mentions', []))  # Use `.get()` to avoid KeyError
            hashtags.extend(post.get('hashtags', []))
            l1 = convert_to_int(post.get('likes', 0))
            c1 = convert_to_int(post.get('comments', 0))
            
            # likes_url = convert_to_liked_by(post.get('url' , ''))
            # handle_name = get_post_likes_handle_name(driver,likes_url)
            # handle_list.append(handle_name)
            
            print(f"likes : {l1} , comments : {c1} ,  url : {post.get('url' , '')}")
            if isinstance(l1, int):
                likes += int(l1)
            if isinstance(c1, int):
                comments += int(c1)

        engagement = (likes + comments) / 10
        total_followers = convert_to_int(match.group(1))
        er = round(engagement / total_followers, 2) if total_followers > 0 else 0
        views = round(engagement / er, 2) if er > 0 else 0
        reach = round(views * .97, 2) 
        
        if(category == "NA"):
            category = find_category([], hashtags, mentions)
        
        if match:
            user_data = {
                    "username": username,
                    "full_name" : full_name,
                    "bio"  : bio,
                    "followers": match.group(1),
                    "following": match.group(3),
                    "posts_count": match.group(4),
                    "profile_image_url": profile_image_url,
                    "location" : country,
                    "category" : category,
                    "mentions" : mentions,
                    "hashtags": hashtags,
                    "average_views": views,
                    "er" : er,
                    "reach" : reach,
                    "is_verified" : is_verified
                }
           
            print(f"user data  : {user_data}")
        
            asyncio.run(aws.update_instagram_profiles(user_data))
            asyncio.run(aws.store_post_data_in_opensearch(posts_data))
            # asyncio.run(aws.addInfluencerLikes(handle_list, username))
            return  {"user_data" :  user_data }
        else:
            return "Data not found in the meta description."
    except Exception as e:
        return f"Error in creating the driver4: {e}" 
    

def is_instagram_session_valid(session_id):
    url = "https://www.instagram.com/accounts/edit/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.instagram.com/",
    }
    cookies = {
        "sessionid": session_id
    }

    response = requests.get(url, headers=headers, cookies=cookies, allow_redirects=False)

    if response.status_code == 200:
        print("✅ Session ID is valid.")
        return True
    elif response.status_code == 302:
        print("❌ Session ID is invalid or expired (redirected to login).")
        return False
    else:
        print(f"⚠️ Unexpected status: {response.status_code}")
        return False


def is_instagram_session_valid(session_id):
    
    print(f"session_id : {session_id}")
    url = "https://www.instagram.com/accounts/edit/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.instagram.com/",
    }
    cookies = {
        "sessionid": session_id
    }
    response = requests.get(url, headers=headers, cookies=cookies, allow_redirects=False)

    if response.status_code == 200:
        print("\u2705 Session ID is valid.")
        return True
    elif response.status_code == 302:
        print("\u274C Session ID is invalid or expired (redirected to login).")
        return False
    else:
        print(f"⚠️ Unexpected status: {response.status_code}")
        return False


def create_Driver():
    try:
        # driver_path = "C:/Program Files/chrome-new-driver/chromedriver-win64/chromedriver.exe"
        # service = Service(executable_path=driver_path)
        # driver = webdriver.Chrome(service=service)
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        driver.get("https://www.instagram.com/")

        cookiesList = [

            {'name': 'sessionid', 'value': '72491420302%3AYd5TmtxqL1lDlm%3A26%3AAYe0dc2Me2NXAFEKm44AnJKscCfdtfjEoZ5tnY2-fg'},
            {'name': 'sessionid', 'value': '55622194184%3AcQYoHXMxJkUdqJ%3A23%3AAYenr-esP3aol3eAU6p9bZt1KhmncYtF1t0xdnhWmw'},
            {'name': 'sessionid', 'value': '72730890572%3A2G5mfV5jvwdtSz%3A8%3AAYdMJTMoLNfZmJJqAMApoS-hHGWRRQv7VfYBC-CIEQ'},
            {'name': 'sessionid', 'value': '72491420302%3AfTepGSiU3FkMwg%3A1%3AAYeFkhgOwIHN5zqn0EQEkqd8yO6Ye-ZCCPQ3UJ9Kog'},
            {'name': 'sessionid', 'value': '3077205760%3A6eYgPvBriovx41%3A12%3AAYfBp2UPckIICDTpOUyAYXH8KI11e_g79Da3pme0mg'},
            {'name': 'sessionid', 'value': '73630209054%3AgEGMtTHHR5trj0%3A8%3AAYeiMRq3mX080Q7yDeylnQ8SlLvghZOwXugzPhOEjQ'},
            # {'name': 'sessionid', 'value': '3077205760%3ATcKYoqJUuQEcGM%3A7%3AAYfzO1S5tNPC7IfLB3ySaQkSPOHF1zDnm7rYnmIxcA'},
            # {'name': 'sessionid', 'value': '73795541404%3ARsrvz7Lg5Niuot%3A3%3AAYc22qSoKv5nfgl73ab74WBTSjYvInl3hPa3LsJDVA'},
            # {'name': 'sessionid', 'value': '73630209054%3ABaxZECjgkYKWYt%3A15%3AAYcJvLY3imU9s-rr5aEAOmAzpqi5yQRvj6R-yHS_pA'},
            # {'name': 'sessionid', 'value': '3077205760%3AQkJIRTwIVSSXoQ%3A7%3AAYcn3syHpWjmhTLNh8UqkvvjwSgU4fUSXzESXR5isg'},
            # {'name': 'sessionid', 'value': '72491420302%3AL69ZVPCfh1ADRA%3A13%3AAYfax9G6HQpDzJkHB2M5NsLHOmtmjnxy7f_tMJDkwg'},
            # {'name': 'sessionid', 'value': '55622194184%3AU9AjsSqZf3SxFu%3A2%3AAYehPvQCgsh-bPvE5hCA4Apdl-xQ6X3yDxoPUAU-yw'},
            # {'name': 'sessionid', 'value': '72491420302%3AlLNZxYCLzBd7h6%3A7%3AAYfHWDiYroXrsEzpdvT5SETeMDaY1Wn1ZbuBSxmP4g'},
            # {'name': 'sessionid', 'value': '73565872976%3AvDlkBBhHIPGVsK%3A26%3AAYeyY4aKyCndPmxDCUvwS5UYoD5bjFaGhqlMCArKPg'},
            # {'name': 'sessionid', 'value': '73749423400%3Aq40NaTlGVSfQmm%3A20%3AAYeDA1IN-MWq5RYqbfFLghv3aEBfGHCv3syAU1q_hg'},
            # {'name': 'sessionid', 'value': '73986905335%3A2JeLS7lB7uJ9EH%3A21%3AAYdwh-jOWyCbPIH-nrkkS2BTD1DuVJnMlEwAH8RP3A'},
            # {'name': 'sessionid', 'value': '73178258443%3Ax13aeuzwTJ19PC%3A6%3AAYePEKzjAMclRpBoIEg047XhkjLd-9gk5yagH5fkrA'},
            # {'name': 'sessionid', 'value': '73315780130%3AY8ZvEWf6XJslVL%3A24%3AAYc8CIEGBisQApId4fdt5t2gIMvE5deMuzflXRx3Rg'},

            # {'name': 'sessionid', 'value': '73564372761%3AhpyJnaDOGuTNbi%3A0%3AAYfRZMS_u8p_FTRViMt6OUkNxIecWad92od-wgCuTw'},
            # {'name': 'sessionid', 'value': '72526559706%3ATTGNNZ39L1u7xD%3A7%3AAYfXxfQQJD7puXgw_HIT3JVfBHauX1qEKn3IVfz8PFw'},
            # {'name': 'sessionid', 'value': '73565872976%3An5JPsfYkvVyplm%3A3%3AAYeBvW_C16GNHlJNdwl5N8uybgSQh_GDMWhWt6GBMQ'},
            # {'name': 'sessionid', 'value': '72491420302%3AVGm3WUTFCa92MB%3A3%3AAYcRFnw9MNzBUWeQ-FYCg_ceEDcVy_Z-hqIHBm-S5w'},
            # {'name': 'sessionid', 'value': '72526559706%3ATTGNNZ39L1u7xD%3A7%3AAYfXxfQQJD7puXgw_HIT3JVfBHauX1qEKn3IVfz8PFw'},  
            # {'name': 'sessionid', 'value': '73565872976%3An5JPsfYkvVyplm%3A3%3AAYeBvW_C16GNHlJNdwl5N8uybgSQh_GDMWhWt6GBMQ'}, 
            # {'name': 'sessionid', 'value': '72526559706%3ATTGNNZ39L1u7xD%3A7%3AAYdOYwXjz8E-unA9onJV2JFknfS37_q29SfniZ9gkoc'},
            # {'name': 'sessionid', 'value': '72730890572%3AM6BOWTpnaRXUZn%3A9%3AAYetHKr1vbHkCmYuuH1hgnA5KupvTQ8Uv8mJ41SwBA'},
            # {'name': 'sessionid', 'value': '51317686193%3AAHvdnOhUK9JxH1%3A2%3AAYeudiq6ASkuapFrgWffY7dFPIZIhrThB3nAIvC7Ug'},
            # {'name': 'sessionid', 'value': '55622194184%3AFcY4oZ2pvOYyrY%3A21%3AAYf4NpX4h6_4n25rCTmDh4f3oe0WTGLsYUmcFieDCQ'},
            # {'name': 'sessionid', 'value': '51317686193%3AAHvdnOhUK9JxH1%3A2%3AAYeudiq6ASkuapFrgWffY7dFPIZIhrThB3nAIvC7Ug'},
            # {'name': 'sessionid', 'value': '73561734336%3ATgcP6lHHGKUJyn%3A24%3AAYd7m1-B4Y37vsA4ewNZL9Pz_jC-6e8cZ9P5ciFBAQ'},
            # {'name': 'sessionid', 'value': '73565872976%3An5JPsfYkvVyplm%3A3%3AAYeBvW_C16GNHlJNdwl5N8uybgSQh_GDMWhWt6GBMQ'},
            # {'name': 'sessionid', 'value': '73708908925%3AwsE6xq5mzV4AHy%3A13%3AAYcn5a0SBaC1xVkr8AiGSi4LCNg4VGWWmOHWiL5mxg'},
            # {'name': 'sessionid', 'value': '73620888717%3AAFWlBMx8AwryTh%3A15%3AAYdsFdt732v_RzH9A2OQkb4tQvkay6mbdZBANrx01g'},
            # {'name': 'sessionid', 'value': '72526559706%3ATTGNNZ39L1u7xD%3A7%3AAYfXxfQQJD7puXgw_HIT3JVfBHauX1qEKn3IVfz8PFw'},
            # {'name': 'sessionid', 'value': '72491420302%3AVGm3WUTFCa92MB%3A3%3AAYcRFnw9MNzBUWeQ-FYCg_ceEDcVy_Z-hqIHBm-S5w'},
            # {'name': 'sessionid', 'value': '72526559706%3ATTGNNZ39L1u7xD%3A7%3AAYfXxfQQJD7puXgw_HIT3JVfBHauX1qEKn3IVfz8PFw'},  
            # {'name': 'sessionid', 'value': '73708908925%3AwsE6xq5mzV4AHy%3A13%3AAYcH8_gI5RIri0Mlf9pTX_64pb0pMYWpgE8rTcXjKw'},
            # {'name': 'sessionid', 'value': '72730890572%3AM6BOWTpnaRXUZn%3A9%3AAYetHKr1vbHkCmYuuH1hgnA5KupvTQ8Uv8mJ41SwBA'},
            # {'name': 'sessionid', 'value': '51317686193%3AAHvdnOhUK9JxH1%3A2%3AAYeudiq6ASkuapFrgWffY7dFPIZIhrThB3nAIvC7Ug'},
            # {'name': 'sessionid', 'value': '73565872976%3An5JPsfYkvVyplm%3A3%3AAYeos8FvRSeA7xVtIkTSZG88V7JTIckfvZyrsUFZXw'},
            # {'name': 'sessionid', 'value': '73518940261%3ALd4hXprOVmf58E%3A25%3AAYdPeW9PtKUYPfKwORYGNq9HvTJHJmMi5vksJVS62A'},
            # {'name': 'sessionid', 'value': '72491420302%3AVGm3WUTFCa92MB%3A3%3AAYdmmRz0k0rzd_Z0eb9QqbPYiFcpgWAE_bxMVhboIA'},
            # {'name': 'sessionid', 'value': '73178258443%3Aded9QXpecC67g1%3A8%3AAYfUWXEHpzL4LkPDvIW3cfIiLI9i7Oxp_dJTZBeBGA'},
            # {'name': 'sessionid', 'value': '72730890572%3AM6BOWTpnaRXUZn%3A9%3AAYeTpmRckIAurx1lNn5Hos8jIHNHZwYaNrhZtoDrPQ'},
            # {'name': 'sessionid', 'value': '72491420302%3AVGm3WUTFCa92MB%3A3%3AAYdSDtGGoxcmsoeg8Qi19DP0CclqPiLTC03qJjS7Tg'},
            # {'name': 'sessionid', 'value': '73408446729%3Ada0DHZCzyeKD5D%3A16%3AAYfXdiLYWkvftMEXcw7rR2C6It_C5oKcmTi-qwzuBg'},
            # {'name': 'sessionid', 'value': '73749423400%3A5MU8j0RdcVZE5S%3A3%3AAYc1opEyQfI7ObPVw2Ld20XAYBRmrQoSBwV4SVdKPw'},
            # {'name': 'sessionid', 'value': '73970416934%3AoNsChKa5Iu1HRQ%3A3%3AAYe23da0WH7Q9jPsIGn7nEna0JfGE2bP5Fgs1PBtFA'},
            
       
            
        ]

        cookies_copy = cookiesList[:]
        random.shuffle(cookies_copy)
        
        # Try each cookie until a valid one is found
        while cookies_copy:
            cookie = cookies_copy.pop()  # Remove and get a random cookie
            try:
                if is_instagram_session_valid(cookie['value']):
                    driver.add_cookie(cookie)
                    driver.refresh()
                    print("Logged in with a valid session ID.")
                    # return driver
                else :
                    continue
            except Exception as e:
                print(f"Error in creating driver {e}")
        print("All session IDs failed to log in.")
        driver.quit()
        return None

    except Exception as e:
        print(f"Error in creating the driver: {e}")
        return None
    

def scrap_data(batch_array,start,size) :
  
    flag = True
    count = 0
    print(f"batch array  : {batch_array}")
    for data_set in batch_array:
        driver = create_Driver()
        if(driver):
            profile_data = get_profile_data(data_set, driver)
            print(json.dumps(profile_data))
            driver.quit()
            count = count + 1
        else :
            flag = False
            break
    
    if(flag):
        # send_email_aws_ses("Request Processed", f"Request has been completed from {start} to {size}", "lavkus@flynt.social")
        print(f"Request has been processed")
    else :
        # send_email_aws_ses("session id", f"There is no any sessionId available to proceess the request from {start + count} to {size}", "lavkus@flynt.social")
        print(f"Request has not been processed, No sesion id is available")
        
         
         

         
# ['alessandrobillycostacurta', 'official_sslazio', 'celticfc', 'el_falso9']
def scrap_data() :
    batch_array  = ["riyasendv"]
    print(f"batch_array : {batch_array}")
    for data_set in batch_array:
        driver = create_Driver()
        print(f"Driver : {driver}")
        if(driver):
            profile_data = get_profile_data(data_set, driver)
            print(json.dumps(profile_data))
            driver.quit()  
        else :
            print(f"There is no driver available")  
scrap_data()


# def convert_to_liked_by(url):
#     # Handle both /p/ and /reel/ URLs
#     parts = url.split("/p/")
#     if len(parts) > 1:
#         shortcode = parts[1].split("/")[0]
#         return f"https://www.instagram.com/p/{shortcode}/liked_by"

#     # Try handling /reel/ URLs as fallback
#     parts = url.split("/reel/")
#     if len(parts) > 1:
#         shortcode = parts[1].split("/")[0]
#         return f"https://www.instagram.com/p/{shortcode}/liked_by"

#     raise ValueError("Invalid Instagram URL format")



# def scrapDataForInsight(handlename):
#     try:
#         response = client1.search(
#             index="posts_likes_hanelname",
#             body={
#                 "query": {
#                     "match": {
#                         "_id": handlename
#                     }
#                 }
#             }
#         )

#         hits = response.get("hits", {}).get("hits", [])
#         likes_handle_name = hits[0]["_source"]["followers"][6]
#         handle_list = []
        
       

        
#         # flat_list = [item for sublist in likes_handle_name for item in sublist]
#         # if(flat_list) :
#         scrap_data(likes_handle_name,0,0)
           
#         # print(f"handle_list : {flat_list}")

        
#         # print(f"handle_list : {handle_list}")

#     except Exception as e:
#         print(f"Error in scrapDataForInsight: {e}")

        
        
# def get_post_likes_handle_name(driver, url):
#     try : 
#         driver.get(url)
#         time.sleep(random.uniform(2,3))
#         handles = []
#         for i in range(1, 100):
#             try:
#                 xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div[1]/div/div[{i}]/div/div/div/div[2]/div/div/div/div/span/div/a/div/div/span"
#                 element = driver.find_element(By.XPATH, xpath)
#                 handles.append(element.text)
#             except:
#                 continue
#         return handles
#     except Exception as e:
#         return f"Error in creating the driver1: {e}" 
    
# def findPostLikesHandleName(handlename):
#     print(f"handle : {handlename}")
    
#     try:
#         response = client1.search(
#             index="instagram_posts",
#             body={
#                 "query": {
#                     "match": {
#                         "handle": handlename
#                     }
#                 }
#             }
#         )
        
#         hits = response.get("hits", {}).get("hits", [])

#         print(f"hnadle_name : {hits}")
        
#         handle_list = []

#         if hits:
#             driver = create_Driver()
#             print(f"driver : {driver}")
#             if driver:
#                 for hit in hits:
#                     source = hit.get("_source", {})
#                     url = source.get('url', '')
#                     print(f"url : {url}")

#                     if url:
#                         likesUrl = convert_to_liked_by(url)
#                         try:
#                             print(f"likesd : {likesUrl}")
#                             handle = get_post_likes_handle_name(driver,likesUrl)
#                         except Exception as e:
#                             print(f"error in getting data {e}")
#                         time.sleep(random.randint(5, 9))
                        
#                         if handle:
#                             handle_list.append(handle)
#         else:
#             print(f"No data found")
        
#         driver.quit()
        
#         try:
#             print(f"handlelist len before : {len(handle_list)}")
#             handle_list = analyze_account(handle_list,'')
#             print(f"handlelist len after: {len(handle_list)}")
#         except Exception as e:
#             print(f"Error in filter handle name : {e}")
        
#         try:
#            client1.index(
#                 index="posts_likes_hanelname",
#                 id=handlename,
#                 body={
#                     "username": handlename,
#                     "followers": handle_list
#                 }
#             )
#         except Exception as e:
#             print(f"Error in adding the data : {e}")
            

#     except Exception as e:
#          print(f"Error in getting the handle name: {e}")
    
# findPostLikesHandleName("riyasendv")

# scrapDataForInsight("riyasendv")


# def getCommentsData():
   
#     comments = [
#         {
#             "post_id": "post_123",
#             "text": "this is awesome",
#             "commentor": "riyasenv",
#             "likes": 12,
            
#         },
#         {
#             "post_id": "post_123",
#             "text": "great",
#             "commentor": "virat.kohli",
#             "likes": 22,
            
#         },
#         {
#             "post_id": "post_123",
#             "text": "nice one",
#             "commentor": "thefoodieshub",
#             "likes": 44,
            
#         }
#     ]

#     # Prepare for bulk ingestion
    # actions = [
    #     {
    #         "_index": "posts_comments_index",
    #         "_source": comment
    #     }
    #     for comment in comments
    # ]
    
#     response = helpers.bulk(client1, actions)
#     print("Bulk insert response:", response)
    
    

=======
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
    
>>>>>>> 545368e94f890cf7ac229226e8815e91b3669134
