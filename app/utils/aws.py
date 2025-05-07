import json
import asyncio
import re
from datetime import datetime
from opensearchpy import OpenSearch, NotFoundError
import os
from dotenv import load_dotenv
load_dotenv()

def parse_number(value):
    
    value = value.replace(",", "")
    if value.endswith("M"):
        return int(value[:-1]) * 1_000_000
    elif value.endswith("K"):
        return int(value[:-1]) * 1_000
    elif value.endswith("B"):
        return int(value[:-1]) * 1_000_000_000
    else:
        return int(value) 

user_name = os.getenv("USER_NAME")
user_password = os.getenv("PASSWORD")
host_url = os.getenv("HOST_URL")

client = OpenSearch(
    hosts=[host_url],
    http_auth=(user_name, user_password),
)

async def extract_post_id(url):
    """Extracts the post ID from the given Instagram URL."""
    match = re.search(r"/(p|reel)/([^/]+)/", url)
    return match.group(2) if match else None


def extract_username(url):
    match = re.match(r"https://www\.instagram\.com/([^/]+)/", url)
    return match.group(1) if match else None


async def update_instagram_profiles(data):
    try:
        username = data.get("username")
        followers = data.get("followers")
        posts_count = data.get("posts_count")
        hashtags = data.get("hashtags")
        mentions = data.get("mentions")

        
        stats_data = {
            "username": username,
            "followers": followers,
            "posts_count": posts_count,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            client.index(
                index="instagram_profile_stats",
                body=stats_data
            )
        except  Exception as e:
            print(f"Error in saving stats data")
            
        
            
        try : 
            client.index(
                index="discovery_data",
                id=username,  
                body=data
            )
        except Exception as e:
            print(f"Error in saving data on db {e}")
            
    
        response =  client.search(
            index="discovery_data",
            body={
                "query": {
                    "match": {
                        "handle": username
                    }
                }
            }
        )

        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return  
        
        existing_id = hits[0].get("_id")
        existing_data = hits[0].get("_source", {})
        
        updated_data = {
            "followers": parse_number(followers),
            "posts": parse_number(posts_count),
            "hashtags": hashtags,
            "mentions": mentions,
        }

        client.update(
            index="discovery_data",
            id=existing_id,
            body={
                "doc": updated_data,
                "doc_as_upsert": True  # Create document if it doesn’t exist
            }
        )
    
        print(f"Updated Instagram profile: {username}")

    except Exception as e:
        print(f"Error updating: {e}")
        
async def add_influencers_followers(data,username):
    try:
        
        if isinstance(data, set):
            data = {"followers_list": list(data)}
       
        print(f"username : {username}")
        client.index(
            index="influencer-followers",
            id=username,  
            body=data
        )

    except Exception as e:
        print(f"Error storing : {e}")

async def store_hashtag_mentions(hashtags_lists, mentions_lists, handle):
  
    try:
        # Flatten the nested lists and remove duplicates using set()
        merged_hashtags = list(set([tag for sublist in hashtags_lists for tag in sublist]))
        merged_mentions = list(set([mention for sublist in mentions_lists for mention in sublist]))

        # ✅ Await the async OpenSearch update operation
        try:
            client.update(
                index='hashtags_mentions',
                id=handle,
                body={
                    "doc": {
                        "hashtags": merged_hashtags,
                        "mentions": merged_mentions
                    },
                    "doc_as_upsert": True  
                }
            )
            print(f"successfully stored hastag and mentions {handle}")
        except Exception as e:
            print(f"Error in storing hastag and mentions {handle}")

    except Exception as error:
        print("Error storing hashtags and mentions in OpenSearch:", error)
        
        
async def store_post_data_in_opensearch(batch_results):
    """Stores post data in OpenSearch."""
   
    try:
        tasks = []
        hashtags_lists = []
        mentions_lists = []
        handle = ""

        for data in batch_results:
            url = data.get("url", "")
            post_id = await extract_post_id(url)

            hashtags_lists.append(data.get("hashtags", ""))  # ✅ Fix append syntax
            mentions_lists.append(data.get("mentions", ""))  

            # Store the first non-empty handle
            if not handle:
                handle = extract_username(url)
            
            data['handle'] = handle
            
            if post_id:
                client.index(  # ✅ Use async function correctly
                    index="instagram_posts",
                    body=data,
                    id=str(post_id)
                )
        
        if handle:
            await store_hashtag_mentions(hashtags_lists, mentions_lists, handle)

    except Exception as error:
        print("Error storing data in OpenSearch:", error)


async def addInfluencerLikes(handles,username):
    
    print(f"handles : {handles}, username : {username}")
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
    
    return "success"
        
