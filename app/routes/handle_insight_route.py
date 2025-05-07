import os
import re
import requests
import json
from flask import Blueprint, request, jsonify
from opensearchpy import OpenSearch, NotFoundError
from app.helper.get_post_insight import analyze_audience_insights
from dotenv import load_dotenv
load_dotenv()

user_name = os.getenv("USER_NAME")
user_password = os.getenv("PASSWORD")
host_url = os.getenv("HOST_URL")

client = OpenSearch(
    hosts=[host_url],
    http_auth=(user_name, user_password),
)


def clean_insights_percentages(insights):
    def remove_percent(value):
        try:
            if isinstance(value, str) and value.endswith('%'):
                return float(value.strip('%'))
            elif isinstance(value, dict):
                return {k: remove_percent(v) for k, v in value.items()}
            return value
        except:
            return value

    return {k: remove_percent(v) for k, v in insights.items()}



handle_insight_bp = Blueprint("handle_insight", __name__)


@handle_insight_bp.route('/profile_insights', methods=['POST'])
def insight_instagram_posts():
    handles = request.json.get("handles")  # Expecting a list

    if not handles or not isinstance(handles, list):
        return jsonify({"error": "handles parameter (list) is required"}), 400

    results = []
    

    for handle in handles:
        try:
            # Get the latest post of this handle from instagram_posts index
            response2 = client.search(
            index='hashtags_mentions',
            body={
        "query": {
            "match": {
                "_id": handle
            }
        }

            }
        )
            profile_response = client.search(
    index="discovery_data",
    body={
        "query": {
            "match": {
                "handle": handle
            }
        }
    }
)

            hits = profile_response.get('hits', {}).get('hits', [])
            if not hits:
                raise ValueError(f"No profile data found for handle: {handle}")

            data = hits[0]["_source"]

        

            hashtags = []
            mentions = []

            hits = response2.get('hits', {}).get('hits', [])
            if hits:
                source = hits[0].get('_source', {})
                hashtags = source.get('hashtags', [])
                mentions = source.get('mentions', [])

            profile_data = {
                'username': data.get('username'),
                'followers': data.get('followers'),
                'category': data.get('category'),
                'location': data.get('location'),
                'mentions' : mentions,
                'hashtags' : hashtags,
                'is_verified': True,
                'caption':''
            }

            # Analyze audience insights
            insights = analyze_audience_insights(profile_data)
            cleaned_insights = clean_insights_percentages(insights)

            # Store in Elasticsearch
            try:
                response = client.index(
                    index='insight_data',
                    id=handle,
                    body=cleaned_insights
                )
                if response['_shards']['successful'] > 0:
                    print(f"Stored successfully for {handle}")
                else:
                    print(f"Storage failed for {handle}")
            except Exception as e:
                print(f"Storage error for {handle}: {e}")

            results.append({
                "handle": handle,
                "profile_data": profile_data,
                "insights": cleaned_insights
            })

        except Exception as e:
            print(f"Error processing handle {handle}: {e}")
            results.append({"handle": handle, "error": str(e)})

    return jsonify(results)
