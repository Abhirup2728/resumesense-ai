"""
ResumeSense AI - Keyword Analyzer (Rule‑based with curated skills list)
Extracts skills from job descriptions by matching against a known list.
"""

import os
import re
from typing import List, Dict, Set

# Load the skills list once
def _load_skills() -> Set[str]:
    skills_file = os.path.join(os.path.dirname(__file__), "..", "assets", "tech_skills.txt")
    if not os.path.exists(skills_file):
        # Fallback if path resolution fails (e.g., running from wrong dir)
        skills_file = "assets/tech_skills.txt"
    skills = set()
    with open(skills_file, "r", encoding="utf-8") as f:
        for line in f:
            skill = line.strip().lower()
            if skill and not skill.startswith("#"):
                skills.add(skill)
    return skills

SKILLS_SET = _load_skills()

def tokenize(text: str) -> List[str]:
    """Return lowercase alphanumeric tokens."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.split()

def get_jd_keywords(jd_text: str, top_n: int = 15) -> List[str]:
    """
    Extract skills from the job description by matching against the curated list.
    Returns only skills that appear in the text (substring match).
    """
    jd_lower = jd_text.lower()
    found = []
    seen = set()
    # Sort by length (longest first) to prefer multi-word skills over substrings
    for skill in sorted(SKILLS_SET, key=len, reverse=True):
        if skill in jd_lower and skill not in seen:
            found.append(skill)
            seen.add(skill)
        if len(found) >= top_n:
            break
    return found

def find_missing_keywords(jd_text: str, resume_text: str) -> Dict:
    """
    Compare JD keywords against resume (substring + token match).
    Returns gap analysis.
    """
    jd_keywords = get_jd_keywords(jd_text)
    if not jd_keywords:
        return {
            "total_jd_keywords": 0,
            "matched_keywords": 0,
            "missing_keywords": [],
            "match_percentage": 0.0,
            "found_keywords": [],
            "all_jd_keywords": []
        }
    
    resume_lower = resume_text.lower()
    resume_tokens = set(tokenize(resume_text))
    
    found = []
    missing = []
    for kw in jd_keywords:
        kw_lower = kw.lower()
        if kw_lower in resume_lower:
            found.append(kw)
        elif len(kw_lower.split()) == 1 and kw_lower in resume_tokens:
            found.append(kw)
        else:
            missing.append(kw)
    
    match_perc = round((len(found) / len(jd_keywords)) * 100, 1)
    
    return {
        "total_jd_keywords": len(jd_keywords),
        "matched_keywords": len(found),
        "missing_keywords": missing,
        "match_percentage": match_perc,
        "found_keywords": found,
        "all_jd_keywords": jd_keywords
    }

if __name__ == "__main__":
    sample_jd = """
    We are looking for a Data Scientist with expertise in Python, machine learning, 
    deep learning, TensorFlow, and cloud platforms like AWS. Experience with NLP and 
    computer vision is a plus. The candidate should be proficient in SQL and data 
    visualization tools like Tableau or Power BI.
    """
    sample_resume = "I have experience in Python, SQL, and machine learning. I've used AWS for deployment."
    
    result = find_missing_keywords(sample_jd, sample_resume)
    print("JD Keywords:", result["all_jd_keywords"])
    print("Missing:", result["missing_keywords"])
    print("Match %:", result["match_percentage"])
