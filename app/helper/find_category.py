categories = {
    'Automotive': ['car', 'vehicle', 'engine', 'motor', 'automobile'],
    'Beauty & Make-up': ['beauty', 'makeup', 'cosmetics', 'skincare'],
    'Family & Parenting': ['parenting', 'family', 'children', 'kids'],
    'Health & Wellness': ['health', 'wellness', 'fitness', 'mental health'],
    'Fitness & Yoga': ['fitness', 'yoga', 'exercise', 'workout'],
    'Food & Cooking': ['food', 'cooking', 'recipe', 'meal'],
    'Travel': ['travel', 'vacation', 'trip', 'holiday', 'tour'],
    'Fashion & Lifestyle': ['fashion', 'style', 'clothing', 'lifestyle'],
    'Tech, Gadgets & Electronics': ['technology', 'gadget', 'electronics', 'tech'],
    'Student & Education': ['education', 'student', 'school', 'learning'],
    'Gaming': ['gaming', 'video game', 'gamer', 'play'],
    'Music & Dance': ['music', 'dance', 'song', 'melody'],
    'Movies & Television': ['movie', 'film', 'tv', 'television'],
    'Sports': ['sports', 'soccer', 'basketball', 'football', 'athlete'],
    'Home & Garden': ['home', 'garden', 'decoration', 'interior'],
    'Pets': ['pets', 'dog', 'cat', 'animal'],
    'Personal Finance & Investing': ['finance', 'investing', 'stock', 'money'],
    'Books & Literature': ['book', 'reading', 'novel', 'literature'],
    'Business & Careers': ['business', 'career', 'startup', 'entrepreneur'],
    'Science & Technology': ['science', 'tech', 'innovation', 'research'],
    'Hobbies, DIY & Interests': ['hobby', 'DIY', 'craft', 'interest'],
    'Photography': ['photo', 'photography', 'camera', 'picture'],
    'Art': ['art', 'painting', 'drawing', 'artist'],
    'Social Causes': ['cause', 'social', 'charity', 'activism']
}

def find_category(captions, hashtags, mentions):
    # Ensure inputs are lists, replacing None with empty lists
    captions = captions or []
    hashtags = hashtags or []
    mentions = mentions or []

    category_count = {category: 0 for category in categories}
    
    # Combine all captions, hashtags, and mentions into one list
    all_text = captions + hashtags + mentions
    
    # Loop through each category and check if any keyword exists in the text
    for category, keywords in categories.items():
        for keyword in keywords:
            for text in all_text:
                if isinstance(text, str) and keyword.lower() in text.lower():
                    category_count[category] += 1

    suitable_category = max(category_count, key=category_count.get)
    
    return suitable_category if category_count[suitable_category] > 0 else 'N/A'


# geoffreyjames ,  
# "geoffreyjames",
# "iamhadleykay",
# "enjoi",
# "gepjpeg",
# "johnny_joness",
# "krooked",
# "rem"