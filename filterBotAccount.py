import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import numpy as np
import re
from scipy.special import softmax
tokenizer = None
model = None

def polarity_scores(example):
    global tokenizer, model
    
    # Ensure model is loaded
    if tokenizer is None or model is None:
        return {"error": "Model not loaded"}
    
    encoded_text = tokenizer(example, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'Negative': scores[0],
        'Neutral': scores[1],
        'Positive': scores[2]
    }
    return scores_dict

def convert_to_serializable(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    return obj

def analyze_comments_sentiment():
    try:
        # Check if model is loaded
        if tokenizer is None or model is None:
            return jsonify({"error": "Sentiment model not loaded properly"}), 500
            
        # Get comments from request
        comments = request.json['comments']
        
        # Store sentiment counts
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        total_comments = len(comments)
        
        # Analyze each comment
        for comment in comments:
            # Skip empty comments
            if not comment.strip():
                total_comments -= 1
                continue
                
            # Get sentiment scores
            sentiment_result = polarity_scores(comment)
            
            # Check for errors
            if "error" in sentiment_result:
                return jsonify(sentiment_result), 500
            
            # Determine dominant sentiment
            max_sentiment = max(sentiment_result, key=sentiment_result.get)
            
            # Increment counter
            sentiment_counts[max_sentiment] += 1
        
        # Calculate percentages
        sentiment_percentages = {
            sentiment: (count / total_comments * 100) if total_comments > 0 else 0 
            for sentiment, count in sentiment_counts.items()
        }
        
        # Return the results
        return jsonify({
            "total_comments_analyzed": total_comments,
            "sentiment_counts": convert_to_serializable(sentiment_counts),
            "sentiment_percentages": convert_to_serializable(sentiment_percentages)
        })
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

def extract_features_from_handle_and_bio(username, bio):
    # Feature 1: nums/length username
    total_chars = len(username)
    num_digits = sum(c.isdigit() for c in username)
    nums_len_username = num_digits / total_chars if total_chars > 0 else 0.0

    # Feature 2: description length
    description_length = len(bio)

    # Feature 3: external URL (presence of a URL in bio)
    url_pattern = r'https?://|www\.'
    external_url = 1 if re.search(url_pattern, bio) else 0


    return {
        "nums_len_username": round(nums_len_username, 2),
        "description_length": description_length,
        "external_url": external_url
    }
    
def analyze_account(username, bio):
    try:
        
        handleList = []
        for user in username:
            features = extract_features_from_handle_and_bio(username, bio)
            is_fake = (
                features["nums_len_username"] > 0.4 or  # suspicious if many numbers
                features["description_length"] < 10      # very short bio
            )

            features["fake_prediction"] = int(is_fake)
            if int(is_fake) < .5 : 
                handleList.append(user)
                
        
        return handleList

    except Exception as e:
        return jsonify({"error": str(e)}), 500