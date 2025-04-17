from flask import request, jsonify
from logic import process_data
from scrapProfile import scrap_data, findPostLikesHandleName, scrapDataForInsight
import threading
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=["https://search-scraping-data-sqjdyrnbfijveyo3fr3lc6y24m.ap-south-1.es.amazonaws.com"],
    http_auth=("Lavkus", "Lavkus@#1212"),
)

def threaded_scraping(data_set,start,size):
    try:
        print(f"data_set  : {data_set}")
        scrap_data(data_set,start,size)
    except Exception as e:
        print(f"Error in thread: {e}")
        
def configure_routes(app):
    @app.route("/api/scrapedata", methods=["POST"])
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
            return jsonify({"error": str(e)}), 500  # Return error message if API fail

    @app.route("/api/v1/scrapdata1", methods=["POST"])
    def handle_handle_name():
        index_name = "instagram_handle"
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data received"}), 400

            start = data.get('start')
            size = data.get('size')

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

            thread = threading.Thread(target=threaded_scraping, args=(handle_list,start,size), daemon=True)
            thread.start()

            return jsonify({
                "status": "success",
                "message": "Data scraping started",
                "handle_count": handle_list
            }), 200

        except Exception as e:
            print(f"Exception occurred: {e}")
            return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

        
    @app.route('/api/v1/findPostHandle', methods=["POST"])
    def findLikesHandleData():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400

            handlename = data.get('handlename')
        
            if not handlename:
                return jsonify({"error": "handlename is required"}), 400
            
            findPostLikesHandleName(handlename)
            
            return jsonify({"message" : "gettng the data"})

        except Exception as e:
            return jsonify({"error": f"Error in finding the post: {str(e)}"}), 500
    @app.route('/api/v1/findComments', methods=["POST"])
    def findCommentsData():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400

            posturl = data.get('url')
        
            if not posturl:
                return jsonify({"error": "handlename is required"}), 400
            
            # getCommentsData(posturl)
            
            return jsonify({"message" : "gettng the data"})

        except Exception as e:
            return jsonify({"error": f"Error in finding the post: {str(e)}"}), 500
        
    @app.route('/api/v1/findInsight', methods=["POST"])
    def findLoacationData():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400

            username = data.get('username')
        
            if not username:
                return jsonify({"error": "handlename is required"}), 400
            
            scrapDataForInsight(username)
            
            return jsonify({"message" : "gettng the data"})

        except Exception as e:
            return jsonify({"error": f"Error in finding the post: {str(e)}"}), 500
            

