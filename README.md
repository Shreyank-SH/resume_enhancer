# Resume Enhancer

A Streamlit application that helps users optimize their resumes for specific job descriptions using AI-powered analysis and enhancement suggestions.

## Features

- Resume and Job Description Analysis
- ATS Compatibility Score
- Strengths and Areas of Improvement Analysis
- AI-powered Resume Enhancement
- Downloadable Enhanced Resume in DOCX format

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your API keys:
```
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

3. Run the application:
```bash
streamlit run app.py
```

## Deployment

This application is ready to be deployed on Streamlit Cloud. Make sure to:
1. Add your API keys in the Streamlit Cloud secrets management
2. Connect your GitHub repository to Streamlit Cloud
3. Deploy using the main branch

## Technologies Used

- Streamlit
- Groq AI
- Google Gemini
- PyMuPDF
- python-docx 