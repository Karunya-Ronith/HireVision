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


def format_analysis_output(analysis: Dict[str, Any] | str) -> str:
    """Format the analysis results into a readable markdown output"""
    if not isinstance(analysis, dict):
        return str(analysis)

    output = f"""
## 📊 ATS Score: {analysis.get('ats_score', 'N/A')}/100

### 📈 Score Explanation
{analysis.get('score_explanation', 'No explanation available')}

### ✅ Strengths
"""

    for strength in analysis.get("strengths", []):
        output += f"• {strength}\n"

    output += "\n### ❌ Areas for Improvement\n"
    for weakness in analysis.get("weaknesses", []):
        output += f"• {weakness}\n"

    output += "\n### 💡 Recommendations\n"
    for rec in analysis.get("recommendations", []):
        output += f"• {rec}\n"

    output += "\n### 🔍 Skills Gap Analysis\n"
    for skill in analysis.get("skills_gap", []):
        output += f"• {skill}\n"

    output += "\n### 🚀 Upskilling Suggestions\n"
    for suggestion in analysis.get("upskilling_suggestions", []):
        output += f"• {suggestion}\n"

    output += f"\n### 📋 Overall Assessment\n{analysis.get('overall_assessment', 'No assessment available')}"

    return output


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text response with improved error handling"""
    if not text:
        return None

    try:
        # Find JSON in the response
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        if start_idx != -1 and end_idx != 0:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON extraction error: {e}")
        pass
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


def validate_inputs(pdf_file, job_description: str) -> Tuple[bool, str]:
    """Validate user inputs with comprehensive error checking"""
    try:
        # Debug: Print validation information
        print(f"Validating file: {pdf_file}")
        print(f"Supported file types: {SUPPORTED_FILE_TYPES}")
        
        # Check if PDF file is provided
        if pdf_file is None:
            print("File is None")
            return False, ERROR_MESSAGES["no_pdf"]

        # Check if file exists
        if not os.path.exists(pdf_file):
            print(f"File does not exist: {pdf_file}")
            return False, ERROR_MESSAGES["invalid_file"]

        # Check file size
        file_size = os.path.getsize(pdf_file)
        print(f"File size: {file_size}")
        if file_size > MAX_FILE_SIZE:
            return False, ERROR_MESSAGES["file_too_large"]

        # Check file extension
        file_ext = os.path.splitext(pdf_file)[1].lower()
        print(f"File extension: '{file_ext}'")
        print(f"Supported extensions: {SUPPORTED_FILE_TYPES}")
        if file_ext not in SUPPORTED_FILE_TYPES:
            print(f"Extension '{file_ext}' not in supported types")
            return False, ERROR_MESSAGES["invalid_file"]

        # Check job description
        if not job_description or not job_description.strip():
            return False, ERROR_MESSAGES["no_job_desc"]

        # Check if job description is too short
        if len(job_description.strip()) < 10:
            return (
                False,
                "Please provide a more detailed job description (at least 10 characters).",
            )

        return True, ""

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def retry_with_backoff(func, *args, **kwargs):
    """Retry function with exponential backoff"""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            time.sleep(RETRY_DELAY * (2**attempt))
    return None


def handle_api_error(error: Exception) -> str:
    """Handle different types of API errors and return appropriate messages"""
    error_str = str(error).lower()

    if "rate limit" in error_str or "429" in error_str:
        return ERROR_MESSAGES["rate_limit_error"]
    elif "timeout" in error_str or "timed out" in error_str or "timedout" in error_str:
        return ERROR_MESSAGES["timeout_error"]
    elif "network" in error_str or "connection" in error_str:
        return ERROR_MESSAGES["network_error"]
    elif "server" in error_str or "500" in error_str:
        return ERROR_MESSAGES["server_error"]
    elif "api key" in error_str or "authentication" in error_str:
        return ERROR_MESSAGES["api_key_missing"]
    else:
        return ERROR_MESSAGES["unknown_error"]


def validate_file_content(file_path: str) -> Tuple[bool, str]:
    """Validate file content and structure"""
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Check if file is readable
        with open(file_path, "rb") as f:
            # Read first few bytes to check if it's a valid PDF
            header = f.read(4)
            if header != b"%PDF":
                return False, "Invalid PDF file format"

        return True, ""

    except Exception as e:
        return False, f"File validation error: {str(e)}"


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", "script", "javascript"]
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized.strip()
