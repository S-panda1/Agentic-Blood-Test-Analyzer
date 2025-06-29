# 🧪 Blood Test Analyzer (CrewAI Prototype)

This project is a **barebones prototype** built with [CrewAI](https://github.com/joaomdmoura/crewai), FastAPI, and Redis to demonstrate how autonomous agents can collaboratively analyze blood test reports. Multiple agents (Verifier, Doctor, Nutritionist, and Exercise Expert) work in sequence to extract key findings, provide diet/fitness suggestions, and respond based on user queries.


![image](image.jpg)
## 🛠️ Setup Instructions
Follow these steps to run the Blood Test Analyzer — works locally via FastAPI and Redis Queue.

### ✅ 1. Clone the Repository

```bash
https://github.com/S-panda1/Blood-test-analysis-system-Subhankar-Panda.git
cd Blood-test-analysis-system-Subhankar-Panda
```

### ✅ 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# For Windows:
venv\Scripts\activate

# For MacOS/Linux:
source venv/bin/activate
```
### 3. Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt

```
### 4. Set Up .env File

```bash
GEMINI_API_KEY="YOUR_API_KEY_HERE"
REDIS_URL="YOUR_REDIS_URL_HERE"
```
[Gemini API Docs](https://ai.google.dev/)
[Redis](https://redis.io/)
###  5. Start Redis Queue Worker

```bash
python worker.py

```
### ✅ 6. Run the Server (FastAPI + Uvicorn)

```bash
uvicorn main:app --reload

http://127.0.0.1:8000 # The server will start here

```

## 🐞 Bugs Found and Improvements made (Database integration + Queue Worker Model)

---

### 🔧 Bugs Fixed & Features Added

#### 🗂 `tools.py`

- ✅ **Properly implemented CrewAI tools**
  - Refactored custom tools (`BloodTestReportTool`, `NutritionTool`, `ExerciseTool`) to subclass `BaseTool` with `_run()` method.
- ✅ **Fixed PDF parsing**
  - Imported missing `PyPDFLoader` from `langchain_community.document_loaders`.
- ✅ **Dynamic input**
  - Tools now accept dynamic `file_path` instead of using hardcoded values.
- ✅ **Implemented LLM logic**
  - Implemented the logic for Nutrition and exercise tools to generate intelligent plans using `LLM(model="gemini/gemini-2.0-flash")`.

#### 👨‍⚕️ `agents.py`

- ✅ **Replaced placeholder agents**
  - Created realistic agents: `doctor`, `nutritionist`, `verifier`, and `exercise_specialist`, with better prompt engineering, rather than the existing harmful and misleading prompts.
- ✅ **Correct tool usage**
  - Tools are now passed as instantiated objects, not broken method calls.
- ✅ **LLM configuration**
  - All agents use `crewai.LLM()` for consistent behavior and better reasoning.

#### 🚀 `main.py`

- ✅ **Runs a full 4-agent Crew**
  - Crew includes: `verifier`, `doctor`, `nutritionist`, and `exercise_specialist`.
- ✅ **Safe task execution**
  - Introduced `safe_output()` to prevent failures from crashing the response pipeline.
- ✅ **File validation**
  - Checks for empty uploads and missing query inputs.
- ✅ **Integrated SQLite**
  - Stores all results using SQLAlchemy ORM.
- ✅ **Static file serving**
  - Mounted `/static` for frontend integration.

#### 📊 `tasks.py`

- ✅ **Background job support**
  - Integrated Redis + RQ for async processing.
- ✅ **Persistent storage**
  - All results are saved in the database.
  
### Extra Files Added
These additional files extend the system for modularity, background processing, and data persistence:

#### `tasks.py`
Defines all CrewAI `Task` objects like report verification, medical analysis, nutrition, and exercise planning. Tasks use agent context and tools to operate sequentially.

#### `db.py`
Initializes a local SQLite DB with `SQLAlchemy`. Stores uploaded file metadata, query, and generated results for history tracking.

#### `redis_connect.py`
Establishes a shared Redis connection using `REDIS_URL` from `.env`. Used across background task modules to ensure clean connectivity.

#### `worker.py`
Starts an RQ (Redis Queue) worker to process queued tasks. Run it in a separate terminal to enable asynchronous execution.

## API Documentation

This project exposes a REST API using **FastAPI** to analyze blood test reports using multi-agent AI with CrewAI.

### 🔗 Base URL
```bash
http://localhost:8000

```
### 📍 POST /analyze
#### Description:
Upload a blood test PDF report and provide a query. The system will analyze the report and return structured insights.

#### Request:
Content-Type: multipart/form-data

#### Fields:

- file: Blood test report in PDF format (Required)

- query: A string describing what you want (Optional, defaults to "Summarise my Blood Test Report")
  
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@blood_test_report.pdf" \
  -F "query=Summarize key findings and suggest a diet plan"
```
#### Results: 
```bash
{
  "status": "success",
  "query": "Summarize key findings and suggest a diet plan",
  "analysis": {
    "verifier": "The document is a blood test report.",
    "doctor": "... summarized findings ...",
    "nutrition": "... diet recommendations ...",
    "exercise": "... fitness recommendations ..."
  },
  "file_processed": "blood_test_report.pdf"
}
```

#### You can also test this endpoint interactively via:
```bash
http://localhost:8000/docs#/
```

### 📍 GET /history
#### Description:
Returns a list of all previous analyses stored in the database.

```bash
[
  {
    "id": 1,
    "file_name": "blood_test_report.pdf",
    "query": "Summarize my Blood Test Report",
    "created_at": "2025-06-29T15:21:30.174Z",
    "result": "{...}"
  },
  ...
]

```
### Using the HTML file
#### Location:
Open this file in your browser:
```bash
Open the HTML demo:
http://localhost:8000/static/index.html
```

#### Features:
- Upload your blood test PDF

- Type a custom query like:

 ```bash

"Summarise my blood report"

"Focus only on thyroid"

"Skip everything" (To return nothing)

```
#### Output:
You’ll see:
- A structured summary
- Nutrition & fitness suggestions (if query permits)
- JSON output displayed on screen


---
