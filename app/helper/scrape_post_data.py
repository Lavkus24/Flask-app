import re
import time
import random
import requests
import logging
from bs4 import BeautifulSoup
from app.utils.is_within_last_year import is_within_last_year


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