# worker.py
import os
from dotenv import load_dotenv
load_dotenv()

from tasks import queue  # triggers Redis connection via redis_connect.py

if __name__ == "__main__":
    import rq
    from redis_connect import redis_conn
    from rq import Worker

    Worker(["default"], connection=redis_conn).work()
