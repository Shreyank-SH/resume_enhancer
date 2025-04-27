import streamlit as st
import tempfile
import os
import fitz  # PyMuPDF
from docx import Document
from groq import Groq
import re
import google.generativeai as genai

# Initialize Groq client
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com"
    )
except Exception as e:
    st.error(f"Error initializing Groq client: {str(e)}")
    client = None

# Initialize Gemini
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Error initializing Gemini: {str(e)}")

# Set theme to light
st.set_page_config(
    page_title="Resume Enhancer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Move header section higher */
    .main .block-container {
        padding-top: 1rem !important;
        width: 100% !important;
        max-width: none;
        padding: 1rem 2rem;
        margin: 0;
    }

    /* Make the app container responsive */
    .stApp {
        width: 100vw !important;
        min-height: 100vh !important;
        max-width: none;
        padding: 0 !important;
        margin: 0;
        background-color: #FFFFFF;
    }

    /* Header Styling with adjusted position */
    .main-header {
        text-align: center;
        margin-top: -0rem !important;
        margin-bottom: 1rem;
        padding-top: 0 !important;
        color: #1D3557;
    }

    .main-header h1 {
        color: #1D3557;
        font-size: 2.5rem;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Remove default Streamlit padding */
    .stApp > header {
        background-color: transparent;
    }

    /* Remove extra spacing from first widget */
    .stApp > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #1D3557;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #2A9D8F;
    }

    /* Status Colors */
    .stSuccess {
        background-color: #2A9D8F;
        color: white;
    }

    .stWarning {
        background-color: #F4A261;
        color: white;
    }

    /* Metric Styling */
    .stMetric {
        background-color: #E9C46A;
        color: #1D3557;
        border-radius: 4px;
        padding: 1rem;
        width: 100% !important;
    }

    /* Input Elements */
    .stExpander {
        background-color: white;
        border: 1px solid #1D3557;
        border-radius: 4px;
        width: 100% !important;
    }

    .stTextArea>div>div>textarea {
        background-color: white;
        border: 1px solid #1D3557;
        width: 100% !important;
    }

    .stSelectbox>div>div>div {
        background-color: white;
        border: 1px solid #1D3557;
        width: 100% !important;
    }

    .stFileUploader>div {
        background-color: white;
        border: 1px solid #1D3557;
        width: 100% !important;
    }

    /* Footer Styling */
    footer {
        text-align: center;
        padding: 1rem;
        color: #1D3557;
        margin-top: 2rem;
        background-color: white;
        width: 100% !important;
    }

    /* Custom Highlights */
    .highlight {
        background-color: #E9C46A;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
    }

    .success-highlight {
        background-color: #2A9D8F;
        color: white;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
    }

    .warning-highlight {
        background-color: #F4A261;
        color: white;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
    }

    /* Responsive Design */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem 1rem;
        }

        .main-header h1 {
            font-size: 2rem;
        }

        .row-widget.stHorizontal {
            flex-direction: column;
        }

        .stButton>button {
            margin: 0.5rem 0;
        }
    }

    /* Make columns responsive */
    .row-widget.stHorizontal {
        flex-wrap: wrap;
        gap: 1rem;
    }

    /* Ensure proper scaling of content inside expanders */
    .streamlit-expanderHeader, 
    .streamlit-expanderContent {
        width: 100% !important;
    }

    /* Make sure content scales properly */
    .stMarkdown, 
    .stText, 
    .stTextArea {
        width: 100% !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb {
        background: #1D3557;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #2A9D8F;
    }
    </style>

    <script>
        // Function to update height
        function updateHeight() {
            const doc = document.documentElement;
            doc.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
        }

        // Update on first load
        updateHeight();

        // Update on resize
        window.addEventListener('resize', updateHeight);
    </script>
    <style>
        .stApp {
            height: calc(var(--vh, 1vh) * 100) !important;
        }
    </style>
    <style>
    /* Modify button styling for Start Analysis */
    .stButton>button {
        background-color: #1D3557;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.3rem 0.8rem;  /* Reduced padding */
        width: auto !important;  /* Override full width */
        font-size: 0.9rem;      /* Smaller font size */
        margin-top: 0.2rem !important;  /* Small gap after header */
        margin-bottom: 1rem;
    }

    /* Container for Analyze Compatibility section */
    h3:contains("🔍 Analyze Compatibility") {
        margin-bottom: 0.2rem !important;  /* Reduce space between header and button */
        padding-bottom: 0 !important;
    }

    /* Adjust spacing after the button */
    .stButton {
        margin-bottom: 1.5rem;  /* Space after the button */
    }

    /* Make button container align properly */
    .stButton>div {
        display: flex;
        justify-content: flex-start;  /* Align to the left */
    }

    /* Rest of your existing styles... */
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>🚀 Resume Enhancer</h1>
        <p>Upload your Resume and Job Description to get personalized enhancement suggestions and ATS optimization.</p>
    </div>
""", unsafe_allow_html=True)

# Session state
for key in ["resume_text", "jd_text", "enhanced_resume", "analysis_result", "enhanced_resume_text"]:
    if key not in st.session_state:
        st.session_state[key] = None

# -------- Functions --------

def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        doc = fitz.open(tmp_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    else:
        return uploaded_file.read().decode('utf-8')

def call_groq_llama(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        return None

def analyze_resume(resume_text, jd_text):
    prompt = f"""
You are an expert recruiter and career consultant.

Given a candidate's resume and a job description (JD):
- Assess how well the resume aligns with the JD.
- Give a *Compatibility Score out of 100*.
- Highlight *Top 3-5 Strengths* where the resume matches the JD.
- Point out *Top 3-5 Gaps or Improvements* needed to better align with the JD.
- Be detailed, specific, and professional.
- Focus on skills, experiences, certifications, technical expertise, and ATS keywords.
- Avoid generic statements; back your points with resume or JD references.

Resume:
{resume_text}

Job Description:
{jd_text}
"""
    return call_groq_llama("You are an expert recruiter analyzing resumes.", prompt)

def create_word_resume(enhanced_resume_text):
    doc = Document()
    doc.add_paragraph(enhanced_resume_text)
    save_path = 'Enhanced_Resume.docx'
    doc.save(save_path)
    return save_path

def call_gemini_enhance_resume(resume_text, jd_text, reference_text):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
You are a professional resume writer and career coach specialized in ATS optimization.

Given a candidate's resume, a job description, and some additional material:
- Rewrite and enhance the resume to maximize compatibility.
- Incorporate missing important skills, tools, certifications, and responsibilities.
- Improve phrasing to be professional, quantifiable, and impact-driven.
- Ensure ATS-friendliness.

Resume:
{resume_text}

Job Description:
{jd_text}

Reference Material:
{reference_text}

Return ONLY the enhanced full resume, no extra explanations.
"""
    response = model.generate_content(prompt)
    return response.text

# -------------------- UI --------------------

# File Upload Section
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3>📄 Upload Your Resume</h3>", unsafe_allow_html=True)
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "txt"], key="resume_uploader")
with col2:
    st.markdown("<h3>📋 Upload Job Description</h3>", unsafe_allow_html=True)
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "txt"], key="jd_uploader")

# Process uploaded files
if resume_file and jd_file:
    st.session_state.resume_text = extract_text(resume_file)
    st.session_state.jd_text = extract_text(jd_file)
    
    # Analysis Section
    st.markdown("<h3>🔍 Analyze Compatibility</h3>", unsafe_allow_html=True)
    
    if st.button("Start Analysis"):
        with st.spinner("Analyzing your resume..."):
            analysis_result = analyze_resume(
                st.session_state.resume_text, st.session_state.jd_text
            )
            st.session_state.analysis_result = analysis_result

    if st.session_state.analysis_result:
        analysis_result = st.session_state.analysis_result
        
        # Updated score extraction!
        score_match = re.search(r"Compatibility Score[:\s]*([\d]{1,3})", analysis_result, re.IGNORECASE)
        score = score_match.group(1) if score_match else "N/A"

        st.metric("Compatibility Score", f"{score}/100")

        strengths = []
        improvements = []
        strengths_match = re.search(
            r"(?:Strengths|Top Strengths|Strength):([\s\S]*?)(?:Gaps|Improvements|Areas to Improve|$)", 
            analysis_result, re.IGNORECASE
        )
        improvements_match = re.search(
            r"(?:Gaps|Improvements|Areas to Improve):([\s\S]*)", 
            analysis_result, re.IGNORECASE
        )
        
        if strengths_match:
            strengths = [line.strip(" -•\n") for line in strengths_match.group(1).split('\n') if line.strip()]
        if improvements_match:
            improvements = [line.strip(" -•\n") for line in improvements_match.group(1).split('\n') if line.strip()]

        strengths = [point for point in strengths if point.strip() != "**"]
        improvements = [point for point in improvements if point.strip() != "**"]

        col1, col2 = st.columns(2)

        # Strengths
        if strengths:
            with col1:
                st.subheader("✅ Strengths")
                for point in strengths:
                    clean_point = point.replace('•', '').strip()
                    clean_point = re.sub(r'\*\*(.*?)\*\*', r'**\1**', clean_point)
                    if "Top 3" not in clean_point and clean_point != "":
                        st.success(clean_point)

        # Areas to Improve
        if improvements:
            with col2:
                st.subheader("🔄 Areas to Improve")
                for point in improvements:
                    clean_point = point.replace('•', '').strip()
                    clean_point = re.sub(r'\*\*(.*?)\*\*', r'**\1**', clean_point)
                    if "Top 3" not in clean_point and clean_point != "":
                        st.warning(clean_point)


        # Full Analysis Text
        with st.expander("📋 View Full Analysis"):
            st.text_area(
                label="Analysis Results",
                value=analysis_result,
                height=300,
                key="analysis_text_area"
            )

    # Enhancement Section
    st.markdown("<h3>✨ Enhance Resume</h3>", unsafe_allow_html=True)
    
    if st.button("Generate Enhanced Resume"):
        with st.spinner("Enhancing your resume..."):
            reference_text = "N/A"  # You can add your own reference material here
            enhanced_resume_text = call_gemini_enhance_resume(
                st.session_state.resume_text,
                st.session_state.jd_text,
                reference_text
            )
            st.session_state.enhanced_resume_text = enhanced_resume_text

            if enhanced_resume_text:
                enhanced_resume_path = create_word_resume(enhanced_resume_text)
                st.session_state.enhanced_resume = enhanced_resume_path
                st.success("✨ Resume enhancement completed!")

    if st.session_state.enhanced_resume_text and st.session_state.enhanced_resume:
        st.subheader("📄 Enhanced Resume Preview")
        with st.expander("Show Enhanced Resume"):
            st.text_area(
                label="Enhanced Resume Content",
                value=st.session_state.enhanced_resume_text,
                height=400,
                key="enhanced_resume_text_area"
            )

        with open(st.session_state.enhanced_resume, "rb") as file:
            st.download_button(
                label="📥 Download Enhanced Resume (DOCX)",
                data=file,
                file_name="enhanced_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )