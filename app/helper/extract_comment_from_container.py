from selenium.webdriver.common.by import By

def extract_comments_from_container(driver, container):
    """Extract comments using more specific Instagram selectors"""
    print("Extracting comments with improved selectors...")
    comments = []
    
    # Try different approaches to find comment elements
    approaches = [
        # Approach 1: Direct selector for comment li elements
        lambda: container.find_elements(By.CSS_SELECTOR, "ul > li"),
        
        # Approach 2: Look for comments by text content structure
        lambda: driver.find_elements(By.XPATH, "//div[contains(@role, 'button') and .//span]"),
        
        # Approach 3: Find elements with username and text structure
        lambda: driver.find_elements(By.CSS_SELECTOR, "span._aacl._aaco._aacu._aacx._aad7._aade")
    ]
    
    # Try each approach until we find comments
    for approach_func in approaches:
        try:
            comment_elements = approach_func()
            print(f"Found {len(comment_elements)} potential comment elements")
            
            if comment_elements and len(comment_elements) > 0:
                # Use a more specific extraction approach using JavaScript
                for i, comment_elem in enumerate(comment_elements[:200]):  # Limit to 200 to prevent long runtime
                    try:
                        # Use JavaScript to extract data in a more flexible way
                        comment_data = driver.execute_script("""
                            const el = arguments[0];
                            
                            // Instagram specific approach
                            // Try to find the username element using Instagram's specific structure
                            let usernameEl = el.querySelector('a span, a h2, h2 a, h3, a, span a');
                            if (!usernameEl && el.querySelector('a')) {
                                usernameEl = el.querySelector('a'); // Fallback to any link
                            }
                            
                            // Get username text
                            const username = usernameEl ? usernameEl.textContent.trim() : '';
                            
                            // Extract all text to find the comment
                            let fullText = el.textContent.trim();
                            
                            // Get main comment text (skip username part if found)
                            let commentText = fullText;
                            if (username && fullText.includes(username)) {
                                commentText = fullText.substring(fullText.indexOf(username) + username.length).trim();
                            }
                            
                            // Clean up common patterns in comment text
                            const patterns = ['Reply', 'Like', 'Report', 'View replies', 'See translation'];
                            patterns.forEach(pattern => {
                                if (commentText.includes(pattern)) {
                                    commentText = commentText.replace(pattern, '').trim();
                                }
                            });
                            
                            // Try to extract timestamp
                            let timestamp = '';
                            const timeElements = el.querySelectorAll('time, a[href*="comments"]');
                            for (const elem of timeElements) {
                                const text = elem.textContent.trim();
                                if (/^\\d+[dwmhy]$|^\\d+ [a-z]+$/.test(text)) {
                                    timestamp = text;
                                    break;
                                }
                            }
                            
                            // Look for like count
                            let likes = '';
                            const likeElements = el.querySelectorAll('span, div');
                            for (const elem of likeElements) {
                                const text = elem.textContent.trim();
                                if (/^\\d+ likes?$|^\\d+ like this$/.test(text)) {
                                    likes = text;
                                    break;
                                }
                            }
                            
                            return {
                                username: username || '',
                                comment: commentText || '',
                                timestamp: timestamp || '',
                                likes: likes || ''
                            };
                        """, comment_elem)
                        
                        # Add to comments if both username and comment are present
                        if comment_data and comment_data['username'] and comment_data['comment']:
                            # Further clean up the comment
                            comment_text = comment_data['comment']
                            
                            # Remove timestamp if it appears within the comment
                            if comment_data['timestamp'] in comment_text:
                                comment_text = comment_text.replace(comment_data['timestamp'], '').strip()
                                
                            # Remove username if it appears again in the comment
                            if comment_data['username'] in comment_text:
                                comment_text = comment_text.replace(comment_data['username'], '').strip()
                                
                            # Update with cleaned text
                            comment_data['comment'] = comment_text
                            
                            # Only add if comment is not empty after cleaning
                            if len(comment_data['comment']) > 0:
                                comments.append(comment_data)
                                if len(comments) % 10 == 0:
                                    print(f"Extracted {len(comments)} comments so far...")
                    except Exception as e:
                        print(f"Error processing comment #{i}: {e}")
                        continue
                
                # Break out of approaches loop if we found comments
                if len(comments) > 0:
                    break
        except Exception as e:
            print(f"Error with extraction approach: {e}")
            continue
    
    # If we still have no comments, try a more aggressive approach with XPath
    if len(comments) == 0:
        print("Trying direct XPath targeting...")
        try:
            # Looking specifically for comment structures with any approach
            xpath_comments = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'comment') or .//a[contains(@href, '/p/')]]")
            
            for comment_elem in xpath_comments:
                try:
                    text = comment_elem.text.strip()
                    if text and len(text) > 5:  # Only process non-empty text with reasonable length
                        # Basic split on first line break to separate username and comment
                        parts = text.split('\n', 1)
                        username = parts[0].strip() if len(parts) > 0 else ""
                        comment_text = parts[1].strip() if len(parts) > 1 else text
                        
                        # Only add if we have both username and comment
                        if username and comment_text and username != comment_text:
                            comments.append({
                                'username': username,
                                'comment': comment_text,
                                'timestamp': '',
                                'likes': ''
                            })
                except:
                    continue
        except Exception as e:
            print(f"XPath approach failed: {e}")
    
    print(f"Successfully extracted {len(comments)} comments")
    return comments