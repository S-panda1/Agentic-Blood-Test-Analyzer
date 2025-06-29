## Importing libraries and files
import os
from dotenv import load_dotenv
from crewai_tools import BaseTool
# BUG FIX: Imported PDFLoader, which was missing.
from langchain_community.document_loaders import PyPDFLoader

from crewai import LLM
load_dotenv()

# BUG FIX: Hardcoded path removed from the tool method signature.
# It now properly gets the file path from the agent's context.
class BloodTestReportTool(BaseTool):
    name: str = "Blood Test Report Reader"
    description: str = "Reads all the text content from a specified PDF blood test report."

    def _run(self, file_path: str) -> str:
        """Tool to extract cleaned summary-friendly content from the PDF."""
        loader = PyPDFLoader(file_path=file_path)
        docs = loader.load()

        # Combine all page content
        full_text = "\n".join(page.page_content.strip() for page in docs)
        
        # Clean up repeated newlines
        clean_text = full_text.replace('\n\n', '\n').strip()

        # Return only first part to avoid overwhelming LLM
        preview_text = clean_text

        return (
            f"blood test report for context :\n\n"
            f"{preview_text}\n\n"
            
        )

# TODO TASK (Completed): Implemented the nutrition analysis logic.
class NutritionTool(BaseTool):
    name: str = "Nutrition Analyzer"
    description: str = "Analyzes blood report data to generate a personalized nutrition plan."

    def _run(self, blood_report_data: str) -> str:
        """Generates a nutrition plan based on the report."""
        llm = LLM(model="gemini/gemini-2.0-flash", temperature=0.3)
        
        prompt = f"""
        Based on the following blood report data, act as an expert clinical nutritionist and create a detailed, actionable, and personalized diet plan.
        Explain the reasons for your recommendations by linking them to specific values in the report (e.g., high cholesterol, low vitamin D).
        The plan should be easy to follow and focus on whole foods.

        Blood Report Data:
        {blood_report_data}

        Provide a response formatted in Markdown.
        """
        
        response = llm.invoke(prompt)
        return response.content

# TODO TASK (Completed): Implemented the exercise planning logic.
class ExerciseTool(BaseTool):
    name: str = "Exercise Planner"
    description: str = "Creates a personalized exercise plan based on blood report data."

    def _run(self, blood_report_data: str) -> str:
        """Generates an exercise plan based on the report."""
        llm = LLM(model="gemini/gemini-2.0-flash", temperature=0.3)
        
        prompt = f"""
        Based on the following blood report data, act as a certified exercise physiologist and create a safe, effective, and personalized exercise plan.
        Consider all health markers (e.g., cardiovascular health, glucose levels, bone density indicators) to tailor the recommendations.
        The plan should include a mix of cardiovascular, strength, and flexibility exercises and be suitable for the user's likely condition.
        Explain why each type of exercise is recommended based on the report.

        Blood Report Data:
        {blood_report_data}
        
        Provide a response formatted in Markdown.
        """
        response = llm.invoke(prompt)
        return response.content