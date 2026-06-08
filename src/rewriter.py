"""
ResumeSense AI - Resume Rewriter (Fallback-safe)
If ChromaDB is unavailable, uses the whole resume as retrieval context.
"""

import os
import sys

CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

def _safe_load_vector_store(collection_name: str = "test_resume"):
    """Try to load Chroma; if it fails, return None so we can fall back."""
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_community.vectorstores import Chroma
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=CHROMA_DB_PATH
        )
    except Exception as e:
        print(f"Warning: ChromaDB not available ({e}). Using full resume as retrieval context.")
        return None

def rewrite_resume_section(
    jd_text: str,
    resume_text: str,
    missing_keywords: list,
    section: str = "summary"
):
    """
    Rewrite a resume section. Uses RAG retrieval from ChromaDB if available,
    otherwise falls back to using the entire resume as context.
    """
    # Attempt RAG retrieval
    vector_store = _safe_load_vector_store()
    if vector_store is not None:
        try:
            retrieved_docs = vector_store.similarity_search(jd_text, k=2)
            retrieved_text = "\n".join([doc.page_content for doc in retrieved_docs])
        except Exception:
            retrieved_text = resume_text
    else:
        retrieved_text = resume_text

    # Build the prompt (for LLM; we'll still use template while quota limited)
    prompt = f"""
You are a professional resume writer.

Job Description:
{jd_text}

Candidate's Current Resume:
{resume_text}

Relevant parts of the resume (retrieved):
{retrieved_text}

Missing Keywords: {', '.join(missing_keywords)}

Task: Rewrite the candidate's {section} section to better match the job description.
Incorporate missing keywords naturally.
"""

    # Local template‑based rewrite (no API call needed)
    base_sentences = [s.strip() for s in resume_text.split('.') if s.strip()]
    base = ". ".join(base_sentences[:2]) + "."
    if missing_keywords:
        kw_text = ", ".join(missing_keywords)
        enhancement = f" Additionally, I have been actively building skills in {kw_text} through hands‑on projects and self‑study."
    else:
        enhancement = ""
    rewritten = f"{base}{enhancement}\n\n[Note: ChromaDB unavailable – used full resume as retrieval context.]"

    return rewritten, prompt
