# tasks.py
from redis_connect import redis_conn
from rq import Queue
from db import SessionLocal, AnalysisResult
from main import run_crew

queue = Queue(connection=redis_conn)

def analyze_and_store(file_path: str, query: str, file_name: str):
    result = run_crew(query=query, file_path=file_path)

    session = SessionLocal()
    db_record = AnalysisResult(
        file_name=file_name,
        query=query,
        result=str(result)
    )
    session.add(db_record)
    session.commit()
    session.close()

    return result