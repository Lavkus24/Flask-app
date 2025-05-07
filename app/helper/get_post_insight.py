import json
import requests
import re





def analyze_audience_insights(post_data):
    # Prepare the prompt with the Instagram data
    prompt = f"""
Given the following Instagram post data:
Username: {post_data['username']}
Caption: {post_data['caption']}
Category: {post_data['category']}
Location: {post_data['location']}
Followers: {post_data['followers']}
Mentions: {post_data['mentions']}
Hashtags: {post_data['hashtags']}

Comments:
{json.dumps(post_data.get('comments', []), indent=2)}

Provide six estimates for this post:

 1. "city_distribution": Include the top 5 Indian cities with the highest concentration of followers, and group all remaining followers under "Other". Ensure the total adds up to 100%. Base the distribution on cricket popularity, Virat Kohli’s fan following, and regional demographics — not just population size. All values must be integers (no decimal places).

2. "age_distribution": Use the following buckets: '13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'. The percentages must sum to exactly 100%. All values must be integers.

3. "gender_distribution": Use 'male', 'female' . Ensure this also totals 100%. Values must be integers.

 4. "age_gender_distribution": Break down each age group into a nested object containing integers for 'male' and 'female' percentages. The total of male + female in each group must equal that group’s age percentage from "age_distribution".

5. "authenticity_distribution": Categories should be 'real', 'fake', 'mass_followers', and 'influencer'. These must total 100% and all values should be integers.

6. "interest_distribution": List the top 8 to 15 interest areas among the audience (e.g., sports, fashion, fitness, tech, travel). Assign each a percentage. All percentages must be integers.

Output only the final JSON object. Ensure all numbers are integers and totals for each category are exactly 100%.

Format example:
{{
  "age_group_distribution": {{
    "13-17": "XX.X%",
    "18-24": "XX.X%",
    "25-34": "XX.X%",
    "35-44": "XX.X%",
    "45-54": "XX.X%",
    "55-64": "XX.X%",
    "65+": "XX.X%"
  }},
  "age_gender_distribution": {{
    "13-17": {{
      "male": "XX.X%",
      "female": "XX.X%"
    }},
    "18-24": {{
      "male": "XX.X%",
      "female": "XX.X%"
    }},
    "25-34": {{
      "male": "XX.X%",
      "female": "XX.X%"
    }},
    "35-44": {{
      "male": "XX.X%",
      "female": "XX.X%"
    }},
    "45-54": {{
      "male": "XX.X%",
      "female": "XX.X%"
    }},
    "55-64": {{
      "male": "XX.X%",
      "female": "XX.X%"
    }},
    "65+": {{
      "male": "XX.X%",
      "female": "XX.X%"
    }}
  }},
  "gender_distribution": {{
    "male": "XX.X%",
    "female": "XX.X%"
  }},
  "city_distribution": {{
    "City 1": "XX.X%",
    "City 2": "XX.X%",
    "City 3": "XX.X%",
    "City 4": "XX.X%",
    "City 5": "XX.X%",
    "Others": "XX.X%"
  }}
}}

Ensure values in each category add up to 100% and are reasonable estimates based on the post content and engagement patterns.
"""

    
    # Make request to OpenRouter API with Mistral model
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-site.com",  # Optional
                "X-Title": "ViratFandomInsightGen",       # Optional
            },
            data=json.dumps({
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })
        )
        
        # Extract the response
        response_data = response.json()
        response_text = response_data['choices'][0]['message']['content']
        
        # Try to parse the JSON response
        try:
            # Find JSON in response (in case there's surrounding text)
            json_match = re.search(r'({[\s\S]*})', response_text)
            if json_match:
                json_str = json_match.group(1)
                insights_json = json.loads(json_str)
                return insights_json
            else:
                return {"raw_response": response_text}
        except json.JSONDecodeError:
            return {"raw_response": response_text}
            
    except Exception as e:
        print(f"Error calling Mistral API via OpenRouter: {e}")
        return {"error": str(e)}