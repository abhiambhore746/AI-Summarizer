# analyzer.py
from textstat import textstat
import google.generativeai as genai
from pydantic import BaseModel, Field
import json

# Assuming ask_gemini is imported from chatbot.py or defined here.
# For simplicity and to use the structured schema, we define the model call here.

# --- Pydantic Schema Definition ---
class LegalAnalysis(BaseModel):
    """Schema for legal document entity and risk analysis."""
    entity_count_total: int = Field(description="Total number of unique legal entities (names, dates, clauses) found in the document.")
    entity_count_retained: int = Field(description="Number of those entities that are present in the summary.")
    risk_rating: str = Field(description="Overall risk level of the document/summary (Low, Medium, or High).")

def analyze_summary_metrics(original_text, summary):
    """
    Analyzes the summary against the original text using textstat and Gemini's structured output.
    """
    
    # 1. Calculate Simple Metrics
    original_words = len(original_text.split())
    summary_words = len(summary.split())
    density = (summary_words / original_words) * 100 if original_words > 0 else 0

    try:
        readability = textstat.flesch_kincaid_grade(summary)
    except Exception:
        readability = 15.0 # High grade if textstat fails

    # 2. Prepare LLM Structured Analysis
    llm_prompt = (
        "You are an expert legal paralegal. Compare the following ORIGINAL DOCUMENT "
        "and its SUMMARY. Your task is to count key entities (names, dates, amounts, "
        "and contract clauses like 'Term' or 'Indemnification') in the ORIGINAL document, "
        "count how many of those entities were successfully retained in the SUMMARY, "
        "and provide a single Risk Rating. Return ONLY the JSON object that matches the requested schema."
        f"\n\n--- ORIGINAL DOCUMENT ---\n{original_text[:4000]}"
        f"\n\n--- SUMMARY ---\n{summary[:2000]}"
    )
    
    llm_results = {}
    try:
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        
        # FIX: Enforce Pydantic schema for guaranteed numeric output
        response = model.generate_content(
            contents=llm_prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=LegalAnalysis, 
            )
        )
        
        # The response text is guaranteed to be valid JSON matching the schema
        llm_results = json.loads(response.text)
        
    except Exception as e:
        # Fallback to safe numeric defaults if the LLM call fails
        print(f"LLM Structured Analysis Error (Analyzer): {e}")
        llm_results = {
            "entity_count_total": 1, # Set to 1 to prevent division by zero, though 
            "entity_count_retained": 0,
            "risk_rating": "Error/N/A"
        }

    # 3. Return Combined Data
    return {
        "word_count_original": original_words,
        "word_count_summary": summary_words,
        "information_density": round(density, 2),
        "readability_grade": readability,
        "retention_data": llm_results
    }