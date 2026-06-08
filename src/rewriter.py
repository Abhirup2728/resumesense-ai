"""
ResumeSense AI - Resume Rewriter (Local RAG + Template)
Retrieves relevant resume chunks from ChromaDB and produces a
template‑based rewrite that incorporates missing keywords.
"""

import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

def load_vector_store(collection_name: str = "test_resume"):
    """Load the existing ChromaDB collection."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

def rewrite_resume_section(
    jd_text: str,
    resume_text: str,
    missing_keywords: list,
    section: str = "summary"
) -> str:
    """
    Rewrite a resume section using RAG retrieval + template generation.
    
    - Retrieves relevant resume chunks from ChromaDB (RAG retrieval).
    - Builds a structured prompt.
    - Generates a rewritten section that incorporates missing keywords.
    """
    # RAG step: retrieve similar chunks from vector store
    vector_store = load_vector_store()
    retrieved_docs = vector_store.similarity_search(jd_text, k=2)
    retrieved_text = "\n".join([doc.page_content for doc in retrieved_docs])

    # Build a prompt (we can show this in the app as "what we'd send to LLM")
    prompt = f"""
You are a professional resume writer.

Job Description:
{jd_text}

Candidate's Current Resume:
{resume_text}

Relevant parts of the resume:
{retrieved_text}

Missing Keywords: {', '.join(missing_keywords)}

Task: Rewrite the candidate's {section} section to better match the job description.
Incorporate missing keywords naturally.
"""

    # Template‑based rewrite (local, no API)
    # Extract the first two sentences from the resume as base
    base_sentences = [s.strip() for s in resume_text.split('.') if s.strip()]
    base = ". ".join(base_sentences[:2]) + "."

    # Add a sentence that incorporates missing keywords
    if missing_keywords:
        kw_text = ", ".join(missing_keywords)
        enhancement = f" Additionally, I have been actively building skills in {kw_text} through hands‑on projects and self‑study."
    else:
        enhancement = ""

    rewritten = f"{base}{enhancement}\n\n[Prompt built but LLM call skipped due to quota. The above template demonstrates RAG retrieval + prompt creation.]"
    return rewritten, prompt

if __name__ == "__main__":
    sample_jd = """
    We are looking for a Data Scientist with expertise in Python, machine learning,
    deep learning, TensorFlow, and cloud platforms like AWS. Experience with NLP and
    computer vision is a plus. The candidate should be proficient in SQL and data
    visualization tools like Tableau or Power BI.
    """
    sample_resume = """
    John Doe is a Data Scientist with 5 years of experience.
    He has expertise in Python, machine learning, SQL, and AWS.
    He built customer churn prediction models and deployed them using Docker.
    """
    missing = ["deep learning", "tensorflow", "nlp", "computer vision", "tableau", "power bi"]
    
    print("Generating rewritten summary (local template)...")
    rewritten_text, prompt = rewrite_resume_section(
        jd_text=sample_jd,
        resume_text=sample_resume,
        missing_keywords=missing,
        section="summary"
    )
    print("\n--- Rewritten Summary ---")
    print(rewritten_text)
    print("\n--- Prompt (for LLM) ---")
    print(prompt)
