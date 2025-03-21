from flask import request, jsonify
from logic import process_data
from scrapProfile import scrap_data
from data_store import data
# import threading
# def async_scrap():
#     for batch in data:
#         scrap_data("thefoodieshub")


def configure_routes(app):
    @app.route("/api/data", methods=["POST"])
    def handle_data():
        if not request.is_json:
            return jsonify({"error": "Invalid Content-Type, use application/json"})
        
        data1 = request.get_json()  # Get JSON data safely
        response = process_data(data1)
        return jsonify(response)
    
    @app.route("/api/data1", methods=["GET"])
    def handle_get():

        # thread = threading.Thread(target=async_scrap)
        # thread.start()
        # for batch in data :
        scrap_data("thefoodieshub")
        sample_data = {
            "message": "Welcome to the API!",
            "status": "success"
        }
        
        return jsonify(sample_data) 