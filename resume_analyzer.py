import PyPDF2
import os
import time
from openai import OpenAI
from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    OPENROUTER_TEMPERATURE,
    OPENROUTER_MAX_TOKENS,
    OPENROUTER_SITE_URL,
    OPENROUTER_SITE_NAME,
    ERROR_MESSAGES,
)
from utils import (
    format_analysis_output,
    extract_json_from_text,
    create_fallback_analysis,
    create_error_analysis,
    validate_inputs,
    retry_with_backoff,
    handle_api_error,
    validate_file_content,
    sanitize_input,
)
from logging_config import get_logger, log_function_call, log_api_call, log_file_operation, log_performance

# Initialize logger
logger = get_logger(__name__)


@log_function_call
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file with comprehensive error handling"""
    start_time = time.time()
    logger.info(f"Starting PDF text extraction for file: {pdf_file}")
    
    try:
        # Validate file content first
        logger.debug("Validating file content")
        is_valid, error_msg = validate_file_content(pdf_file)
        if not is_valid:
            logger.error(f"File validation failed: {error_msg}")
            log_file_operation("validation", pdf_file, success=False, error=error_msg)
            return f"Error: {error_msg}"

        logger.info("File validation successful, proceeding with text extraction")
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        total_pages = len(pdf_reader.pages)
        
        logger.info(f"PDF has {total_pages} pages")

        # Check if PDF has pages
        if total_pages == 0:
            logger.error("PDF file appears to be empty or corrupted")
            log_file_operation("extraction", pdf_file, success=False, error="Empty PDF")
            return "Error: PDF file appears to be empty or corrupted."

        successful_pages = 0
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                logger.debug(f"Extracting text from page {page_num + 1}")
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    successful_pages += 1
                    logger.debug(f"Successfully extracted {len(page_text)} characters from page {page_num + 1}")
                else:
                    logger.warning(f"Page {page_num + 1} appears to be empty or unreadable")
            except Exception as e:
                logger.error(f"Error extracting text from page {page_num + 1}: {e}")
                continue

        logger.info(f"Text extraction completed. {successful_pages}/{total_pages} pages processed successfully")

        if not text.strip():
            logger.error("No readable text found in the PDF")
            log_file_operation("extraction", pdf_file, success=False, error="No readable text")
            return "Error: No readable text found in the PDF. The file might be scanned images or corrupted."

        extracted_text_length = len(text.strip())
        logger.info(f"Successfully extracted {extracted_text_length} characters from PDF")
        log_file_operation("extraction", pdf_file, success=True, file_size=extracted_text_length)
        
        duration = time.time() - start_time
        log_performance("PDF text extraction", duration, f"Extracted {extracted_text_length} characters from {successful_pages} pages")
        
        return text.strip()

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"PDF text extraction failed after {duration:.3f}s: {str(e)}", exc_info=True)
        log_file_operation("extraction", pdf_file, success=False, error=str(e))
        
        if "PDF" in str(e).upper() or "corrupt" in str(e).lower():
            return f"Error: Invalid or corrupted PDF file - {str(e)}"
        else:
            return f"Error extracting text from PDF: {str(e)}"


@log_function_call
def analyze_resume(resume_text, job_description):
    """Analyze resume against job description using OpenAI with enhanced error handling"""
    start_time = time.time()
    logger.info("Starting resume analysis")
    logger.debug(f"Resume text length: {len(resume_text) if resume_text else 0}")
    logger.debug(f"Job description length: {len(job_description) if job_description else 0}")
    
    if not resume_text or not job_description:
        logger.warning("Missing resume text or job description")
        return ERROR_MESSAGES["no_job_desc"]

    # Sanitize inputs
    logger.debug("Sanitizing inputs")
    resume_text = sanitize_input(resume_text)
    job_description = sanitize_input(job_description)
    logger.debug(f"Sanitized resume text length: {len(resume_text)}")
    logger.debug(f"Sanitized job description length: {len(job_description)}")

                # Check if OpenRouter API key is available
    logger.info(f"OpenRouter API key configured: {bool(OPENROUTER_API_KEY)}")
    logger.info(f"OpenRouter API key starts with: {OPENROUTER_API_KEY[:10] if OPENROUTER_API_KEY else 'None'}...")
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        logger.warning("OpenRouter API key not configured, returning demo message")
        return """
## ⚠️ OpenRouter API Key Not Configured

To get full AI-powered analysis, please:

1. Get your OpenRouter API key from: https://openrouter.ai/keys
2. Create a `.env` file in the project directory
3. Add your API key: `OPENROUTER_API_KEY=your_actual_api_key_here`
4. Restart the application

**For now, you can use the demo version by running:**
```bash
python demo.py
```

This will show you the interface without requiring an API key.
"""

    def make_api_call():
        """Make the actual API call with retry logic"""
        logger.info("Making OpenRouter API call for resume analysis")
        
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

        logger.debug(f"Prompt length: {len(prompt)} characters")
        logger.debug(f"Using model: {OPENROUTER_MODEL}, temperature: {OPENROUTER_TEMPERATURE}, max_tokens: {OPENROUTER_MAX_TOKENS}")

        # Call OpenRouter API using the OpenAI-compatible client
        client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
        
        api_start_time = time.time()
        try:
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": OPENROUTER_SITE_URL,
                    "X-Title": OPENROUTER_SITE_NAME,
                },
                extra_body={},
                model=OPENROUTER_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a top 1% HR manager with exceptional talent evaluation skills. Provide thorough, fair, and constructive resume analysis.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=OPENROUTER_TEMPERATURE,
                max_tokens=OPENROUTER_MAX_TOKENS,
            )
            
            api_duration = time.time() - api_start_time
            logger.info(f"OpenRouter API call successful in {api_duration:.3f}s")
            log_api_call("OpenRouter Chat Completions", 
                        request_data={"model": OPENROUTER_MODEL, "temperature": OPENROUTER_TEMPERATURE, "max_tokens": OPENROUTER_MAX_TOKENS},
                        response_data={"response_length": len(response.choices[0].message.content)},
                        success=True)
            
            return response.choices[0].message.content
            
        except Exception as e:
            api_duration = time.time() - api_start_time
            logger.error(f"OpenRouter API call failed after {api_duration:.3f}s: {str(e)}")
            log_api_call("OpenRouter Chat Completions", 
                        request_data={"model": OPENROUTER_MODEL, "temperature": OPENROUTER_TEMPERATURE, "max_tokens": OPENROUTER_MAX_TOKENS},
                        success=False, error=str(e))
            raise

    try:
        # Use retry logic for API calls
        logger.info("Starting retry logic for API calls")
        analysis_text = retry_with_backoff(make_api_call)

        if not analysis_text:
            logger.error("Failed to get response from AI service after multiple attempts")
            return create_error_analysis(
                "Failed to get response from AI service after multiple attempts"
            )

        logger.info(f"Received analysis text of length: {len(analysis_text)}")
        logger.debug(f"Analysis text preview: {analysis_text[:200]}...")

        # Try to extract JSON from the response
        logger.debug("Attempting to extract JSON from response")
        logger.debug(f"Raw API response: {analysis_text[:500]}...")
        analysis = extract_json_from_text(analysis_text)
        if analysis is None:
            logger.warning("No JSON found in response, creating fallback analysis")
            # If no JSON found, create a structured response
            analysis = create_fallback_analysis(analysis_text)
        else:
            logger.info("Successfully extracted JSON from response")
            logger.debug(f"Extracted analysis keys: {list(analysis.keys())}")
            logger.debug(f"ATS Score: {analysis.get('ats_score')}")
            logger.debug(f"Strengths count: {len(analysis.get('strengths', []))}")

        duration = time.time() - start_time
        log_performance("Resume analysis", duration, f"Analysis completed with {len(analysis_text)} characters")
        
        return analysis

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Resume analysis failed after {duration:.3f}s: {str(e)}", exc_info=True)
        error_message = handle_api_error(e)
        return create_error_analysis(error_message)


@log_function_call
def process_resume_analysis(pdf_file, job_description):
    """Main function to process resume analysis with comprehensive error handling"""
    start_time = time.time()
    logger.info(f"Starting resume analysis process for file: {pdf_file}")
    logger.debug(f"Job description length: {len(job_description) if job_description else 0}")
    
    try:
        # Validate inputs
        logger.info("Validating inputs")
        is_valid, error_message = validate_inputs(pdf_file, job_description)
        if not is_valid:
            logger.error(f"Input validation failed: {error_message}")
            return f"## ❌ Input Validation Error\n\n{error_message}"

        logger.info("Input validation successful")

        # Extract text from PDF
        logger.info("Extracting text from PDF")
        resume_text = extract_text_from_pdf(pdf_file)

        if resume_text.startswith("Error"):
            logger.error(f"PDF processing failed: {resume_text}")
            return f"## ❌ PDF Processing Error\n\n{resume_text}"

        # Check if extracted text is meaningful
        text_length = len(resume_text.strip())
        logger.info(f"Extracted text length: {text_length} characters")
        
        if text_length < 50:
            logger.warning(f"Extracted text too short: {text_length} characters")
            return "## ❌ Insufficient Content\n\nThe PDF appears to contain very little text. Please ensure you've uploaded a text-based PDF (not scanned images)."

        # Analyze resume
        logger.info("Starting resume analysis")
        analysis = analyze_resume(resume_text, job_description)
        
        duration = time.time() - start_time
        logger.info(f"Resume analysis process completed successfully in {duration:.3f}s")
        log_performance("Complete resume analysis process", duration, f"Processed {text_length} characters of resume text")
        
        return analysis

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Resume analysis process failed after {duration:.3f}s: {str(e)}", exc_info=True)
        error_message = handle_api_error(e)
        return f"## ❌ Unexpected Error\n\n{error_message}\n\nPlease try again or contact support if the issue persists."
