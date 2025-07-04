import PyPDF2
import os
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS, ERROR_MESSAGES
from utils import format_analysis_output, extract_json_from_text, create_fallback_analysis, create_error_analysis, validate_inputs

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def analyze_resume(resume_text, job_description):
    """Analyze resume against job description using OpenAI"""
    if not resume_text or not job_description:
        return ERROR_MESSAGES["no_job_desc"]
    
    # Check if OpenAI API key is available
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        return """
## ⚠️ OpenAI API Key Not Configured

To get full AI-powered analysis, please:

1. Get your OpenAI API key from: https://platform.openai.com/api-keys
2. Create a `.env` file in the project directory
3. Add your API key: `OPENAI_API_KEY=your_actual_api_key_here`
4. Restart the application

**For now, you can use the demo version by running:**
```bash
python demo.py
```

This will show you the interface without requiring an API key.
"""
    
    try:
        # Create the analysis prompt
        prompt = f"""
        You are an expert ATS (Applicant Tracking System) analyst and career coach. 
        
        Please analyze the following resume against the job description and provide:
        
        1. ATS Score (0-100) - How well the resume matches the job requirements, be lenient with the score don't be too strict
        2. Detailed analysis of strengths and weaknesses
        3. Specific recommendations for improvement
        4. Skills gap analysis and upskilling suggestions
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Please provide your analysis in the following JSON format:
        {{
            "ats_score": <score>,
            "score_explanation": "<explanation of the score>",
            "strengths": ["<strength1>", "<strength2>", ...],
            "weaknesses": ["<weakness1>", "<weakness2>", ...],
            "recommendations": ["<recommendation1>", "<recommendation2>", ...],
            "skills_gap": ["<missing_skill1>", "<missing_skill2>", ...],
            "upskilling_suggestions": ["<suggestion1>", "<suggestion2>", ...],
            "overall_assessment": "<overall assessment>"
        }}
        """
        
        # Call OpenAI API using the newer syntax
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert ATS analyst and career coach. Provide detailed, actionable feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        # Parse the response
        analysis_text = response.choices[0].message.content
        
        # Try to extract JSON from the response
        analysis = extract_json_from_text(analysis_text)
        if analysis is None:
            # If no JSON found, create a structured response
            analysis = create_fallback_analysis(analysis_text)
        
        return analysis
        
    except Exception as e:
        return create_error_analysis(str(e))

def process_resume_analysis(pdf_file, job_description):
    """Main function to process resume analysis"""
    # Validate inputs
    is_valid, error_message = validate_inputs(pdf_file, job_description)
    if not is_valid:
        return error_message
    
    # Extract text from PDF
    resume_text = extract_text_from_pdf(pdf_file)
    
    if resume_text.startswith("Error"):
        return resume_text
    
    # Analyze resume
    analysis = analyze_resume(resume_text, job_description)
    
    # Format the output using utility function
    return format_analysis_output(analysis) 