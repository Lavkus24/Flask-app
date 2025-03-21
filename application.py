from flask import Flask
from routes import configure_routes
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get PORT from .env (set a default value if not provided)
PORT = int(os.getenv("PORT", 5000))

application = Flask(__name__)

# Register Routes
configure_routes(application)

@application.route('/')
def hello_world():
    return 'Hello World'

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=PORT)
