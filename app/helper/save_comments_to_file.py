from app.utils.convert_relative_time import convert_relative_time
from app.services.opensearch_client import client
from opensearchpy import OpenSearch, helpers


def save_comments_to_file(comments,post_id, filename="instagram_comments.json"):
    """Clean, parse, and save comments to a structured JSON file"""
    try:
        all_cleaned_comments = []
        seen_comments = set()  # Track unique (username, comment) pairs
        
        for comment_block in comments:
            # Process each raw comment block
            if "comment" in comment_block and isinstance(comment_block["comment"], str):
                # First, try to extract just the main comment from the block
                raw_text = comment_block["comment"]
                
                # First try to get just the main comment by looking for patterns
                lines = raw_text.split('\n')
                
                # Basic structure: possible timestamp, comment text, likes count
                if len(lines) >= 3:
                    username = comment_block.get("username", "")
                    
                    # First line might be timestamp (e.g., "9w")
                    timestamp = ""
                    if len(lines[0]) <= 3 and any(char in lines[0] for char in "wdhms"):
                        timestamp = lines[0].strip()
                        # Remove timestamp line
                        lines = lines[1:]
                    
                    # Extract likes if present in a line
                    likes = ""
                    for i, line in enumerate(lines):
                        if "likes" in line and any(c.isdigit() for c in line):
                            likes_text = line.strip()
                            # Extract just the number from likes
                            import re
                            likes_match = re.search(r'(\d+)\s*likes', likes_text)
                            if likes_match:
                                likes = likes_match.group(1)
                            # Remove likes line
                            lines.pop(i)
                            break
                    
                    # Remaining lines before "Reply" are the comment text
                    comment_text = ""
                    for i, line in enumerate(lines):
                        if line.strip() == "Reply" or "View all" in line:
                            break
                        comment_text += line + " "
                    
                    comment_text = comment_text.strip()
                    
                    # Only add if we have valid comment text
                    if comment_text and username:
                        # Create a unique identifier for deduplication
                        unique_id = (username, comment_text)
                        if unique_id not in seen_comments:
                            seen_comments.add(unique_id)
                            all_cleaned_comments.append({
                                "username": username,
                                "comment": comment_text,
                                "likes": likes,
                                "timestamp" : convert_relative_time(timestamp)
                            })
        
        # Now also process the raw text to extract nested replies
        for comment_block in comments:
            if "comment" in comment_block and isinstance(comment_block["comment"], str):
                raw_text = comment_block["comment"]
                lines = raw_text.split('\n')
                
                # Process multiline text to find replies
                i = 0
                while i < len(lines):
                    # Look for username followed by timestamp pattern
                    if i+1 < len(lines) and len(lines[i].strip()) > 0:
                        potential_username = lines[i].strip()
                        # Check if next line could be a timestamp
                        if i+1 < len(lines) and re.match(r'^\s*\d+[wdhms]\s*$', lines[i+1]):
                            timestamp = lines[i+1].strip()
                            comment_start = i + 2
                            
                            # Look for the end of this comment (next username or end)
                            comment_end = comment_start
                            while comment_end < len(lines):
                                if "likes" in lines[comment_end] or "Reply" in lines[comment_end]:
                                    break
                                comment_end += 1
                            
                            # Extract the comment text
                            comment_lines = lines[comment_start:comment_end]
                            if comment_lines:
                                comment_text = ' '.join(comment_lines).strip()
                                
                                # Extract likes if present
                                likes = ""
                                if comment_end < len(lines) and "likes" in lines[comment_end]:
                                    likes_text = lines[comment_end]
                                    likes_match = re.search(r'(\d+)\s*likes', likes_text)
                                    if likes_match:
                                        likes = likes_match.group(1)
                                
                                # Only add if we have valid data
                                if potential_username and comment_text:
                                    unique_id = (potential_username, comment_text)
                                    if unique_id not in seen_comments:
                                        seen_comments.add(unique_id)
                                        all_cleaned_comments.append({
                                            "username": potential_username,
                                            "comment": comment_text,
                                            "timestamp": timestamp,
                                            "likes": likes
                                        })
                    i += 1
        
        # Remove duplicates again (just to be safe)
        final_comments = []
        seen = set()
        for comment in all_cleaned_comments:
            unique_id = (comment["username"], comment["comment"])
            if unique_id not in seen:
                seen.add(unique_id)
                final_comments.append(comment)
        
        # with open(filename, 'w', encoding='utf-8') as f:
        #     json.dump(final_comments, f, ensure_ascii=False, indent=4)
        # print(f"Comments successfully saved to {filename}")
        
        # Print sample of structured comments for verification
        # if final_comments:
        #     print("\nSample of extracted comments:")
        #     for i, comment in enumerate(final_comments[:5]):
        #         print(f"{i+1}. User: {comment['username']}")
        #         print(f"   Comment: {comment['comment']}")
        #         print(f"   Time: {comment.get('timestamp', 'N/A')}")
        #         print(f"   Likes: {comment.get('likes', 'N/A')}")
        #         print("---")
        
        try:
            actions = [
                {
                    "_index": "posts_comments_index",
                    "_source": {
                        "post_id": post_id,
                        **comment
                    }
                }
                for comment in final_comments
            ]

            
            response = helpers.bulk(client, actions, request_timeout=60)
        except Exception as e:
            print(f"Error in saving data in database {e}")
        
      
        return final_comments
    except Exception as e:
        print(f"Error saving comments to file: {e}")
        import traceback
        traceback.print_exc()
        return []