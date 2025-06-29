# db.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()
engine = create_engine("sqlite:///output/analysis.db")
SessionLocal = sessionmaker(bind=engine)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String)
    query = Column(String)
    result = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True)  # Optional for future auth support

def init_db():
    Base.metadata.create_all(bind=engine)
