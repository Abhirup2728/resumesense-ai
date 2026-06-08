"""
ResumeSense AI - Main Streamlit Application
"""

import streamlit as st
import tempfile
import os
import sys

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from src.extractor import extract_text_from_pdf
from src.keyword_analyzer import find_missing_keywords
from src.matcher import compute_match_score
from src.rewriter import rewrite_resume_section

st.set_page_config(page_title="ResumeSense AI", layout="wide")
st.title("📄 ResumeSense AI")
st.markdown("Upload your resume & paste a job description to get a match score, missing keywords, and a rewritten resume section.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

with col2:
    st.subheader("2. Job Description")
    jd_text = st.text_area("Paste the job description here", height=250)

if st.button("Analyze Resume"):
    if uploaded_file is None or not jd_text.strip():
        st.error("Please upload a resume and paste a job description.")
    else:
        with st.spinner("Analyzing..."):
            # Save uploaded PDF to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Extract text
            resume_text = extract_text_from_pdf(tmp_path)
            os.unlink(tmp_path)  # clean up temp file

            # 1. Keyword Gap Analysis
            gap_result = find_missing_keywords(jd_text, resume_text)
            missing_keywords = gap_result["missing_keywords"]
            found_keywords = gap_result["found_keywords"]
            keyword_match = gap_result["match_percentage"]

            # 2. Semantic Match Score
            semantic_score = compute_match_score(jd_text, resume_text)

            # 3. Rewrite summary
            rewritten, _ = rewrite_resume_section(
                jd_text=jd_text,
                resume_text=resume_text,
                missing_keywords=missing_keywords,
                section="summary"
            )

            # Display results
            st.success("Analysis complete!")
            st.metric("Semantic Match Score", f"{semantic_score}%")
            st.metric("Keyword Match", f"{keyword_match}%")

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("✅ Found Keywords")
                if found_keywords:
                    st.write(", ".join(found_keywords))
                else:
                    st.write("None")
            with col_b:
                st.subheader("❌ Missing Keywords")
                if missing_keywords:
                    st.write(", ".join(missing_keywords))
                else:
                    st.write("None")

            st.subheader("✏️ Rewritten Summary")
            st.write(rewritten)
