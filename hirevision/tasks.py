import os
import django
import dramatiq
import json
import time
from typing import Dict, Any

# Setup Django before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hirevision_django.settings')
django.setup()

from django.core.files.base import ContentFile
from .models import ResumeAnalysis, LearningPath, ResumeBuilder
from resume_analyzer import process_resume_analysis
from learning_path_analyzer import process_learning_path_analysis
from resume_builder import process_resume_builder
from pdf_generator import generate_pdf_from_latex, get_sample_pdf_path

# Import logging
from logging_config import get_logger, log_performance

# Initialize logger
logger = get_logger(__name__)


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=30000)
def process_resume_analysis_task(analysis_id: str):
    """
    Async task to process resume analysis
    """
    start_time = time.time()
    logger.info(f"Starting resume analysis task for analysis ID: {analysis_id}")
    
    try:
        analysis = ResumeAnalysis.objects.get(id=analysis_id)
        logger.info(f"Found analysis record: {analysis_id}, user: {analysis.user.id if analysis.user else 'None'}")
        
        analysis.task_status = 'running'
        analysis.save(update_fields=['task_status'])
        logger.debug(f"Updated task status to 'running' for analysis: {analysis_id}")
        
        # Process the resume analysis
        logger.info(f"Processing resume analysis for file: {analysis.resume_file.path}")
        result = process_resume_analysis(
            analysis.resume_file.path,
            analysis.job_description
        )
        
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result content: {str(result)[:500]}...")
        
        # Check if the result is an error message
        if isinstance(result, str) and result.startswith('## ❌'):
            logger.error(f"Resume analysis failed for analysis {analysis_id}: {result}")
            analysis.task_status = 'failed'
            analysis.task_error = result
            analysis.save(update_fields=['task_status', 'task_error'])
            return
        
        # Check if it's the OpenRouter API key error - provide demo data
        if isinstance(result, str) and ("OpenRouter API Key Not Configured" in result or "API key not configured" in result.lower()):
            logger.info(f"Using demo data for analysis {analysis_id} (OpenRouter API key not configured)")
            # Demo data
            analysis.ats_score = 78
            analysis.score_explanation = "Demo analysis: Your resume shows good technical skills and relevant experience. The ATS score indicates a strong match for the position."
            analysis.strengths = [
                "Strong technical background in software development",
                "Relevant project experience",
                "Good educational qualifications",
                "Demonstrated problem-solving skills"
            ]
            analysis.weaknesses = [
                "Could include more quantifiable achievements",
                "Consider adding more industry-specific keywords",
                "Experience section could be more detailed"
            ]
            analysis.recommendations = [
                "Add specific metrics and numbers to achievements",
                "Include more relevant keywords from the job description",
                "Expand on technical skills and tools used"
            ]
            analysis.skills_gap = [
                "Advanced cloud computing (AWS/Azure)",
                "Microservices architecture",
                "DevOps practices"
            ]
            analysis.upskilling_suggestions = [
                "Take AWS or Azure certification courses",
                "Learn about microservices and containerization",
                "Study DevOps tools and practices"
            ]
            analysis.overall_assessment = "Demo assessment: You have a solid foundation and good potential for this role. Focus on highlighting quantifiable achievements and adding relevant technical skills to improve your ATS score."
        else:
            # Parse the result if it's structured
            if isinstance(result, dict):
                logger.info(f"Processing structured result for analysis {analysis_id}")
                # Ensure ats_score is an integer
                ats_score = result.get('ats_score', 75)
                if isinstance(ats_score, str):
                    try:
                        ats_score = int(ats_score)
                    except (ValueError, TypeError):
                        ats_score = 75
                
                analysis.ats_score = ats_score
                analysis.score_explanation = result.get('score_explanation', 'Analysis completed successfully')
                analysis.strengths = result.get('strengths', [])
                analysis.weaknesses = result.get('weaknesses', [])
                analysis.recommendations = result.get('recommendations', [])
                analysis.skills_gap = result.get('skills_gap', [])
                analysis.upskilling_suggestions = result.get('upskilling_suggestions', [])
                analysis.overall_assessment = result.get('overall_assessment', 'Analysis completed successfully')
                
                logger.info(f"Saved analysis data: score={analysis.ats_score}, strengths={len(analysis.strengths)}, weaknesses={len(analysis.weaknesses)}")
            else:
                logger.info(f"Processing fallback result for analysis {analysis_id}")
                # Fallback for markdown string result
                analysis.overall_assessment = result[:500] + "..." if len(result) > 500 else result
                analysis.ats_score = 75
                analysis.score_explanation = "Analysis completed successfully"
                analysis.strengths = ["Strong technical skills", "Good experience"]
                analysis.weaknesses = ["Could improve communication skills"]
                analysis.recommendations = ["Add more quantifiable achievements"]
                analysis.skills_gap = ["Advanced Python", "Cloud computing"]
                analysis.upskilling_suggestions = ["Take advanced Python course"]
        
        analysis.task_status = 'completed'
        analysis.save()
        logger.info(f"Resume analysis task completed successfully for analysis {analysis_id}")
        
        duration = time.time() - start_time
        log_performance("Resume analysis task", duration, f"Completed analysis {analysis_id} with score {analysis.ats_score}")
        
    except ResumeAnalysis.DoesNotExist:
        logger.error(f"ResumeAnalysis with id {analysis_id} not found")
    except Exception as e:
        logger.error(f"Error processing resume analysis task for {analysis_id}: {str(e)}", exc_info=True)
        try:
            analysis = ResumeAnalysis.objects.get(id=analysis_id)
            analysis.task_status = 'failed'
            analysis.task_error = str(e)
            analysis.save(update_fields=['task_status', 'task_error'])
            logger.info(f"Updated analysis {analysis_id} status to 'failed'")
        except Exception as save_error:
            logger.error(f"Failed to update analysis {analysis_id} status: {str(save_error)}")


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=30000)
def process_learning_path_task(path_id: str):
    """
    Async task to process learning path analysis with proper error handling and validation
    """
    start_time = time.time()
    logger.info(f"Starting learning path task for path ID: {path_id}")
    
    try:
        # Get the learning path record
        learning_path = LearningPath.objects.get(id=path_id)
        logger.info(f"Found learning path record: {path_id}, user: {learning_path.user.id if learning_path.user else 'None'}")
        
        # Update status to running
        learning_path.task_status = 'running'
        learning_path.save(update_fields=['task_status'])
        logger.debug(f"Updated task status to 'running' for learning path: {path_id}")
        
        # Validate inputs before processing
        if not learning_path.current_skills or not learning_path.dream_role:
            error_msg = "Missing current skills or dream role information"
            logger.error(f"Validation failed for learning path {path_id}: {error_msg}")
            learning_path.task_status = 'failed'
            learning_path.task_error = f"## ❌ Input Validation Error\n\n{error_msg}"
            learning_path.save(update_fields=['task_status', 'task_error'])
            return
        
        # Process the learning path analysis
        logger.info(f"Processing learning path analysis for skills: {len(learning_path.current_skills)} chars, role: {len(learning_path.dream_role)} chars")
        result = process_learning_path_analysis(
            learning_path.current_skills,
            learning_path.dream_role
        )
        
        logger.info(f"Learning path analysis result type: {type(result)}")
        logger.debug(f"Result preview: {str(result)[:200]}...")
        
        # Handle different result types with proper validation
        if isinstance(result, str):
            # Check for error messages
            if result.startswith('## ❌'):
                logger.error(f"Learning path analysis failed for {path_id}: {result}")
                learning_path.task_status = 'failed'
                learning_path.task_error = result
                learning_path.save(update_fields=['task_status', 'task_error'])
                return
            
            # Check for API key configuration error
            if "OpenRouter API Key Not Configured" in result:
                error_msg = """
## ❌ Configuration Error

The OpenRouter API key is not properly configured. To use the AI-powered learning path generator:

1. Get your OpenRouter API key from: https://openrouter.ai/keys
2. Create a `.env` file in the project directory
3. Add your API key: `OPENROUTER_API_KEY=your_actual_api_key_here`
4. Restart the application

Without the API key, the system cannot generate personalized learning paths.
"""
                logger.warning(f"API key not configured for learning path {path_id}")
                learning_path.task_status = 'failed'
                learning_path.task_error = error_msg
                learning_path.save(update_fields=['task_status', 'task_error'])
                return
            
            # If it's a successful string result, parse it for structured data
            logger.info(f"Processing string result for learning path {path_id}")
            # Try to extract structured data from the markdown result
            structured_data = _parse_markdown_to_structured_data(result)
            if structured_data:
                _update_learning_path_with_data(learning_path, structured_data)
            else:
                # Fallback: store the raw result
                learning_path.career_advice = result
                learning_path.role_analysis = "Analysis completed - see career advice below"
                learning_path.skills_gap = ["Review the detailed analysis above"]
                learning_path.learning_path_data = []
                learning_path.timeline = "See detailed analysis"
                learning_path.success_metrics = ["Complete the recommended learning path"]
                learning_path.networking_tips = ["Follow the career advice provided"]
        
        elif isinstance(result, dict):
            # Validate the structured result
            logger.info(f"Processing structured result for learning path {path_id}")
            if _validate_learning_path_data(result):
                _update_learning_path_with_data(learning_path, result)
            else:
                error_msg = "## ❌ Data Validation Error\n\nReceived invalid data structure from the analysis service."
                logger.error(f"Invalid data structure for learning path {path_id}")
                learning_path.task_status = 'failed'
                learning_path.task_error = error_msg
                learning_path.save(update_fields=['task_status', 'task_error'])
                return
        else:
            # Unknown result type
            error_msg = f"## ❌ Unexpected Result Type\n\nReceived unexpected result type: {type(result)}"
            logger.error(f"Unexpected result type for learning path {path_id}: {type(result)}")
            learning_path.task_status = 'failed'
            learning_path.task_error = error_msg
            learning_path.save(update_fields=['task_status', 'task_error'])
            return
        
        # Mark as completed
        learning_path.task_status = 'completed'
        learning_path.save()
        logger.info(f"Learning path task completed successfully for {path_id}")
        
        duration = time.time() - start_time
        log_performance("Learning path task", duration, f"Completed learning path {path_id}")
        
    except LearningPath.DoesNotExist:
        logger.error(f"LearningPath with id {path_id} not found")
    except Exception as e:
        logger.error(f"Error processing learning path task for {path_id}: {str(e)}", exc_info=True)
        try:
            learning_path = LearningPath.objects.get(id=path_id)
            learning_path.task_status = 'failed'
            learning_path.task_error = f"## ❌ Processing Error\n\nAn unexpected error occurred: {str(e)}"
            learning_path.save(update_fields=['task_status', 'task_error'])
            logger.info(f"Updated learning path {path_id} status to 'failed'")
        except Exception as save_error:
            logger.error(f"Failed to update learning path {path_id} status: {str(save_error)}")


def _validate_learning_path_data(data: dict) -> bool:
    """
    Validate the structure and content of learning path data
    """
    if not isinstance(data, dict):
        return False
    
    # Check for required fields
    required_fields = ['role_analysis', 'skills_gap', 'learning_path']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field in learning path data: {field}")
            return False
    
    # Validate role_analysis
    if not data.get('role_analysis') or len(str(data['role_analysis']).strip()) < 10:
        logger.warning("Role analysis is too short or empty")
        return False
    
    # Validate skills_gap
    if not isinstance(data.get('skills_gap'), list) or len(data['skills_gap']) == 0:
        logger.warning("Skills gap must be a non-empty list")
        return False
    
    # Validate learning_path
    if not isinstance(data.get('learning_path'), list):
        logger.warning("Learning path must be a list")
        return False
    
    return True


def _update_learning_path_with_data(learning_path: LearningPath, data: dict):
    """
    Update learning path record with validated data
    """
    logger.info("Updating learning path with validated data")
    
    # Update core fields
    learning_path.role_analysis = data.get('role_analysis', 'Role analysis completed')
    learning_path.skills_gap = data.get('skills_gap', [])
    learning_path.learning_path_data = data.get('learning_path', [])
    learning_path.timeline = data.get('timeline', 'Timeline to be determined')
    learning_path.success_metrics = data.get('success_metrics', [])
    learning_path.career_advice = data.get('career_advice', 'Career advice available in the detailed analysis')
    learning_path.networking_tips = data.get('networking_tips', [])
    
    logger.info(f"Updated learning path with: {len(learning_path.skills_gap)} skills gaps, {len(learning_path.learning_path_data)} learning phases")


def _parse_markdown_to_structured_data(markdown_text: str) -> dict:
    """
    Parse markdown text to extract structured learning path data
    """
    try:
        # This is a simplified parser - in a production system, you'd use a proper markdown parser
        lines = markdown_text.split('\n')
        structured_data = {
            'role_analysis': '',
            'skills_gap': [],
            'learning_path': [],
            'timeline': '',
            'success_metrics': [],
            'career_advice': '',
            'networking_tips': []
        }
        
        current_section = None
        current_phase = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if line.startswith('## 🎯 Dream Role Analysis'):
                current_section = 'role_analysis'
                continue
            elif line.startswith('## 🔍 Skills Gap Analysis'):
                current_section = 'skills_gap'
                continue
            elif line.startswith('## 📚 Detailed Learning Path'):
                current_section = 'learning_path'
                continue
            elif line.startswith('## ⏱️ Overall Timeline'):
                current_section = 'timeline'
                continue
            elif line.startswith('## 📊 Success Metrics'):
                current_section = 'success_metrics'
                continue
            elif line.startswith('## 💼 Career Advice'):
                current_section = 'career_advice'
                continue
            elif line.startswith('## 🤝 Networking Tips'):
                current_section = 'networking_tips'
                continue
            
            # Process content based on current section
            if current_section == 'role_analysis' and line and not line.startswith('#'):
                structured_data['role_analysis'] += line + ' '
            elif current_section == 'skills_gap' and line.startswith('•'):
                skill = line[1:].strip()
                if skill:
                    structured_data['skills_gap'].append(skill)
            elif current_section == 'timeline' and line and not line.startswith('#'):
                structured_data['timeline'] = line
            elif current_section == 'success_metrics' and line.startswith('•'):
                metric = line[1:].strip()
                if metric:
                    structured_data['success_metrics'].append(metric)
            elif current_section == 'career_advice' and line and not line.startswith('#'):
                structured_data['career_advice'] += line + ' '
            elif current_section == 'networking_tips' and line.startswith('•'):
                tip = line[1:].strip()
                if tip:
                    structured_data['networking_tips'].append(tip)
        
        # Clean up text fields
        structured_data['role_analysis'] = structured_data['role_analysis'].strip()
        structured_data['career_advice'] = structured_data['career_advice'].strip()
        
        # Validate that we have meaningful data
        if (structured_data['role_analysis'] and 
            structured_data['skills_gap'] and 
            len(structured_data['role_analysis']) > 50):
            return structured_data
        
        return None
        
    except Exception as e:
        logger.error(f"Error parsing markdown to structured data: {str(e)}")
        return None


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=30000)
def process_resume_builder_task(resume_id: str):
    """
    Async task to process resume building
    """
    try:
        resume = ResumeBuilder.objects.get(id=resume_id)
        resume.task_status = 'running'
        resume.save(update_fields=['task_status'])
        
        # Convert form data to the format expected by the existing function
        name = resume.name
        email = resume.email
        phone = resume.phone
        linkedin = resume.linkedin
        github = resume.github
        
        # Convert JSON fields to strings for processing
        education = json.dumps(resume.education) if resume.education else ""
        experience = json.dumps(resume.experience) if resume.experience else ""
        projects = json.dumps(resume.projects) if resume.projects else ""
        skills = json.dumps(resume.skills) if resume.skills else ""
        research_papers = json.dumps(resume.research_papers) if resume.research_papers else ""
        achievements = json.dumps(resume.achievements) if resume.achievements else ""
        others = json.dumps(resume.others) if resume.others else ""
        
        # Process the resume builder
        result = process_resume_builder(
            name, email, phone, linkedin, github,
            education, experience, projects, skills,
            research_papers, achievements, others
        )
        
        # Check if the result is an error message
        if isinstance(result, str) and result.startswith('## ❌'):
            resume.task_status = 'failed'
            resume.task_error = result
            resume.save(update_fields=['task_status', 'task_error'])
            return
        
        # Check if it's the OpenRouter API key error - provide demo data
        if isinstance(result, str) and "OpenRouter API Key Not Configured" in result:
            # Demo data - save the resume with demo content
            resume.latex_content = "Demo LaTeX content for resume"
            
            # Create a demo PDF file
            demo_pdf_path = get_sample_pdf_path()
            if demo_pdf_path and os.path.exists(demo_pdf_path):
                with open(demo_pdf_path, 'rb') as pdf_file:
                    resume.pdf_file.save(f"demo_resume_{resume.id}.pdf", ContentFile(pdf_file.read()), save=False)
        else:
            # Process the result
            if isinstance(result, tuple) and len(result) == 2:
                latex_content, pdf_path = result
                resume.latex_content = latex_content
                
                # Save PDF if generated
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as pdf_file:
                        resume.pdf_file.save(f"resume_{resume.id}.pdf", ContentFile(pdf_file.read()), save=False)
                    # Clean up temporary file
                    try:
                        os.remove(pdf_path)
                    except:
                        pass
            else:
                # Fallback - assume it's LaTeX content
                resume.latex_content = str(result)
                
                # Try to generate PDF from LaTeX
                try:
                    pdf_path = generate_pdf_from_latex(str(result))
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, 'rb') as pdf_file:
                            resume.pdf_file.save(f"resume_{resume.id}.pdf", ContentFile(pdf_file.read()), save=False)
                        os.remove(pdf_path)
                except Exception as e:
                    print(f"PDF generation error: {e}")
        
        resume.task_status = 'completed'
        resume.save()
        
    except ResumeBuilder.DoesNotExist:
        print(f"ResumeBuilder with id {resume_id} not found")
    except Exception as e:
        try:
            resume = ResumeBuilder.objects.get(id=resume_id)
            resume.task_status = 'failed'
            resume.task_error = str(e)
            resume.save(update_fields=['task_status', 'task_error'])
        except:
            pass
        print(f"Error processing resume builder task: {e}") 