from flask import Blueprint, request, jsonify
from app.helper.fetch_instagram_comments import fetch_instagram_comments



comments_bp = Blueprint("comment", __name__)

@comments_bp.route("/getCommentsData", methods=["GET"])
def get_comments_data():
        post_id = request.json.get("post_id")
        if not post_id:
            return jsonify({"error": "post_id is required"}), 400

        comments = fetch_instagram_comments(post_id)


        return jsonify({
            "post_id": post_id,
            "comments": comments
        })