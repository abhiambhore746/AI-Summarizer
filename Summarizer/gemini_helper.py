import time
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found. Please add it to your .env file.")

genai.configure(api_key=api_key)

def generate_gemini_response(prompt):
    models_to_try = ["gemini-2.5-pro", "gemini-1.5-flash"]

    for model_name in models_to_try:
        try:
            print(f"🧠 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            print(f"✅ Success with {model_name}")
            return response.text

        except Exception as e:
            error_str = str(e)
            print(f"⚠️ Error with {model_name}: {error_str}")
            if "429" in error_str or "quota" in error_str.lower():
                print("⏳ Quota exceeded. Trying next model...")
                time.sleep(2)
                continue
            else:
                raise e

    return "❌ All Gemini models failed. Please check your API key or quota."
