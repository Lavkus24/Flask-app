from flask import Blueprint, request, jsonify
# from app.utils.scraping_utils import scrap_data
import threading
import os
from opensearchpy import OpenSearch
from dotenv import load_dotenv
from app.services.opensearch_client import client
from app.utils.scraping_utils import threaded_scraping


load_dotenv()

scraping_bp = Blueprint("scraping", __name__)



# POST /api/v1/scrapdata1
@scraping_bp.route("/v1/scrapdata1", methods=["POST"])
def handle_handle_name():
        index_name = "instagram_handle"
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data received"}), 400

            start = data.get('start')
            size = data.get('size')
            cookie_list=data.get('cookie_list')

            all_hits = []
            batch_size = 1000
            scroll_time = "2m"
            skip_batches = start // batch_size
            required_docs = size

            # Initial search to get the scroll ID
            response = client.search(
                index=index_name,
                scroll=scroll_time,
                size=batch_size,
                body={"query": {"match_all": {}}}
            )

            scroll_id = response.get('_scroll_id')
            hits = response.get('hits', {}).get('hits', [])

            if not scroll_id:
                return jsonify({"error": "Failed to obtain scroll_id"}), 500
            if not hits:
                return jsonify({"error": "No data found in initial scroll"}), 404

            batch_count = 0

            while True:
                batch_count += 1
                if batch_count > skip_batches:
                    all_hits.extend(hits)
                    if len(all_hits) >= required_docs:
                        break

                response = client.scroll(scroll_id=scroll_id, scroll=scroll_time)
                scroll_id = response.get('_scroll_id')
                hits = response.get('hits', {}).get('hits', [])

                if not hits:
                    return jsonify({"error": "Failed to retrieve more data from Elasticsearch"}), 404

            # Clean up scroll
            client.clear_scroll(scroll_id=scroll_id)

            # Prepare handle list
            handle_list = []
            for item in all_hits[:required_docs]:
                try:
                    handle_list.append(item['_source']['handle'].rstrip(","))
                except KeyError:
                    continue  # Skip any document missing 'handle'

            if not handle_list:
                return jsonify({"error": "No handles found in the selected range"}), 404

            thread = threading.Thread(target=threaded_scraping, args=(handle_list,start,size,cookie_list), daemon=True)
            thread.start()

            return jsonify({
                "status": "success",
                "message": "Data scraping started",
                "handle_count": handle_list
            }), 200

        except Exception as e:
            print(f"Exception occurred: {e}")
            return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500