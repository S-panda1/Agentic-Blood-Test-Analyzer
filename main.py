import os
import uuid
import traceback
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from crewai import Crew, Process
from agents import doctor, nutritionist, exercise_specialist, verifier
from task import help_patients, nutrition_analysis, exercise_planning, verification
from db import init_db, SessionLocal, AnalysisResult

import logging
logging.basicConfig(level=logging.INFO)

# Load environment variables (API keys, etc.)
load_dotenv()

# Create FastAPI instance
app = FastAPI(title="Blood Test Report Analyser")

# Mount static directory for HTML
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

# Create output directory for file uploads
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize SQLite DB schema
init_db()

def run_crew(query: str, file_path: str) -> dict:
    """Executes the CrewAI agent workflow and collects all outputs safely."""
    
    def safe_output(task, name):
        try:
            return str(task.output)
        except Exception as e:
            logging.warning(f"[ERROR] {name} failed: {e}")
            return f"Failed to generate {name} output."

    crew = Crew(
        agents=[verifier, doctor, nutritionist, exercise_specialist],
        tasks=[verification, help_patients, nutrition_analysis, exercise_planning],
        process=Process.sequential,
        verbose=True
    )

    try:
        crew.kickoff(inputs={"query": query, "file_path": file_path})
    except Exception as e:
        logging.critical(f"[CRITICAL] Crew execution failed: {e}")
        return {
            "status": "error",
            "query": query,
            "error": f"Crew execution failed: {e}"
        }

    return {
        "status": "success",
        "query": query,
        "verifier": safe_output(verification, "verifier"),
        "doctor": safe_output(help_patients, "doctor"),
        "nutrition": safe_output(nutrition_analysis, "nutrition"),
        "exercise": safe_output(exercise_planning, "exercise")
    }

@app.get("/")
async def root():
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(OUTPUT_DIR, f"blood_test_report_{file_id}.pdf")

    try:
        # Save file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            f.write(content)

        if not query.strip():
            query = "Summarise my Blood Test Report in detail and provide health recommendations."

        # Run CrewAI pipeline
        result = run_crew(query=query.strip(), file_path=file_path)

        # Save result to SQLite
        session = SessionLocal()
        record = AnalysisResult(
            file_name=file.filename,
            query=query,
            result=str(result),
            user_id=None
        )
        session.add(record)
        session.commit()
        session.close()

        return {
            "status": "success",
            "query": query.strip(),
            "analysis": result,
            "file_processed": file.filename
        }

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")

    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            logging.warning(f"Error removing file: {e}")

@app.get("/history")
def get_analysis_history():
    """Returns a list of previous report analyses from the database."""
    session = SessionLocal()
    records = session.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()
    session.close()

    return [
        {
            "id": record.id,
            "file_name": record.file_name,
            "query": record.query,
            "created_at": record.created_at.isoformat(),
            "result": record.result
        }
        for record in records
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
