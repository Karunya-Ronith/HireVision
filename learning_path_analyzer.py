import os
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS, ERROR_MESSAGES
from utils import create_error_analysis

def analyze_learning_path(current_skills, dream_role):
    """Analyze current skills against dream role and provide detailed learning path"""
    if not current_skills or not dream_role:
        return "Please provide both your current skills and dream role."
    
    # Check if OpenAI API key is available
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        return """
## ⚠️ OpenAI API Key Not Configured

To get AI-powered learning path guidance, please:

1. Get your OpenAI API key from: https://platform.openai.com/api-keys
2. Create a `.env` file in the project directory
3. Add your API key: `OPENAI_API_KEY=your_actual_api_key_here`
4. Restart the application
"""
    
    try:
        # Create the analysis prompt
        prompt = f"""
        You are an expert career coach and learning path specialist. 
        
        Please analyze the user's current skills against their dream role and provide a comprehensive, detailed learning path.
        
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
                            "url": "<resource_url>",
                            "description": "<why_this_resource>",
                            "difficulty": "<beginner/intermediate/advanced>"
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
                            "url": "<resource_url>",
                            "description": "<why_this_resource>",
                            "difficulty": "<beginner/intermediate/advanced>"
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
                            "url": "<resource_url>",
                            "description": "<why_this_resource>",
                            "difficulty": "<beginner/intermediate/advanced>"
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
        
        Make the learning path very detailed and practical. Include:
        - Specific courses, books, and online resources with URLs
        - Hands-on projects for each phase
        - Realistic timelines
        - Success metrics to track progress
        - Networking and career advice
        - Industry-specific recommendations
        """
        
        # Call OpenAI API
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert career coach and learning path specialist. Provide detailed, actionable learning paths with specific resources and timelines."},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        # Parse the response
        analysis_text = response.choices[0].message.content
        
        # Try to extract JSON from the response
        from utils import extract_json_from_text
        analysis = extract_json_from_text(analysis_text)
        if analysis is None:
            # If no JSON found, create a structured response
            analysis = {
                "role_analysis": analysis_text,
                "skills_gap": ["Analysis completed"],
                "learning_path": [],
                "timeline": "See detailed analysis above",
                "success_metrics": ["Review the analysis"],
                "career_advice": analysis_text,
                "networking_tips": ["Refer to the analysis"]
            }
        
        return analysis
        
    except Exception as e:
        return create_error_analysis(str(e))

def format_learning_path_output(analysis):
    """Format the learning path analysis into a readable markdown output"""
    if not isinstance(analysis, dict):
        return str(analysis)
    
    output = f"""
## 🎯 Dream Role Analysis

{analysis.get('role_analysis', 'No analysis available')}

## 🔍 Skills Gap Analysis

"""
    
    for skill in analysis.get('skills_gap', []):
        output += f"• {skill}\n"
    
    output += "\n## 📚 Detailed Learning Path\n"
    
    for phase in analysis.get('learning_path', []):
        output += f"""
### {phase.get('phase', 'Phase')} ({phase.get('duration', 'Duration TBD')})

{phase.get('description', 'No description available')}

**Skills to Learn:**
"""
        for skill in phase.get('skills_to_learn', []):
            output += f"• {skill}\n"
        
        output += "\n**📖 Learning Resources:**\n"
        for resource in phase.get('resources', []):
            output += f"""
**{resource.get('type', 'Resource')}**: [{resource.get('name', 'Name')}]({resource.get('url', '#')})
- **Difficulty**: {resource.get('difficulty', 'Not specified')}
- **Why this resource**: {resource.get('description', 'No description')}
"""
        
        output += "\n**🛠️ Hands-on Projects:**\n"
        for project in phase.get('projects', []):
            output += f"""
**{project.get('name', 'Project Name')}**
- **Description**: {project.get('description', 'No description')}
- **Skills practiced**: {', '.join(project.get('skills_practiced', []))}
"""
            if project.get('github_template'):
                output += f"- **Template**: [GitHub Repository]({project.get('github_template')})\n"
        
        output += "\n---\n"
    
    output += f"""
## ⏱️ Overall Timeline

{analysis.get('timeline', 'Timeline not available')}

## 📊 Success Metrics

"""
    for metric in analysis.get('success_metrics', []):
        output += f"• {metric}\n"
    
    output += f"""
## 💼 Career Advice

{analysis.get('career_advice', 'No career advice available')}

## 🤝 Networking Tips

"""
    for tip in analysis.get('networking_tips', []):
        output += f"• {tip}\n"
    
    return output

def process_learning_path_analysis(current_skills, dream_role):
    """Main function to process learning path analysis"""
    if not current_skills or not dream_role:
        return "Please provide both your current skills and dream role."
    
    # Analyze learning path
    analysis = analyze_learning_path(current_skills, dream_role)
    
    # Format the output
    return format_learning_path_output(analysis) 