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
        logger.warning("OpenRouter API key not configured, returning demo message")
        return """
## ⚠️ OpenRouter API Key Not Configured

To get AI-powered learning path guidance, please:

1. Get your OpenRouter API key from: https://openrouter.ai/keys
2. Create a `.env` file in the project directory
3. Add your API key: `OPENROUTER_API_KEY=your_actual_api_key_here`
4. Restart the application
"""

    def make_api_call():
        """Make the actual API call with retry logic"""
        logger.info("Making OpenRouter API call for learning path analysis")
        
        # Create the enhanced analysis prompt with anti-hallucination instructions
        prompt = f"""
        You are an expert career coach and learning path specialist with 15+ years of experience in career development.
        
        Please analyze the user's current skills against their dream role and provide a comprehensive, detailed learning path.
        
        **CRITICAL INSTRUCTIONS:**
        - DO NOT hallucinate or invent links to resources that don't exist
        - Only recommend resources (courses, books, websites) if you are confident they are real and accessible
        - If you cannot find a good, verified resource for a particular skill, simply state "No specific resource recommended" 
          rather than making up a fake link
        - Focus on well-known, established platforms like Coursera, edX, Udemy, LinkedIn Learning, etc.
        - For books, only recommend real, published books with actual authors and titles
        - Be honest about resource limitations - it's better to recommend fewer, verified resources than many fake ones
        
        Current Skills:
        {current_skills}
        
        Dream Role:
        {dream_role}
        
        Please provide a detailed learning path in the following JSON format:
        {{
            "role_analysis": "<analysis of the dream role and its requirements>",
            "skills_gap": ["<missing_skill1>", "<missing_skill2>", ...],
            "learning_path": [
                {{
                    "phase": "Phase 1: Foundation",
                    "duration": "<estimated_duration>",
                    "description": "<detailed_description>",
                    "skills_to_learn": ["<skill1>", "<skill2>", ...],
                    "resources": [
                        {{
                            "type": "<course/book/project/tool>",
                            "name": "<resource_name>",
                            "url": "<resource_url_or_placeholder>",
                            "description": "<why_this_resource>",
                            "difficulty": "<beginner/intermediate/advanced>",
                            "verified": "<true/false>"
                        }}
                    ],
                    "projects": [
                        {{
                            "name": "<project_name>",
                            "description": "<project_description>",
                            "skills_practiced": ["<skill1>", "<skill2>"],
                            "github_template": "<github_url_if_available>"
                        }}
                    ]
                }},
                {{
                    "phase": "Phase 2: Intermediate",
                    "duration": "<estimated_duration>",
                    "description": "<detailed_description>",
                    "skills_to_learn": ["<skill1>", "<skill2>", ...],
                    "resources": [
                        {{
                            "type": "<course/book/project/tool>",
                            "name": "<resource_name>",
                            "url": "<resource_url_or_placeholder>",
                            "description": "<why_this_resource>",
                            "difficulty": "<beginner/intermediate/advanced>",
                            "verified": "<true/false>"
                        }}
                    ],
                    "projects": [
                        {{
                            "name": "<project_name>",
                            "description": "<project_description>",
                            "skills_practiced": ["<skill1>", "<skill2>"],
                            "github_template": "<github_url_if_available>"
                        }}
                    ]
                }},
                {{
                    "phase": "Phase 3: Advanced",
                    "duration": "<estimated_duration>",
                    "description": "<detailed_description>",
                    "skills_to_learn": ["<skill1>", "<skill2>", ...],
                    "resources": [
                        {{
                            "type": "<course/book/project/tool>",
                            "name": "<resource_name>",
                            "url": "<resource_url_or_placeholder>",
                            "description": "<why_this_resource>",
                            "difficulty": "<beginner/intermediate/advanced>",
                            "verified": "<true/false>"
                        }}
                    ],
                    "projects": [
                        {{
                            "name": "<project_name>",
                            "description": "<project_description>",
                            "skills_practiced": ["<skill1>", "<skill2>"],
                            "github_template": "<github_url_if_available>"
                        }}
                    ]
                }}
            ],
            "timeline": "<overall_timeline_summary>",
            "success_metrics": ["<metric1>", "<metric2>", ...],
            "career_advice": "<additional_career_advice>",
            "networking_tips": ["<tip1>", "<tip2>", ...]
        }}
        
        **RESOURCE GUIDELINES:**
        - For courses: Only recommend from well-known platforms (Coursera, edX, Udemy, LinkedIn Learning, etc.)
        - For books: Only recommend real, published books with actual authors
        - For tools: Only recommend tools that actually exist and are accessible
        - For projects: Be specific about what the project should accomplish
        - If unsure about a resource, mark it as "verified": false or don't include it
        
        Make the learning path very detailed and practical. Include:
        - Specific courses, books, and online resources with URLs (only if verified)
        - Hands-on projects for each phase
        - Realistic timelines
        - Success metrics to track progress
        - Networking and career advice
        - Industry-specific recommendations
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
                        "content": "You are an expert career coach and learning path specialist. Provide detailed, actionable learning paths with verified resources only. Never hallucinate or invent fake links.",
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
            logger.warning("No JSON found in response, creating fallback analysis")
            # If no JSON found, create a structured response
            analysis = {
                "role_analysis": analysis_text,
                "skills_gap": ["Analysis completed"],
                "learning_path": [],
                "timeline": "See detailed analysis above",
                "success_metrics": ["Review the analysis"],
                "career_advice": analysis_text,
                "networking_tips": ["Refer to the analysis"],
            }
        else:
            logger.info("Successfully extracted JSON from response")

        duration = time.time() - start_time
        log_performance("Learning path analysis", duration, f"Analysis completed with {len(analysis_text)} characters")
        
        return analysis

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Learning path analysis failed after {duration:.3f}s: {str(e)}", exc_info=True)
        error_message = handle_api_error(e)
        return create_error_analysis(error_message)


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

        # Format the output
        logger.info("Formatting learning path output")
        formatted_output = format_learning_path_output(analysis)
        
        duration = time.time() - start_time
        logger.info(f"Learning path analysis process completed successfully in {duration:.3f}s")
        log_performance("Complete learning path analysis process", duration, f"Processed {skills_length} characters of skills and {role_length} characters of role")
        
        return formatted_output

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Learning path analysis process failed after {duration:.3f}s: {str(e)}", exc_info=True)
        error_message = handle_api_error(e)
        return f"## ❌ Unexpected Error\n\n{error_message}\n\nPlease try again or contact support if the issue persists."
