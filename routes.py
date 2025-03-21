from flask import request, jsonify
from logic import process_data
from scrapProfile import scrap_data
from data_store import data_set

def configure_routes(app):
    @app.route("/api/data", methods=["POST"])
    def handle_data():
        try:
            if not request.is_json:
                return jsonify({"error": "Invalid Content-Type, use application/json"}), 400
            
            data1 = request.get_json()  # Get JSON data safely
            response = process_data(data1)
            return jsonify(response)

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Return detailed error response

    @app.route("/api/data1", methods=["GET"])
    def handle_get():
        try:
            print(f"data_set  : {data_set}")
            for batch in data_set:
                scrap_data(batch)
            
            sample_data = {
                "message": "Welcome to the API!",
                "status": "success"
            }
            return jsonify(sample_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Return error message if API fails
