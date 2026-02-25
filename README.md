# AI-Powered Legal Document Summarizer & Interactive Explainer Chatbot

<p align="center">
  <b>Transforming Complex Legal Documents into Simple, Understandable Insights using AI</b>
</p>

---

## 📌 Overview

The AI-Powered Legal Document Summarizer is an intelligent LegalTech web application designed to simplify complex legal documents. Users can upload legal PDF files, receive concise AI-generated summaries, and interact with a chatbot for detailed explanations of legal terms and clauses.

This system leverages state-of-the-art transformer-based NLP models to enhance accessibility and understanding of legal content.

---

##  Problem Statement

Legal documents are often lengthy, complex, and difficult to interpret without professional assistance. This project aims to:

- Reduce legal complexity using AI summarization
- Improve accessibility for non-legal users
- Provide interactive clarification of legal terms
- Ensure secure handling of sensitive legal data

---

## Core Features

- 📄 Upload Legal Documents (PDF/DOCX)
- 🧠 AI-Based Summarization using Models
- 💬 Interactive Legal Q&A Chatbot using Gemini
- 🔐 AES-Based File Encryption using Fernet
- 📑 Text Extraction using PyMuPDF & python-docx
- 🌐 Responsive Web Interface using Flask

---

## System Architecture

1. User uploads document  
2. Text extraction module processes file  
3. Content encrypted securely  
4. BART model generates summary  
5. FLAN-T5 chatbot answers user queries  
6. Results displayed on web interface  

---

# Program structure

```
AI-Legal-Document-Summarizer/
│
├── backend/
│   ├── app.py
│   ├── analyzer.py
│   ├── chatbot.py
│   ├── summarizer.py
│   ├── extract_text.py
│   ├── highlight.py
│   └── gemini_helper.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── uploads/
│
├── requirements.txt
├── README.md
└── .gitignore
```

### To run the program
- python -m venv .venv
- .venv\Scripts\activate
- python app.py

### Backend
- Python
- Flask

### NLP Models
- BART (Summarization)
- FLAN-T5 (Question Answering)

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap / TailwindCSS

### Security
- cryptography (Fernet - AES Encryption)

### Document Processing
- PyMuPDF
- python-docx

---
