import streamlit as st
import pdfplumber
import docx2txt
import re

# Try to import textstat safely
try:
    from textstat import flesch_reading_ease
except ImportError:
    def flesch_reading_ease(text):
        sentences = len(re.findall(r'[.!?]', text)) or 1
        words = len(re.findall(r'\w+', text)) or 1
        syllables = sum(len(re.findall(r'[aeiouyAEIOUY]', w)) for w in text.split()) or 1
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return round(score, 1)


# ---------------- Helper functions ----------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(uploaded_file):
    return docx2txt.process(uploaded_file)

def extract_text(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith('.docx'):
        return extract_text_from_docx(uploaded_file)
    else:
        return ""

def analyze_resume(text):
    suggestions = []
    lower_text = text.lower()

    required_sections = ['education', 'experience', 'projects', 'skills']
    for section in required_sections:
        if section not in lower_text:
            suggestions.append(f"⚠️ Missing section: **{section.capitalize()}**")

    word_count = len(re.findall(r'\w+', text))
    if word_count < 300:
        suggestions.append("⚠️ Resume is too short. Aim for at least **300 words**.")
    elif word_count > 900:
        suggestions.append("⚠️ Resume might be too long. Keep it concise (1–2 pages).")

    action_verbs = ['developed', 'led', 'created', 'designed', 'managed', 'implemented', 'analyzed', 'organized']
    if not any(v in lower_text for v in action_verbs):
        suggestions.append("💡 Add **action verbs** like *developed*, *implemented*, or *designed* to describe achievements.")

    tech_keywords = ['python', 'java', 'sql', 'flask', 'spring', 'react', 'docker', 'aws', 'html', 'css', 'javascript']
    if not any(k in lower_text for k in tech_keywords):
        suggestions.append("💡 Consider mentioning **technical skills** (e.g., Python, SQL, React).")

    if not re.search(r'\S+@\S+\.\S+', text):
        suggestions.append("⚠️ Email not found. Add your contact email.")
    if not re.search(r'\+?\d[\d\s-]{8,}\d', text):
        suggestions.append("⚠️ Contact number not found. Include your phone number.")

    readability_score = flesch_reading_ease(text)
    if readability_score < 50:
        suggestions.append("💡 The language seems complex. Use simpler, more readable wording.")

    total_checks = 7
    passed = total_checks - len(suggestions)
    score = max(0, int((passed / total_checks) * 100))
    return suggestions, word_count, readability_score, score


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="✨ AI Resume Analyzer", layout="centered")

# ---------------- CSS Styling ----------------
st.markdown("""
<style>
/* Gradient background */
body {
    background: linear-gradient(120deg, #f0f4ff, #e4f5f9);
}

/* Title header */
header, .css-18ni7ap {
    background: linear-gradient(90deg, #1e3a8a, #2563eb);
    color: white !important;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 1.8rem;
    font-weight: bold;
    letter-spacing: 1px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

/* Main card container */
.main {
    background: rgba(255, 255, 255, 0.85);
    padding: 2rem 3rem;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(10px);
}

/* Buttons */
.stButton>button {
    background-color: #2563EB;
    color: white;
    font-weight: 600;
    border-radius: 10px;
    transition: 0.3s ease;
}
.stButton>button:hover {
    background-color: #1D4ED8;
    transform: scale(1.03);
}

/* Expander styling */
.streamlit-expanderHeader {
    font-weight: 600;
    color: #1e3a8a;
}

/* Suggestions box */
.suggestion-box {
    background: #fef3c7;
    border-left: 6px solid #f59e0b;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
}

/* Success box */
.success-box {
    background: #dcfce7;
    border-left: 6px solid #22c55e;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
}

/* Animated progress bar */
.progress-bar div[role="progressbar"] {
    background: linear-gradient(90deg, #22c55e, #3b82f6);
    animation: slide 2s infinite alternate;
}
@keyframes slide {
    from { opacity: 0.6; }
    to { opacity: 1; }
}

/* Metrics styling */
[data-testid="stMetricValue"] {
    color: #1E3A8A;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown('<header>📄 AI Resume Analyzer</header>', unsafe_allow_html=True)
st.write("Upload your resume and get **intelligent feedback** on structure, readability, and keywords.")

# ---------------- Upload ----------------
uploaded_file = st.file_uploader("📎 Choose your resume (.pdf or .docx)", type=["pdf", "docx"])

if uploaded_file:
    with st.spinner("🧠 Analyzing your resume..."):
        resume_text = extract_text(uploaded_file)

        if not resume_text.strip():
            st.error("❌ Could not extract text. Try another file.")
        else:
            suggestions, word_count, readability, score = analyze_resume(resume_text)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("📊 Resume Overview")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📝 Word Count", word_count)
            with col2:
                st.metric("📖 Readability", f"{readability}")
            with col3:
                st.metric("⭐ Resume Score", f"{score}%")

            st.progress(score / 100)

            st.markdown("<hr>", unsafe_allow_html=True)

            with st.expander("📜 View Extracted Text"):
                st.write(resume_text)

            st.subheader("💡 Suggestions for Improvement")
            if suggestions:
                for s in suggestions:
                    st.markdown(f"<div class='suggestion-box'>{s}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='success-box'>🎉 Excellent! Your resume looks professional and well-structured!</div>", unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.info("🧭 Tip: Tailor your resume for each job by adding keywords from the job description for better ATS results.")
