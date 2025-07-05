import PyPDF2
import os
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS, ERROR_MESSAGES
from utils import (
    format_analysis_output, extract_json_from_text, create_fallback_analysis, 
    create_error_analysis, validate_inputs, retry_with_backoff, handle_api_error,
    validate_file_content, sanitize_input
)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file with comprehensive error handling"""
    try:
        # Validate file content first
        is_valid, error_msg = validate_file_content(pdf_file)
        if not is_valid:
            return f"Error: {error_msg}"
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Check if PDF has pages
        if len(pdf_reader.pages) == 0:
            return "Error: PDF file appears to be empty or corrupted."
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    print(f"Warning: Page {page_num + 1} appears to be empty or unreadable")
            except Exception as e:
                print(f"Error extracting text from page {page_num + 1}: {e}")
                continue
        
        if not text.strip():
            return "Error: No readable text found in the PDF. The file might be scanned images or corrupted."
        
        return text.strip()
        
    except Exception as e:
        if "PDF" in str(e).upper() or "corrupt" in str(e).lower():
            return f"Error: Invalid or corrupted PDF file - {str(e)}"
        else:
            return f"Error extracting text from PDF: {str(e)}"

def analyze_resume(resume_text, job_description):
    """Analyze resume against job description using OpenAI with enhanced error handling"""
    if not resume_text or not job_description:
        return ERROR_MESSAGES["no_job_desc"]
    
    # Sanitize inputs
    resume_text = sanitize_input(resume_text)
    job_description = sanitize_input(job_description)
    
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
    
    def make_api_call():
        """Make the actual API call with retry logic"""
        # Create the enhanced analysis prompt for top 1% HR manager
        prompt = f"""
        You are a top 1% HR manager in the world with 20+ years of experience at Fortune 500 companies. 
        You have hired thousands of candidates and have an exceptional eye for talent evaluation.
        
        Your task is to critically analyze the following resume against the job description with the expertise 
        of a senior HR executive who has seen tens of thousands of resumes.
        
        **CRITICAL ANALYSIS REQUIREMENTS:**
        1. **ATS Score (0-100)** - Be LENIENT and FAIR in your scoring. Consider that candidates often have 
           transferable skills and potential that may not be immediately obvious. Don't be overly strict.
        2. **Comprehensive Strengths Analysis** - Identify ALL strengths, including soft skills, potential, 
           and transferable experience
        3. **Constructive Weaknesses** - Provide specific, actionable feedback that helps the candidate improve
        4. **Skills Gap Analysis** - Identify missing skills with realistic assessment of learning difficulty
        5. **Strategic Recommendations** - Provide specific, actionable advice for improvement
        
        **RESUME TO ANALYZE:**
        {resume_text}
        
        **JOB DESCRIPTION:**
        {job_description}
        
        **ANALYSIS INSTRUCTIONS:**
        - Be thorough but fair in your assessment
        - Consider both explicit and implicit qualifications
        - Provide constructive, actionable feedback
        - Be encouraging while being honest about areas for improvement
        - Consider the candidate's potential and growth trajectory
        
        Please provide your analysis in the following JSON format:
        {{
            "ats_score": <score_between_0_and_100>,
            "score_explanation": "<detailed_explanation_of_why_this_score_was_given>",
            "strengths": ["<strength1>", "<strength2>", ...],
            "weaknesses": ["<weakness1>", "<weakness2>", ...],
            "recommendations": ["<specific_actionable_recommendation1>", "<recommendation2>", ...],
            "skills_gap": ["<missing_skill1>", "<missing_skill2>", ...],
            "upskilling_suggestions": ["<specific_upskilling_suggestion1>", "<suggestion2>", ...],
            "overall_assessment": "<comprehensive_assessment_with_encouraging_tone>"
        }}
        
        Remember: You are evaluating a real person's career prospects. Be thorough, fair, and constructive.
        """
        
        # Call OpenAI API using the newer syntax
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a top 1% HR manager with exceptional talent evaluation skills. Provide thorough, fair, and constructive resume analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        return response.choices[0].message.content
    
    try:
        # Use retry logic for API calls
        analysis_text = retry_with_backoff(make_api_call)
        
        if not analysis_text:
            return create_error_analysis("Failed to get response from AI service after multiple attempts")
        
        # Try to extract JSON from the response
        analysis = extract_json_from_text(analysis_text)
        if analysis is None:
            # If no JSON found, create a structured response
            analysis = create_fallback_analysis(analysis_text)
        
        return analysis
        
    except Exception as e:
        error_message = handle_api_error(e)
        return create_error_analysis(error_message)

def process_resume_analysis(pdf_file, job_description):
    """Main function to process resume analysis with comprehensive error handling"""
    try:
        # Validate inputs
        is_valid, error_message = validate_inputs(pdf_file, job_description)
        if not is_valid:
            return f"## ❌ Input Validation Error\n\n{error_message}"
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(pdf_file)
        
        if resume_text.startswith("Error"):
            return f"## ❌ PDF Processing Error\n\n{resume_text}"
        
        # Check if extracted text is meaningful
        if len(resume_text.strip()) < 50:
            return "## ❌ Insufficient Content\n\nThe PDF appears to contain very little text. Please ensure you've uploaded a text-based PDF (not scanned images)."
        
        # Analyze resume
        analysis = analyze_resume(resume_text, job_description)
        
        # Format the output using utility function
        return format_analysis_output(analysis)
        
    except Exception as e:
        error_message = handle_api_error(e)
        return f"## ❌ Unexpected Error\n\n{error_message}\n\nPlease try again or contact support if the issue persists." 