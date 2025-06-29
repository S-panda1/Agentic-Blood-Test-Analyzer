from crewai import Task
from agents import doctor, verifier, nutritionist, exercise_specialist

from tools import BloodTestReportTool, NutritionTool, ExerciseTool

# Step 1: Verifier always runs
verification = Task(
    description="""
    You are a medical document verifier.

    Your job is to inspect the document at {file_path} and determine whether it appears to be a blood test report.

     If yes, return this **exact message**: "The document is a blood test report."
     If not, return: "The document is NOT a blood test report. Stopping."

    Do NOT return the file contents or raw text. Only return one of the two verdicts above.
    """,
    expected_output="A single sentence confirming or rejecting the document type.",
    agent=verifier,
    tools=[BloodTestReportTool()],
    async_execution=False,
)


# Step 2: Doctor responds to user query — with default analysis as fallback
help_patients = Task(
    description="""
    You are a medical expert analyzing the report at {file_path}.

    Based on the user's request: "{query}", respond as follows:
    - If the "{query}" is empty or vague (e.g., "summarize"), perform a full medical analysis ONLY NO NUTRITION OR EXCERCISE PLAN NEEDED.
    - If the "{query}" is specific (e.g., "focus only on thyroid"), do only that.
    - If the "{query}" says "skip" or "do nothing", respond with: "Acknowledged. No analysis performed."

    Carefully analyze the provided blood report from the file path {file_path} using your tools.

  Summarize ONLY the key abnormal findings (e.g., high ALP, low T4, etc.).
  DO NOT return the full raw content of the report.
  DO NOT echo back any line-by-line text.

Return your answer as:
- A markdown summary of 2–3 key abnormalities and also some other minor concerning issues
- Final summary: short advice or suggestion

    Keep your tone professional and explain abnormal values in simple terms.
    """,
    expected_output="""
Your answer MUST be a clean summary of medical findings from the report.

Include:
1. **Abnormal markers only**, explained in clear terms.
2. Mention **any borderline or mildly concerning values**.
3. End with a **short final summary or next-step advice.**

Format:
- Use short bullet points or short paragraphs.
- Do NOT include full PDF text.
- Do NOT repeat raw lines from the report.

Let your format adapt to the context of the query (e.g., short if specific, longer if summarizing full report).
""",
    agent=doctor,
    context=[verification],
    tools=[BloodTestReportTool()],
    async_execution=False,
)

# Step 3: Nutritionist reacts only if nutrition is requested or default applies
nutrition_analysis = Task(
    description="""
    Based on the user query: "{query}", and the findings from the doctor:

    - If the USER "{query}" SPECIFICALLY mentions food, diet, or nutrition, generate a customized plan according to the user's food choices.
    - If the USER "{query}" is VAGUE AND DOESN'T ASK FOR "FOOD" OR "NUTRITION PLAN" AND ONLY ASKS FOR AN REPORT SUMMARY OR ANALYSIS(e.g., "summarize my health"), DO NOT PROVIDE full nutrition , JUST SAY "NO NUTRITION GUIDANCE REQUESTED".
    - If the USER "{query}" says "no nutrition advice", respond: "Nutrition guidance skipped as requested."
    - If the USER "{query}" HAS NOT ASKED ANYTHING ABOUT "NUTRITION", "DIET" OR "FOOD", then DO NOT GENERATE nutrition plan, even if blood test report suggest so, ONLY AND ONLY IF THE USER HAS ASKED FOR IT OTHERWISE NEVER, JUST SAY "NO NUTRITION GUIDANCE REQUESTED"

    Your advice must link directly to blood abnormalities and be clear and actionable.
    """,
    expected_output="A structured nutrition plan in Markdown OR a short opt-out message.",
    agent=nutritionist,
    context=[help_patients],
    tools=[NutritionTool()],
    async_execution=False,
)

# Step 4: Exercise planner mirrors same logic
exercise_planning = Task(
    description="""
    Based on the user query: "{query}" and the doctor's findings:

    - If the USER "{query}" SPECIFICALLY ASKS for "exercise", "fitness", or some related words PROVIDE a full, safe exercise plan.
    - If the USER "{query}" doesn't ask for "exercise", "fitness", or is vague, DO NOT provide a full, safe exercise plan, reply: "Exercise plan omitted as per request."
    - If the USER "{query}" says to exclude exercise, reply: "Exercise plan omitted as per request."
    - If the USER "{query}" HAS NOT ASKED ANYTHING ABOUT "EXCERCISE" OR "FITNESS" , then DO NOT GENERATE nutrition plan, even if blood test report suggest so, ONLY AND ONLY IF THE USER HAS ASKED FOR IT OTHERWISE NEVER, reply: "Exercise plan omitted as per request."

    Tailor your output to the user's blood test and offer clear, structured advice.
    """,
    expected_output="A detailed Markdown exercise plan or a brief skip confirmation.",
    agent=exercise_specialist,
    context=[help_patients],
    tools=[ExerciseTool()],
    async_execution=False,
)
