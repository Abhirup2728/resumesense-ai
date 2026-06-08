import streamlit as st
import tempfile
import os
import sys
import plotly.graph_objects as go

# -----------------------------------------------
# Page Configuration
# -----------------------------------------------
st.set_page_config(
    page_title="ResumeSense AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------
# Premium Dark Theme CSS
# -----------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600;700&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .main {
        background-color: #0B0F19;
        padding-top: 1rem;
    }

    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 0.95) 0%, rgba(11, 15, 25, 1) 100%);
    }

    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #F3F4F6;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #9CA3AF;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    .card-container {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
    }

    .stTextArea textarea {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #F3F4F6 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        padding: 16px !important;
    }

    .stFileUploader div {
        width: 100%;
    }
    .stFileUploader section {
        border: 2px dashed #374151 !important;
        border-radius: 16px !important;
        background-color: rgba(30, 41, 59, 0.3) !important;
        padding: 30px 20px !important;
        transition: border 0.2s ease, background-color 0.2s ease;
    }
    .stFileUploader section:hover {
        border-color: #10B981 !important;
        background-color: rgba(16, 185, 129, 0.05) !important;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #10B981 0%, #1E293B 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 14px 0;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #10B981 0%, #111827 100%);
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
        border-color: #10B981;
        transform: scale(1.02);
    }

    .glow-text {
        font-family: 'Inter', sans-serif;
        color: #10B981;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        font-weight: 500;
        letter-spacing: 1px;
        text-align: center;
        margin: 1rem 0;
    }

    .keyword-pill {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid #374151;
        border-radius: 50px;
        color: #D1D5DB;
        padding: 6px 16px;
        margin: 4px;
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .keyword-pill:hover {
        background: rgba(16, 185, 129, 0.15);
        border-color: #10B981;
        color: #10B981;
    }
    .missing-pill {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #FCA5A5;
    }
    .missing-pill:hover {
        background: rgba(239, 68, 68, 0.2);
        border-color: #EF4444;
    }

    .footer {
        text-align: center;
        color: #4B5563;
        padding: 2rem 0;
        font-family: 'Inter', sans-serif;
    }
    .footer span {
        margin: 0 10px;
        opacity: 0.6;
    }

    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0B0F19;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Backend Imports
# -----------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))
from src.extractor import extract_text_from_pdf
from src.keyword_analyzer import find_missing_keywords
from src.matcher import compute_match_score
from src.rewriter import rewrite_resume_section

# -----------------------------------------------
# Session State
# -----------------------------------------------
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None

# -----------------------------------------------
# Header
# -----------------------------------------------
st.markdown('<div class="main-title">🧠 ResumeSense AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload your resume & paste a job description to unlock match insights, keyword gaps, and a tailored resume rewrite.</div>', unsafe_allow_html=True)

# -----------------------------------------------
# Input Section
# -----------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="margin-bottom: 8px;">
        <span style="font-family: 'Inter', sans-serif; color: #F3F4F6; font-weight: 500; font-size: 0.9rem;">
            📄 1. Upload Resume (PDF)
        </span>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed", key="file_uploader")
    if uploaded_file is not None:
        file_size_kb = round(len(uploaded_file.getvalue()) / 1024, 1)
        st.markdown(f"""
        <div style="margin-top: 10px; padding: 10px 15px; background: rgba(16, 185, 129, 0.1); 
                    border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; display: flex; align-items: center;">
            <span style="font-size: 1.2rem; margin-right: 10px;">📋</span>
            <div>
                <div style="color: #F3F4F6; font-weight: 500; font-size: 0.9rem;">{uploaded_file.name[:25]}...</div>
                <div style="color: #9CA3AF; font-size: 0.75rem;">{file_size_kb} KB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="margin-bottom: 8px;">
        <span style="font-family: 'Inter', sans-serif; color: #F3F4F6; font-weight: 500; font-size: 0.9rem;">
            💼 2. Job Description
        </span>
    </div>
    """, unsafe_allow_html=True)
    jd_text = st.text_area("", height=250, placeholder="Paste the full job description here...", label_visibility="collapsed")

# -----------------------------------------------
# Analyze Button
# -----------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Analyze Resume"):
    if uploaded_file is None or not jd_text.strip():
        st.error("Please upload a resume and paste a job description.")
    else:
        with st.spinner(""):
            st.markdown('<div class="glow-text" style="font-size: 1.2rem;">✨ Analyzing your profile against the job...</div>', unsafe_allow_html=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            resume_text = extract_text_from_pdf(tmp_path)
            os.unlink(tmp_path)

            gap_result = find_missing_keywords(jd_text, resume_text)
            missing_keywords = gap_result["missing_keywords"]
            found_keywords = gap_result["found_keywords"]
            keyword_match = gap_result["match_percentage"]

            semantic_score = compute_match_score(jd_text, resume_text)

            rewritten, _ = rewrite_resume_section(
                jd_text=jd_text,
                resume_text=resume_text,
                missing_keywords=missing_keywords,
                section="summary"
            )

            st.session_state.analysis_complete = True
            st.session_state.results = {
                "semantic_score": semantic_score,
                "keyword_match": keyword_match,
                "found_keywords": found_keywords,
                "missing_keywords": missing_keywords,
                "rewritten": rewritten
            }
            st.rerun()

# -----------------------------------------------
# Results Dashboard
# -----------------------------------------------
if st.session_state.analysis_complete and st.session_state.results is not None:
    res = st.session_state.results
    st.markdown('<div class="glow-text">✓ Analysis Complete</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    g1, g2 = st.columns(2)

    with g1:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=res["semantic_score"],
            number={'suffix': "%", 'font': {'size': 32, 'color': '#F3F4F6', 'family': 'Inter'}},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Semantic Match Score", 'font': {'size': 16, 'color': '#9CA3AF', 'family': 'Inter'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#9CA3AF", 'visible': False},
                'bar': {'color': "#10B981", 'thickness': 0.15},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': '#1E293B'},
                    {'range': [40, 70], 'color': '#334155'},
                    {'range': [70, 100], 'color': '#1E293B'}
                ],
            }
        ))
        fig1.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=250,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=res["keyword_match"],
            number={'suffix': "%", 'font': {'size': 32, 'color': '#F3F4F6', 'family': 'Inter'}},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Keyword Match", 'font': {'size': 16, 'color': '#9CA3AF', 'family': 'Inter'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#9CA3AF", 'visible': False},
                'bar': {'color': "#F59E0B", 'thickness': 0.15},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': '#1E293B'},
                    {'range': [40, 70], 'color': '#334155'},
                    {'range': [70, 100], 'color': '#1E293B'}
                ],
            }
        ))
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=250,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_found, col_missing = st.columns(2)

    with col_found:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #F3F4F6; font-family: Inter; margin-bottom: 12px;">✅ Found Keywords</h3>', unsafe_allow_html=True)
        if res["found_keywords"]:
            pills_html = ""
            for kw in res["found_keywords"]:
                pills_html += f'<span class="keyword-pill">{kw}</span>'
            st.markdown(pills_html, unsafe_allow_html=True)
        else:
            st.markdown('<span style="color: #9CA3AF;">None</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_missing:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #F3F4F6; font-family: Inter; margin-bottom: 12px;">❌ Missing Keywords</h3>', unsafe_allow_html=True)
        if res["missing_keywords"]:
            pills_html = ""
            for kw in res["missing_keywords"]:
                pills_html += f'<span class="keyword-pill missing-pill">{kw}</span>'
            st.markdown(pills_html, unsafe_allow_html=True)
        else:
            st.markdown('<span style="color: #9CA3AF;">None</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h3 style="color: #F3F4F6; font-family: Inter; margin: 0;">✏️ Rewritten Summary</h3>
        <span style="color: #9CA3AF; font-size: 1.2rem; cursor: pointer;" title="Copy to clipboard">📋</span>
    </div>
    """, unsafe_allow_html=True)
    st.code(res["rewritten"], language=None, line_numbers=False)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------
# Footer
# -----------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <span>🦜 LangChain</span>
    <span>🟡 ChromaDB</span>
    <span>✨ Google Gemini</span>
    <span>👑 Streamlit</span>
    <span>⚙️ FAISS</span>
</div>
""", unsafe_allow_html=True)
