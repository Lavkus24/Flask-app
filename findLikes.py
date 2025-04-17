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
import json

from opensearchpy import OpenSearch, NotFoundError

client = OpenSearch(
    hosts=["https://search-scraping-data-sqjdyrnbfijveyo3fr3lc6y24m.ap-south-1.es.amazonaws.com"],
    http_auth=("Lavkus", "Lavkus@#1212"),
)

def findHashtagAnsMentions(handle_list):
    hashtag_list = []

    for handle_name in handle_list:
        response = client.search(
            index="hashtags_mentions",
            body={
                "query": {
                    "match": {
                        "_id": handle_name
                    }
                }
            }
        )

        hits = response.get("hits", {}).get("hits", [])
        for hit in hits:
            hashtags = hit.get("_source", {}).get("hashtags", [])
            mentions = hit.get("_source", {}).get("mentions", [])
            hashtag_list.extend(hashtags)  # Add all hashtags to the final list
            hashtag_list.extend(mentions)  # Add all hashtags to the final list
    
    print(f"List of hashtagandmentions : {hashtag_list}")
    return hashtag_list
# https://www.instagram.com/p/DHyIoy0peKz/liked_by
# https://www.instagram.com/p/DIBQ0hLztzz/liked_by

def get_profile_data(driver):
    try : 
        driver.get(f"https://www.instagram.com/p/DHyIoy0peKz/liked_by/?hl=en")
        time.sleep(random.uniform(2,3))
        handles = []
        for i in range(1, 100):
            try:
                xpath = f"/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div[1]/div/div[{i}]/div/div/div/div[2]/div/div/div/div/span/div/a/div/div/span"
                element = driver.find_element(By.XPATH, xpath)
                handles.append(element.text)
            except:
                continue
            
        username = "riyasendv"
        try:
            existing_doc = client.get(index="instagram_profiles", id=username)
            existing_followers = existing_doc['_source'].get('followers', [])
            updated_followers = list(set(existing_followers + handles)) 
            client.update(
                index="posts_likes_hanelname",
                id=username,
                body={
                    "doc": {
                        "followers": updated_followers
                    }
                }
            )

        except NotFoundError:
            # If document doesn't exist, create a new one
            client.index(
                index="posts_likes_hanelname",
                id=username,
                body={
                    "username": username,
                    "followers": handles
                }
            )
        return handles
        
    except Exception as e:
        return f"Error in creating the driver1: {e}" 
    
def create_Driver():
    try:
        driver_path = "C:/Program Files/chrome-new-driver/chromedriver-win64/chromedriver.exe"
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service)
        
        
        driver.get("https://www.instagram.com/")

        cookiesList = [
        
            {'name': 'sessionid', 'value': '72526559706%3ATTGNNZ39L1u7xD%3A7%3AAYejAbfSthyZ_8HKJ3NkDoueJ7VIDQdZ7Vop3qZF64'},
            
            
        ]
        
        tempList = cookiesList.copy()  # Create a temporary list
        
        for cookie in tempList[:]:  # Iterate over a copy of tempList
            print(f"cookie12 : {cookie}")
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
    except Exception as e:
        return f"Error in creating the driver:2 {e}" 



def scrap_data() :
   
    driver = create_Driver()
    if(driver):
        print(f"session id is working")
        profile_data = get_profile_data(driver)
        print(json.dumps(profile_data))
        driver.quit()



scrap_data()


# "vincentkhokhar", "koooustav", "raajveer2071", "ss.srinivasan8143",  "hattrik17", "iamdk_xo", "rituraj8681", "mohsinshaikh_z1", "shreyashhh_03", "meshii_mesh", "lets_talkpeople", "pankaj_0545", "shakilkhaansk2", "ubed.768", "narzaryjonksar",  "faysal_muntasir", "lloydclarke0007", "dloins", "sunny_kamble__sandi", "raj_mysore", "veer.agrawal.54",  "ravipargir","rone.rock", "sanjay._diwan", "_zammy__1", "aru_thecrackedkidz","kritarthatiwari",  "hemant_buddhiwant", "rehans8270", "savan_bharoliya", "mohsinkhan786101",  "vipi__rohan", "saiyed_photo_studio_","itz_aayat", "kiccha_bharath", "gorgeouscolleen", "arebelsvoice", "dhairy_31", "kolkatamagazine"