# ResumeSense AI

**RAG-powered resume intelligence platform**  
Upload a resume (PDF) + job description → get match score, missing keywords, and a rewritten resume section.

## 🚀 Live Demo
[ResumeSense AI on Streamlit Cloud](https://resumesense-ai.streamlit.app) *(once deployed)*

## 🧠 Features
- **Semantic Match Score**: Cosine similarity between resume & JD using Gemini embeddings
- **Keyword Gap Analysis**: Curated tech skills list matched against JD vs resume
- **Resume Rewriter**: RAG retrieval (ChromaDB) + LLM/template to generate a tailored summary
- **PDF Text Extraction**: pdfplumber‑based extraction

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **NLP & Embeddings**: Google Gemini Embedding 001, spaCy
- **Vector Store**: ChromaDB
- **LLM**: Google Gemini Flash (planned; currently template‑based)
- **Languages & Tools**: Python, LangChain, scikit‑learn

## 🏗️ How to Run Locally
1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/resumesense-ai.git
   cd resumesense-ai
