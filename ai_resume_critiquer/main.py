import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="AI Resume Critiquer",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
# Improves the appearance of the app
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

h2 {
    font-size: 10px !important;
}
.stButton>button{
    background-color: black;
    color:white;
    font-size:18px;
    border-radius:20px;
    height:50px;
}
.stButton>button:hover{
    background-color:grey;
}
.block-container{
    padding-top:2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
# Displays information about the application
with st.sidebar:
    st.title("🤖 AI Resume Critiquer")
    st.markdown("---")

    st.write("### Features")
    st.write("✅ Resume Analysis")
    st.write("✅ ATS Score")
    st.write("✅ Resume Suggestions")
    st.write("✅ Grammar Feedback")
    st.write("✅ Download Report")

# ---------------- TITLE ----------------

st.title("🤖 AI Resume Critiquer")

st.write(
    "Upload your resume and receive detailed AI-powered feedback, ATS analysis, and improvement suggestions."
)

# ---------------- API KEY ----------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- TWO COLUMN LAYOUT ----------------
# Makes the UI cleaner

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "📄 Upload Resume",
        type=["pdf", "txt"]
    )

with col2:
    job_role = st.text_input(
        "💼 Target Job Role",
        placeholder="Example: Software Engineer"
    )

# ---------------- ANALYZE BUTTON ----------------

analyze = st.button(
    "Analyze Resume",
    use_container_width=True
)

# ---------------- PDF READER ----------------

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    text = ""

    for page in pdf_reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text

# ---------------- FILE READER ----------------

def extract_text_from_file(uploaded_file):

    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(
            io.BytesIO(uploaded_file.read())
        )

    return uploaded_file.read().decode("utf-8")

# ---------------- ANALYSIS ----------------

if analyze:

    if uploaded_file is None:
        st.warning("Please upload a resume first.")
        st.stop()

    try:

        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("Resume is empty.")
            st.stop()

        # ---------------- RESUME PREVIEW ----------------
        # Lets the user verify the uploaded resume

        with st.expander("📄 Resume Preview"):
            st.text(file_content[:2500])

        # ---------------- RESUME STATISTICS ----------------
        # Displays quick statistics

        st.metric(
            "Target Role",
            job_role if job_role else "General"
        )

        # ---------------- BETTER PROMPT ----------------
        # Produces a structured response

        prompt = f"""
You are an expert ATS Resume Reviewer.

Analyze this resume carefully.

Return your response exactly in the following format.

**Overall Resume Score (/100)

**ATS Compatibility Score (/100)

**Strengths**

**Weaknesses**

**Missing Skills**

**Grammar and Formatting Issues**

**Suggested Improvements**

**Final Verdict**

Target Job Role:
{job_role if job_role else "General"}

Resume:

{file_content}
"""

        client = Groq(api_key=GROQ_API_KEY)

        # ---------------- LOADING SPINNER ----------------
        # Shows while AI is generating the response

        with st.spinner("🤖 AI is analyzing your resume..."):

            response = client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[
                    {
                        "role": "system",
                        "content":
                        "You are an expert ATS Resume Reviewer."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0,

                max_tokens=1200
            )


        analysis = response.choices[0].message.content
        with st.container(border=True):
            st.markdown(analysis)

        # ---------------- ANALYSIS ----------------

        st.markdown("## 📊 Analysis Results")

        st.markdown(analysis)

        # ---------------- DOWNLOAD BUTTON ----------------
        # Allows downloading the report

        st.download_button(

            label="📥 Download Report",

            data=analysis,

            file_name="resume_analysis.txt",

            mime="text/plain"

        )

    except Exception as e:

        st.error(f"❌ {e}")