import json
import asyncio
import re
from opensearchpy import OpenSearch

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

client = OpenSearch(
    hosts=["https://search-scraping-data-sqjdyrnbfijveyo3fr3lc6y24m.ap-south-1.es.amazonaws.com"],
    http_auth=("Lavkus", "Lavkus@#1212"),
)

async def update_instagram_profiles(data):
    try:
        username = data.get("username")
        followers = data.get("followers")
        posts_count = data.get("posts_count")
        hashtags = data.get("hashtags")
        mentions = data.get("mentions")
        
 
        client.index(
            index="instagram_profiles",
            id=username,  
            body=data
        )
    
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



async def extract_post_id(url):
    """Extracts the post ID from the given Instagram URL."""
    match = re.search(r"/(p|reel)/([^/]+)/", url)
    return match.group(2) if match else None

def extract_username(url):
    match = re.match(r"https://www\.instagram\.com/([^/]+)/", url)
    return match.group(1) if match else None

async def store_hashtag_mentions(hashtags_lists, mentions_lists, handle):
    """Stores hashtags and mentions in OpenSearch."""
    try:
        # Flatten the nested lists and remove duplicates using set()
        merged_hashtags = list(set([tag for sublist in hashtags_lists for tag in sublist]))
        merged_mentions = list(set([mention for sublist in mentions_lists for mention in sublist]))

        # ✅ Await the async OpenSearch update operation
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
        print(f"Successfully stored hashtags and mentions for {handle}")

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
              
        print(f"handle ; {handle}")
        
        if handle:
            await store_hashtag_mentions(hashtags_lists, mentions_lists, handle)

    except Exception as error:
        print("Error storing data in OpenSearch:", error)

        
        
