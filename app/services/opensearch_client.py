from opensearchpy import OpenSearch
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

client = OpenSearch(
    hosts=[os.getenv("HOST_URL")],
    http_auth=(os.getenv("USER_NAME"), os.getenv("PASSWORD")),
)
