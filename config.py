import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-nano"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 2000

# Application Configuration
APP_TITLE = "Resume ATS Analyzer & Career Coach"
DEMO_TITLE = "Resume ATS Analyzer - Demo"
THEME = "soft"

# File Configuration
SUPPORTED_FILE_TYPES = [".pdf", "docx", ".doc", ".tex", ".txt"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# UI Configuration
DEFAULT_PLACEHOLDER = "Paste the job description here..."
DEFAULT_LINES = 10
MAX_LINES = 20

# Analysis Configuration
ATS_SCORE_RANGES = {
    "excellent": (85, 100),
    "good": (65, 84),
    "fair": (45, 64),
    "poor": (0, 44)
}

# Error Messages
ERROR_MESSAGES = {
    "no_pdf": "Please upload a PDF file.",
    "no_job_desc": "Please provide both resume text and job description.",
    "api_key_missing": "OpenAI API key not configured. Please check your .env file.",
    "pdf_extraction_error": "Error extracting text from PDF: {}",
    "api_error": "Error connecting to OpenAI API: {}",
    "invalid_file": "Invalid file format. Please upload a PDF file.",
    "file_too_large": "File size too large. Please upload a file smaller than 10MB.",
    "network_error": "Network error. Please check your internet connection and try again.",
    "rate_limit_error": "Rate limit exceeded. Please wait a moment and try again.",
    "server_error": "Server error. Please try again later.",
    "timeout_error": "Request timed out. Please try again.",
    "unknown_error": "An unexpected error occurred. Please try again."
}

# Success Messages
SUCCESS_MESSAGES = {
    "analysis_complete": "Analysis completed successfully!",
    "demo_mode": "Demo mode - showing interface functionality"
}

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds 