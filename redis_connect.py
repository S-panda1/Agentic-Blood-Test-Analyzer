# redis_connect.py
from redis import Redis
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()
url = urlparse(os.getenv("REDIS_URL"))

redis_conn = Redis(
    host=url.hostname,
    port=url.port,
    password=url.password
)
