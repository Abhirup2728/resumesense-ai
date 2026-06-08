"""
ResumeSense AI - Semantic Matcher
Computes cosine similarity between JD and resume embeddings.
"""

import numpy as np
from src.embedder import get_embeddings_model

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Return cosine similarity between two vectors."""
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def compute_match_score(jd_text: str, resume_text: str) -> float:
    """
    Compute semantic match score between job description and resume.
    
    Args:
        jd_text: Job description text.
        resume_text: Resume text.
    
    Returns:
        Match score as a percentage (0-100).
    """
    embeddings = get_embeddings_model()
    
    # Embed both texts as single vectors
    jd_vector = np.array(embeddings.embed_query(jd_text))
    resume_vector = np.array(embeddings.embed_query(resume_text))
    
    sim = cosine_similarity(jd_vector, resume_vector)
    # Cosine similarity ranges from -1 to 1; in practice embeddings are non-negative
    # Clamp to 0-1 then convert to percentage
    sim = max(0.0, min(1.0, sim))
    score = round(sim * 100, 1)
    return score

if __name__ == "__main__":
    sample_jd = """
    We are looking for a Data Scientist with Python, machine learning, AWS, 
    and SQL experience. Knowledge of Docker is a plus.
    """
    sample_resume = """
    I have experience in Python, SQL, and machine learning. 
    I've used AWS and Docker for model deployment.
    """
    score = compute_match_score(sample_jd, sample_resume)
    print(f"Match score: {score}%")
