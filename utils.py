import json
import re
import time
import os
from typing import Dict, Any, Optional, Tuple
from config import (
    ERROR_MESSAGES,
    MAX_FILE_SIZE,
    SUPPORTED_FILE_TYPES,
    MAX_RETRIES,
    RETRY_DELAY,
)
from logging_config import get_logger, log_function_call, log_performance

# Initialize logger
logger = get_logger(__name__)


@log_function_call
def format_analysis_output(analysis: Dict[str, Any] | str) -> str:
    """Format the analysis results into a readable markdown output"""
    start_time = time.time()
    logger.info("Formatting analysis output")
    
    if not isinstance(analysis, dict):
        logger.warning("Analysis is not a dictionary, returning as string")
        return str(analysis)

    logger.debug(f"Analysis keys: {list(analysis.keys())}")
    
    output = f"""
## 📊 ATS Score: {analysis.get('ats_score', 'N/A')}/100

### 📈 Score Explanation
{analysis.get('score_explanation', 'No explanation available')}

### ✅ Strengths
"""

    strengths = analysis.get("strengths", [])
    logger.debug(f"Formatting {len(strengths)} strengths")
    for strength in strengths:
        output += f"• {strength}\n"

    output += "\n### ❌ Areas for Improvement\n"
    weaknesses = analysis.get("weaknesses", [])
    logger.debug(f"Formatting {len(weaknesses)} weaknesses")
    for weakness in weaknesses:
        output += f"• {weakness}\n"

    output += "\n### 💡 Recommendations\n"
    recommendations = analysis.get("recommendations", [])
    logger.debug(f"Formatting {len(recommendations)} recommendations")
    for rec in recommendations:
        output += f"• {rec}\n"

    output += "\n### 🔍 Skills Gap Analysis\n"
    skills_gap = analysis.get("skills_gap", [])
    logger.debug(f"Formatting {len(skills_gap)} skills gaps")
    for skill in skills_gap:
        output += f"• {skill}\n"

    output += "\n### 🚀 Upskilling Suggestions\n"
    upskilling = analysis.get("upskilling_suggestions", [])
    logger.debug(f"Formatting {len(upskilling)} upskilling suggestions")
    for suggestion in upskilling:
        output += f"• {suggestion}\n"

    output += f"\n### 📋 Overall Assessment\n{analysis.get('overall_assessment', 'No assessment available')}"

    output_length = len(output)
    logger.info(f"Analysis output formatted successfully. Length: {output_length} characters")
    
    duration = time.time() - start_time
    log_performance("Analysis output formatting", duration, f"Formatted output with {len(strengths)} strengths, {len(weaknesses)} weaknesses, {len(recommendations)} recommendations")
    
    return output


@log_function_call
def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text response with improved error handling"""
    start_time = time.time()
    logger.info("Extracting JSON from text")
    logger.debug(f"Text length: {len(text) if text else 0}")
    
    if not text:
        logger.warning("No text provided for JSON extraction")
        return None

    try:
        # Find JSON in the response
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        
        logger.debug(f"JSON boundaries: start={start_idx}, end={end_idx}")
        
        if start_idx != -1 and end_idx != 0:
            json_str = text[start_idx:end_idx]
            logger.debug(f"Extracted JSON string length: {len(json_str)}")
            
            result = json.loads(json_str)
            logger.info("JSON extraction successful")
            
            duration = time.time() - start_time
            log_performance("JSON extraction", duration, f"Extracted JSON with {len(json_str)} characters")
            
            return result
        else:
            logger.warning("No JSON brackets found in text")
            return None
            
    except (json.JSONDecodeError, ValueError) as e:
        duration = time.time() - start_time
        logger.error(f"JSON extraction failed after {duration:.3f}s: {e}")
        return None


def create_fallback_analysis(analysis_text: str) -> Dict[str, Any]:
    """Create a fallback analysis structure when JSON parsing fails"""
    return {
        "ats_score": "Analysis completed",
        "score_explanation": analysis_text,
        "strengths": ["Analysis completed"],
        "weaknesses": ["See detailed feedback"],
        "recommendations": ["Review the analysis above"],
        "skills_gap": ["Check the analysis"],
        "upskilling_suggestions": ["Refer to recommendations"],
        "overall_assessment": analysis_text,
    }


def create_error_analysis(error_message: str) -> Dict[str, Any]:
    """Create an error analysis structure with detailed error information"""
    return {
        "ats_score": "Error",
        "score_explanation": f"Error during analysis: {error_message}",
        "strengths": [],
        "weaknesses": [],
        "recommendations": [
            "Please try again or contact support if the issue persists"
        ],
        "skills_gap": [],
        "upskilling_suggestions": [],
        "overall_assessment": f"Error occurred: {error_message}",
    }


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length with ellipsis"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def clean_text(text: str) -> str:
    """Clean and normalize text with improved error handling"""
    if not text:
        return ""

    try:
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters that might cause issues
        text = re.sub(r"[^\w\s\.\,\!\?\-\:\;\(\)\[\]\{\}]", "", text)

        return text.strip()
    except Exception as e:
        print(f"Text cleaning error: {e}")
        return text.strip() if text else ""


@log_function_call
def validate_inputs(pdf_file, job_description: str) -> Tuple[bool, str]:
    """Validate user inputs with comprehensive error checking"""
    start_time = time.time()
    logger.info("Validating user inputs")
    logger.debug(f"PDF file: {pdf_file}")
    logger.debug(f"Job description length: {len(job_description) if job_description else 0}")
    
    try:
        # Check if PDF file is provided
        if pdf_file is None:
            logger.error("PDF file is None")
            return False, ERROR_MESSAGES["no_pdf"]

        # Check if file exists
        if not os.path.exists(pdf_file):
            logger.error(f"File does not exist: {pdf_file}")
            return False, ERROR_MESSAGES["invalid_file"]

        # Check file size
        file_size = os.path.getsize(pdf_file)
        logger.debug(f"File size: {file_size} bytes")
        if file_size > MAX_FILE_SIZE:
            logger.error(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
            return False, ERROR_MESSAGES["file_too_large"]

        # Check file extension
        file_ext = os.path.splitext(pdf_file)[1].lower()
        logger.debug(f"File extension: '{file_ext}'")
        logger.debug(f"Supported extensions: {SUPPORTED_FILE_TYPES}")
        if file_ext not in SUPPORTED_FILE_TYPES:
            logger.error(f"Unsupported file extension: '{file_ext}'")
            return False, ERROR_MESSAGES["invalid_file"]

        # Check job description
        if not job_description or not job_description.strip():
            logger.error("Job description is empty")
            return False, ERROR_MESSAGES["no_job_desc"]

        # Check if job description is too short
        job_desc_length = len(job_description.strip())
        logger.debug(f"Job description length: {job_desc_length} characters")
        if job_desc_length < 10:
            logger.warning(f"Job description too short: {job_desc_length} characters")
            return (
                False,
                "Please provide a more detailed job description (at least 10 characters).",
            )

        logger.info("Input validation successful")
        duration = time.time() - start_time
        log_performance("Input validation", duration, f"Validated file ({file_size} bytes) and job description ({job_desc_length} characters)")
        
        return True, ""

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Input validation failed after {duration:.3f}s: {str(e)}", exc_info=True)
        return False, f"Validation error: {str(e)}"


@log_function_call
def retry_with_backoff(func, *args, **kwargs):
    """Retry function with exponential backoff"""
    start_time = time.time()
    func_name = func.__name__ if hasattr(func, '__name__') else 'unknown'
    logger.info(f"Starting retry logic for function: {func_name}")
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"Attempt {attempt + 1}/{MAX_RETRIES} for function: {func_name}")
            result = func(*args, **kwargs)
            logger.info(f"Function {func_name} succeeded on attempt {attempt + 1}")
            return result
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for function {func_name}: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                duration = time.time() - start_time
                logger.error(f"Function {func_name} failed after {MAX_RETRIES} attempts in {duration:.3f}s")
                raise e
            delay = RETRY_DELAY * (2**attempt)
            logger.info(f"Waiting {delay}s before retry")
            time.sleep(delay)
    return None


@log_function_call
def handle_api_error(error: Exception) -> str:
    """Handle different types of API errors and return appropriate messages"""
    error_str = str(error).lower()
    logger.info(f"Handling API error: {type(error).__name__}")

    if "rate limit" in error_str or "429" in error_str:
        logger.warning("Rate limit error detected")
        return ERROR_MESSAGES["rate_limit_error"]
    elif "timeout" in error_str or "timed out" in error_str or "timedout" in error_str:
        logger.warning("Timeout error detected")
        return ERROR_MESSAGES["timeout_error"]
    elif "network" in error_str or "connection" in error_str:
        logger.warning("Network error detected")
        return ERROR_MESSAGES["network_error"]
    elif "server" in error_str or "500" in error_str:
        logger.warning("Server error detected")
        return ERROR_MESSAGES["server_error"]
    elif "api key" in error_str or "authentication" in error_str:
        logger.warning("Authentication error detected")
        return ERROR_MESSAGES["api_key_missing"]
    else:
        logger.warning(f"Unknown error type: {error_str}")
        return ERROR_MESSAGES["unknown_error"]


@log_function_call
def validate_file_content(file_path: str) -> Tuple[bool, str]:
    """Validate file content and structure"""
    start_time = time.time()
    logger.info(f"Validating file content: {file_path}")
    
    try:
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False, "File does not exist"

        # Check if file is readable
        with open(file_path, "rb") as f:
            # Read first few bytes to check if it's a valid PDF
            header = f.read(4)
            logger.debug(f"File header: {header}")
            if header != b"%PDF":
                logger.error(f"Invalid PDF header: {header}")
                return False, "Invalid PDF file format"

        logger.info("File content validation successful")
        duration = time.time() - start_time
        log_performance("File content validation", duration, f"Validated PDF file: {file_path}")
        
        return True, ""

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"File content validation failed after {duration:.3f}s: {str(e)}", exc_info=True)
        return False, f"File validation error: {str(e)}"


@log_function_call
def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    start_time = time.time()
    logger.info("Sanitizing user input")
    logger.debug(f"Input length: {len(text) if text else 0}")
    
    if not text:
        logger.debug("Empty input, returning empty string")
        return ""

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", "script", "javascript"]
    sanitized = text
    chars_removed = 0
    
    for char in dangerous_chars:
        if char in sanitized:
            sanitized = sanitized.replace(char, "")
            chars_removed += 1

    result = sanitized.strip()
    logger.debug(f"Sanitization complete. Removed {chars_removed} dangerous characters")
    logger.debug(f"Output length: {len(result)}")
    
    duration = time.time() - start_time
    log_performance("Input sanitization", duration, f"Sanitized {len(text)} characters, removed {chars_removed} dangerous chars")
    
    return result
