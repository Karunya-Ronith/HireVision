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
    create_error_analysis,
    retry_with_backoff,
    handle_api_error,
    sanitize_input,
    extract_json_from_text,
)
from logging_config import get_logger, log_function_call, log_api_call, log_performance

# Initialize logger
logger = get_logger(__name__)


@log_function_call
def analyze_learning_path(current_skills, dream_role):
    """Analyze current skills against dream role and provide detailed learning path with enhanced error handling"""
    start_time = time.time()
    logger.info("Starting learning path analysis")
    logger.debug(f"Current skills length: {len(current_skills) if current_skills else 0}")
    logger.debug(f"Dream role length: {len(dream_role) if dream_role else 0}")
    
    if not current_skills or not dream_role:
        logger.warning("Missing current skills or dream role")
        return "Please provide both your current skills and dream role."

    # Sanitize inputs
    logger.debug("Sanitizing inputs")
    current_skills = sanitize_input(current_skills)
    dream_role = sanitize_input(dream_role)
    logger.debug(f"Sanitized current skills length: {len(current_skills)}")
    logger.debug(f"Sanitized dream role length: {len(dream_role)}")

    # Check if OpenRouter API key is available
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        logger.warning("OpenRouter API key not configured, returning error message")
        return "## ❌ Configuration Error\n\nOpenRouter API key not configured. Please configure your API key to use the learning path generator."

    def make_api_call():
        """Make the actual API call with retry logic"""
        logger.info("Making OpenRouter API call for learning path analysis")
        
        # Create a focused, structured prompt for better results
        prompt = f"""
You are an expert career coach and learning path specialist. Analyze the user's current skills against their dream role and provide a comprehensive, actionable learning path.

**Current Skills:**
{current_skills}

**Dream Role:**
{dream_role}

**Instructions:**
1. Analyze the gap between current skills and dream role requirements
2. Create a realistic, phased learning path
3. Recommend only verified, accessible resources
4. Provide specific, actionable advice
5. Return ONLY valid JSON in the exact format specified below

**Required JSON Response Format:**
{{
    "role_analysis": "Detailed analysis of the dream role, its requirements, and how it differs from current skills. Include specific responsibilities, technologies, and skills needed.",
    "skills_gap": [
        "Specific skill 1 that needs development",
        "Specific skill 2 that needs development",
        "Specific skill 3 that needs development"
    ],
    "learning_path": [
        {{
            "phase": "Phase 1: Foundation (2-3 months)",
            "duration": "2-3 months",
            "description": "Detailed description of what this phase covers and why it's important",
            "skills_to_learn": [
                "Specific skill to learn in this phase",
                "Another specific skill"
            ],
            "resources": [
                {{
                    "type": "course",
                    "name": "Course name (only if you know it exists)",
                    "url": "URL (only if verified)",
                    "description": "Why this resource is recommended",
                    "difficulty": "beginner/intermediate/advanced",
                    "verified": true/false
                }}
            ],
            "projects": [
                {{
                    "name": "Project name",
                    "description": "What this project should accomplish",
                    "skills_practiced": ["skill1", "skill2"],
                    "github_template": "URL if available, otherwise null"
                }}
            ]
        }}
    ],
    "timeline": "Overall timeline summary (e.g., '6-9 months total')",
    "success_metrics": [
        "Specific, measurable metric 1",
        "Specific, measurable metric 2",
        "Specific, measurable metric 3"
    ],
    "career_advice": "Detailed career advice specific to this transition, including strategies, tips, and actionable steps",
    "networking_tips": [
        "Specific networking tip 1",
        "Specific networking tip 2",
        "Specific networking tip 3"
    ]
}}

**Important Guidelines:**
- Only include resources you are confident exist and are accessible
- Be specific about skills, technologies, and requirements
- Provide realistic timelines and expectations
- Focus on actionable, measurable advice
- If unsure about a resource, set verified: false or omit it
- Return ONLY the JSON object, no additional text or markdown
- Ensure all JSON is properly formatted with correct quotes and brackets
- Keep descriptions concise but informative
- Use realistic timeframes (2-4 months per phase)
- Include 2-4 skills per phase
- Provide 1-2 resources per phase
- Include 1 hands-on project per phase
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
                        "content": "You are an expert career coach and learning path specialist. Provide detailed, actionable learning paths with verified resources only. Return only valid JSON in the exact format requested. Never hallucinate or invent fake links.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=OPENROUTER_TEMPERATURE,
                max_tokens=OPENROUTER_MAX_TOKENS,
            )
            
            api_duration = time.time() - api_start_time
            logger.info(f"OpenRouter API call successful in {api_duration:.3f}s")
            log_api_call("OpenRouter Learning Path Analysis", 
                        request_data={"model": OPENROUTER_MODEL, "temperature": OPENROUTER_TEMPERATURE, "max_tokens": OPENROUTER_MAX_TOKENS},
                        response_data={"response_length": len(response.choices[0].message.content)},
                        success=True)
            
            return response.choices[0].message.content
            
        except Exception as e:
            api_duration = time.time() - api_start_time
            logger.error(f"OpenRouter API call failed after {api_duration:.3f}s: {str(e)}")
            log_api_call("OpenRouter Learning Path Analysis", 
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
        analysis = extract_json_from_text(analysis_text)
        if analysis is None:
            logger.warning("No valid JSON found in response, creating error response")
            return create_error_analysis(
                "Failed to parse structured response from AI service. Please try again."
            )
        
        logger.info("Successfully extracted JSON from response")
        
        # Validate the extracted data
        if not _validate_extracted_data(analysis):
            logger.warning("Extracted data failed validation")
            return create_error_analysis(
                "Received invalid data structure from AI service. Please try again."
            )

        duration = time.time() - start_time
        log_performance("Learning path analysis", duration, f"Analysis completed with {len(analysis_text)} characters")
        
        return analysis

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Learning path analysis failed after {duration:.3f}s: {str(e)}", exc_info=True)
        error_message = handle_api_error(e)
        return create_error_analysis(error_message)


def _validate_extracted_data(data: dict) -> bool:
    """
    Validate the extracted JSON data has the required structure and content
    """
    if not isinstance(data, dict):
        logger.warning("Extracted data is not a dictionary")
        return False
    
    # Check required fields
    required_fields = ['role_analysis', 'skills_gap', 'learning_path']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Validate role_analysis
    role_analysis = data.get('role_analysis', '')
    if not role_analysis or len(str(role_analysis).strip()) < 50:
        logger.warning("Role analysis is too short or empty")
        return False
    
    # Validate skills_gap
    skills_gap = data.get('skills_gap', [])
    if not isinstance(skills_gap, list) or len(skills_gap) == 0:
        logger.warning("Skills gap must be a non-empty list")
        return False
    
    # Validate learning_path
    learning_path = data.get('learning_path', [])
    if not isinstance(learning_path, list) or len(learning_path) == 0:
        logger.warning("Learning path must be a non-empty list")
        return False
    
    # Validate each phase in learning_path
    for i, phase in enumerate(learning_path):
        if not isinstance(phase, dict):
            logger.warning(f"Phase {i} is not a dictionary")
            return False
        
        required_phase_fields = ['phase', 'description', 'skills_to_learn']
        for field in required_phase_fields:
            if field not in phase:
                logger.warning(f"Phase {i} missing required field: {field}")
                return False
    
    logger.info("Extracted data validation passed")
    return True


def format_learning_path_output(analysis):
    """Format the learning path analysis into a readable markdown output with resource verification"""
    if not isinstance(analysis, dict):
        return str(analysis)

    output = f"""
## 🎯 Dream Role Analysis

{analysis.get('role_analysis', 'No analysis available')}

## 🔍 Skills Gap Analysis

"""

    for skill in analysis.get("skills_gap", []):
        output += f"• {skill}\n"

    output += "\n## 📚 Detailed Learning Path\n"

    for phase in analysis.get("learning_path", []):
        output += f"""
### {phase.get('phase', 'Phase')} ({phase.get('duration', 'Duration TBD')})

{phase.get('description', 'No description available')}

**Skills to Learn:**
"""
        for skill in phase.get("skills_to_learn", []):
            output += f"• {skill}\n"

        output += "\n**📖 Learning Resources:**\n"
        for resource in phase.get("resources", []):
            resource_type = resource.get("type", "Resource")
            resource_name = resource.get("name", "Name")
            resource_url = resource.get("url", "#")
            resource_desc = resource.get("description", "No description")
            resource_diff = resource.get("difficulty", "Not specified")
            is_verified = resource.get("verified", False)

            if is_verified and resource_url and resource_url != "#":
                output += f"""
**{resource_type}**: [{resource_name}]({resource_url})
- **Difficulty**: {resource_diff}
- **Why this resource**: {resource_desc}
- **✅ Verified Resource**
"""
            else:
                output += f"""
**{resource_type}**: {resource_name}
- **Difficulty**: {resource_diff}
- **Why this resource**: {resource_desc}
- **⚠️ Resource not verified - please research before using**
"""

        output += "\n**🛠️ Hands-on Projects:**\n"
        for project in phase.get("projects", []):
            output += f"""
**{project.get('name', 'Project Name')}**
- **Description**: {project.get('description', 'No description')}
- **Skills practiced**: {', '.join(project.get('skills_practiced', []))}
"""
            if project.get("github_template"):
                output += f"- **Template**: [GitHub Repository]({project.get('github_template')})\n"

        output += "\n---\n"

    output += f"""
## ⏱️ Overall Timeline

{analysis.get('timeline', 'Timeline not available')}

## 📊 Success Metrics

"""
    for metric in analysis.get("success_metrics", []):
        output += f"• {metric}\n"

    output += f"""
## 💼 Career Advice

{analysis.get('career_advice', 'No career advice available')}

## 🤝 Networking Tips

"""
    for tip in analysis.get("networking_tips", []):
        output += f"• {tip}\n"

    return output


@log_function_call
def process_learning_path_analysis(current_skills, dream_role):
    """Main function to process learning path analysis with comprehensive error handling"""
    start_time = time.time()
    logger.info("Starting learning path analysis process")
    logger.debug(f"Current skills length: {len(current_skills) if current_skills else 0}")
    logger.debug(f"Dream role length: {len(dream_role) if dream_role else 0}")
    
    try:
        if not current_skills or not dream_role:
            logger.warning("Missing current skills or dream role")
            return "## ❌ Input Error\n\nPlease provide both your current skills and dream role."

        # Check if inputs are meaningful
        skills_length = len(current_skills.strip())
        role_length = len(dream_role.strip())
        logger.debug(f"Skills length: {skills_length}, Role length: {role_length}")
        
        if skills_length < 10:
            logger.warning(f"Skills information too short: {skills_length} characters")
            return "## ❌ Insufficient Skills Information\n\nPlease provide more detailed information about your current skills and experience."

        if role_length < 10:
            logger.warning(f"Role information too short: {role_length} characters")
            return "## ❌ Insufficient Role Information\n\nPlease provide more detailed information about your dream role."

        # Analyze learning path
        logger.info("Starting learning path analysis")
        analysis = analyze_learning_path(current_skills, dream_role)

        # Return structured data directly (no markdown formatting)
        logger.info("Returning structured learning path data")
        
        duration = time.time() - start_time
        logger.info(f"Learning path analysis process completed successfully in {duration:.3f}s")
        log_performance("Complete learning path analysis process", duration, f"Processed {skills_length} characters of skills and {role_length} characters of role")
        
        return analysis

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Learning path analysis process failed after {duration:.3f}s: {str(e)}", exc_info=True)
        error_message = handle_api_error(e)
        return f"## ❌ Unexpected Error\n\n{error_message}\n\nPlease try again or contact support if the issue persists."
