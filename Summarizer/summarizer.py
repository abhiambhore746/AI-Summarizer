import google.generativeai as genai
from transformers import pipeline
import torch
import re
import math 

# Configure Gemini
genai.configure(api_key="AIzaSyAMW7G9HpP_OPV5_3TM8BkOeYL322QsuqU") 


def summarize_text(model_name, text):
    """
    Summarize text using Gemini API or local Hugging Face models (BART / T5).
    Optimized for CONCISE summaries and eliminates max_length warnings.
    """

    # --- GEMINI SUMMARIZATION ---
    if "gemini" in model_name.lower():
        try:
            model = genai.GenerativeModel("models/gemini-2.5-pro")
            
            # Use in-prompt system instruction for compatibility
            system_instruction_prompt = (
                "You are an expert legal assistant. Provide a concise, bulleted summary of the following legal text."
                "Do not include any introductory phrases like 'Based on the provided text' or 'The document states'."
                "\n\nLegal Document:\n\n"
            )

            full_prompt = system_instruction_prompt + text
            
            response = model.generate_content(
                contents=full_prompt
            )
            
            summary = response.text.strip()
            return summary
        except Exception as e:
            # Check for common API errors or network issues
            return f"Gemini error: {str(e)}"

    # --- LOCAL SUMMARIZATION (BART / T5) ---
    try:
        # 1. Determine Model ID
        if model_name.lower() == "bart":
            model_id = "facebook/bart-large-cnn"
        elif model_name.lower() == "t5":
            model_id = "t5-small"
        else:
            return "Local summarization error: Unsupported model name"

        # Initialize pipeline 
        summarizer = pipeline(
            "summarization",
            model=model_id,
            device=0 if torch.cuda.is_available() else -1
        )

        # 2. Clean and limit text
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 4000:
            text = text[:4000] 

        # 3. Split into smaller logical chunks
        sentences = re.split(r"(?<=[.!?]) +", text)
        chunks, current_chunk = [], ""
        max_chunk_size = 500

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        # 4. Cap chunk count
        chunks = chunks[:5] 

        summarized_chunks = []
        for chunk in chunks:
            
            # --- Dynamic Length Calculation per Chunk (Final Refinement) ---
            chunk_words = len(chunk.split())
            
            # FIX: Set max_new_tokens to a smaller percentage (20%) of the input 
            # with a lower max cap (40) to satisfy the Hugging Face warning logic.
            dynamic_max_tokens = max(15, min(40, int(chunk_words * 0.20))) 
            # -----------------------------------------------------------------
            
            summary = summarizer(
                chunk,
                max_new_tokens=dynamic_max_tokens,  # Use max_new_tokens
                min_length=10,                      # Lowered min_length slightly
                do_sample=False,
                early_stopping=True
            )
            summarized_chunks.append(summary[0]["summary_text"].strip())

        final_summary = " ".join(summarized_chunks)
        # Return the final stitched summary, capping at a reasonable length
        return final_summary[:1000] + "..." if len(final_summary) > 1000 else final_summary

    except Exception as e:
        # Fallback to Gemini if local model fails
        try:
            model = genai.GenerativeModel("models/gemini-2.5-pro")
            response = model.generate_content(f"Summarize briefly:\n\n{text}")
            return f"(Local Model Failed. Fallback to Gemini)\n{response.text.strip()}"
        except Exception as fallback_e:
            return f"Critical Failure: Local summarization error ({str(e)}) and Gemini fallback error ({str(fallback_e)})"