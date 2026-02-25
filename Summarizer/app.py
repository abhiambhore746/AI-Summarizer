from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

# -----------------------------
# Import helper modules
# -----------------------------
from extract_text import extract_text
from summarizer import summarize_text
from analyzer import analyze_summary_metrics
from highlight import highlight_terms
from gemini_helper import generate_gemini_response  # ✅ updated fallback handler

# -----------------------------
# Flask app setup
# -----------------------------
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Load environment variables
load_dotenv()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Memory to store user context
user_context = {
    "text": "",
    "summary": ""
}

# -----------------------------
# Serve Frontend (index.html)
# -----------------------------
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')


# -----------------------------
# File Upload & Text Extraction
# -----------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        extracted_text = extract_text(file_path)
        user_context["text"] = extracted_text  # ✅ store extracted text
        return jsonify({"text": extracted_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Text Highlighting
# -----------------------------
@app.route('/highlight', methods=['POST'])
def highlight_text_route():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        highlighted = highlight_terms(text)
        return jsonify({"highlighted_text": highlighted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Summarization & Analysis
# -----------------------------
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get("text")
    model_name = data.get("model", "bart")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        summary = summarize_text(model_name, text)
        user_context["summary"] = summary  # ✅ store summary for chatbot

        analysis_data = analyze_summary_metrics(text, summary)

        return jsonify({
            "model": model_name,
            "summary": summary,
            "metrics": analysis_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Multi-Model Comparison
# -----------------------------
@app.route('/compare_models_full', methods=['POST'])
def compare_models_full():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided for comparison"}), 400

    models_to_compare = ["bart", "t5", "gemini-2.5-pro"]
    comparison_results = []
    full_text = user_context["text"] if user_context["text"] else text

    for model_name in models_to_compare:
        try:
            summary = summarize_text(model_name, full_text)
            analysis_data = analyze_summary_metrics(full_text, summary)

            comparison_results.append({
                "model": model_name,
                "summary": summary,
                "metrics": analysis_data
            })
        except Exception as e:
            comparison_results.append({
                "model": model_name,
                "error": f"Model failed: {str(e)}"
            })

    return jsonify({"results": comparison_results})


# -----------------------------
# Chatbot (Gemini Fallback Integrated)
# -----------------------------
@app.route('/chat', methods=['POST'])
def chat_with_gemini():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # ✅ Combine uploaded text + summary as context
    context = (
        "Answer the user's question ONLY based on the following context.\n"
        "If the answer cannot be found, say 'The information is not available in the uploaded document.'\n\n"
        f"Extracted text (truncated):\n{user_context['text'][:4000]}\n\n"
        f"Summary:\n{user_context['summary'][:2000]}\n\n"
        f"User question: {prompt}"
    )

    try:
        # ✅ Use fallback handler (auto-switches between gemini-2.5-pro and gemini-1.5-flash)
        response = generate_gemini_response(context)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Run Flask App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
