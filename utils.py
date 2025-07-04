import json
import re
from typing import Dict, Any, Optional

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
    
    for strength in analysis.get('strengths', []):
        output += f"• {strength}\n"
    
    output += "\n### ❌ Areas for Improvement\n"
    for weakness in analysis.get('weaknesses', []):
        output += f"• {weakness}\n"
    
    output += "\n### 💡 Recommendations\n"
    for rec in analysis.get('recommendations', []):
        output += f"• {rec}\n"
    
    output += "\n### 🔍 Skills Gap Analysis\n"
    for skill in analysis.get('skills_gap', []):
        output += f"• {skill}\n"
    
    output += "\n### 🚀 Upskilling Suggestions\n"
    for suggestion in analysis.get('upskilling_suggestions', []):
        output += f"• {suggestion}\n"
    
    output += f"\n### 📋 Overall Assessment\n{analysis.get('overall_assessment', 'No assessment available')}"
    
    return output

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text response"""
    try:
        # Find JSON in the response
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
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
        "overall_assessment": analysis_text
    }

def create_error_analysis(error_message: str) -> Dict[str, Any]:
    """Create an error analysis structure"""
    return {
        "ats_score": "Error",
        "score_explanation": f"Error during analysis: {error_message}",
        "strengths": [],
        "weaknesses": [],
        "recommendations": [],
        "skills_gap": [],
        "upskilling_suggestions": [],
        "overall_assessment": f"Error occurred: {error_message}"
    }

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)\[\]\{\}]', '', text)
    
    return text.strip()

def validate_inputs(pdf_file, job_description: str) -> tuple[bool, str]:
    """Validate user inputs"""
    if pdf_file is None:
        return False, "Please upload a PDF file."
    
    if not job_description or not job_description.strip():
        return False, "Please provide a job description."
    
    return True, "" 