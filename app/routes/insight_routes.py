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



insight_bp = Blueprint("insight", __name__)


@insight_bp.route('/post_insight', methods=['GET'])
def insight_instagram_post():
    post_id = request.json.get("post_id")  # For GET method

    if not post_id:
        return jsonify({"error": "post_id parameter is required"}), 400

    try:
        response = client.search(
            index="instagram_posts",
            body={
                "query": {
                    "match": {
                        "_id": post_id
                    }
                }
            }
        )

        hits = response.get('hits', {}).get('hits', [])
        if not hits:
            return jsonify({"error": "No post found"}), 404

        post_data = hits[0].get('_source', {})
        print(post_data)

        match = re.search(r'instagram\.com/([^/]+)/p/', post_data["url"])
        handle=match.group(1)

        details = client.search(
            index="discovery_data",
            body={
                "query":{
                    "match":{
                        "handle":handle
                    }
                }
            }
        )

        details_hits = details.get("hits", {}).get("hits", [])
        if details_hits:
            discovery_data = details_hits[0].get("_source", {})
            post_data["username"] = discovery_data.get("handle", "")
            post_data["location"] = discovery_data.get("location", "")
            post_data["category"] = discovery_data.get("category", "")
            post_data["followers"]=discovery_data.get("followers", "")

        # Process audience insights
        insights = analyze_audience_insights(post_data)
        cleaned_insights=clean_insights_percentages(insights)
        # Save to files
        
        try:
                    response = client.index(
                        index='reporting_insight',
                        id=post_data["username"],
                        body=cleaned_insights
                    )
                    print(f"Response : {response}")

                    if response['_shards']['successful'] > 0:
                        print(f"Data is stored successfully for {response['_id']}")
                    else:
                        print("Data storage failed.")

        except Exception as e:
                    print(f"Error in storing the response {e}")

        print("Audience insights:")
        print(json.dumps(insights, indent=2, ensure_ascii=False))

        return jsonify({
            "post_data": post_data,
            "insights": cleaned_insights
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500