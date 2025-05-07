from flask import Blueprint, request, jsonify
import threading
from app.utils.scraping_utils import threaded_scraping

# Define the blueprint
handle_get_bp = Blueprint("scraping", __name__)

# Define the function within the blueprint
@handle_get_bp.route("/scrapedata", methods=["POST"])
def handle_get():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files["file"]
        
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
         
        data_file = file.read().decode("utf-8")
        print(f"file : {data_file}")
        thread = threading.Thread(target=threaded_scraping, args=(data_file,), daemon=True)
        thread.start()
        
        sample_data = {
            "status": "success",
            "message": "Data scraping start"        
        }
        return jsonify(sample_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500