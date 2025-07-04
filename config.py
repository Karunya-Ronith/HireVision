import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 2000

# Application Configuration
APP_TITLE = "Resume ATS Analyzer & Career Coach"
DEMO_TITLE = "Resume ATS Analyzer - Demo"
THEME = "soft"

# File Configuration
SUPPORTED_FILE_TYPES = [".pdf"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# UI Configuration
DEFAULT_PLACEHOLDER = "Paste the job description here..."
DEFAULT_LINES = 10
MAX_LINES = 20

# Analysis Configuration
ATS_SCORE_RANGES = {
    "excellent": (90, 100),
    "good": (70, 89),
    "fair": (50, 69),
    "poor": (0, 49)
}

# Error Messages
ERROR_MESSAGES = {
    "no_pdf": "Please upload a PDF file.",
    "no_job_desc": "Please provide both resume text and job description.",
    "api_key_missing": "OpenAI API key not configured. Please check your .env file.",
    "pdf_extraction_error": "Error extracting text from PDF: {}"
}

# Success Messages
SUCCESS_MESSAGES = {
    "analysis_complete": "Analysis completed successfully!",
    "demo_mode": "Demo mode - showing interface functionality"
} 