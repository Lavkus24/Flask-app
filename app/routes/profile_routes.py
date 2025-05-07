from flask import Blueprint, request, jsonify
from app.helper.get_profile_data import get_profile_data



search_bp = Blueprint("profile", __name__)


@search_bp.route('/instagram_profiles/_search',methods=['GET'])
def search_instagram_profile():
        username = request.json.get("handlename")
        if not username:
            return jsonify({"error": "Invalid query structure"}), 400

        result = get_profile_data(username)

        
        
        return jsonify({
            "result":result
        })