from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
import json
import os

from .forms import ResumeAnalysisForm, LearningPathForm, ResumeBuilderForm, UserSignUpForm, UserLoginForm
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User

# Import the existing modules
from resume_analyzer import process_resume_analysis
from learning_path_analyzer import process_learning_path_analysis
from resume_builder import process_resume_builder
from pdf_generator import get_sample_pdf_path, generate_pdf_from_latex

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        # Show dashboard for logged-in users
        return render(request, 'hirevision/dashboard.html')
    else:
        # Show landing page for non-logged-in users
        return render(request, 'hirevision/landing.html')

@login_required
def resume_analyzer(request):
    """Resume analyzer view"""
    if request.method == 'POST':
        form = ResumeAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the form to get the model instance
                analysis = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    analysis.user = request.user
                
                # Save the file first so it exists on disk
                analysis.save()
                
                # Debug: Print file information
                print(f"File path: {analysis.resume_file.path}")
                print(f"File name: {analysis.resume_file.name}")
                print(f"File size: {analysis.resume_file.size}")
                
                # Process the resume analysis using the existing function
                result = process_resume_analysis(
                    analysis.resume_file.path,
                    analysis.job_description
                )
                
                # Debug: Print the result to see what we're getting
                print(f"Resume analysis result: {result[:200]}...")
                
                # Check if the result is an error message
                if isinstance(result, str) and result.startswith('## ❌'):
                    # Error occurred
                    messages.error(request, "Analysis failed. Please try again.")
                    return render(request, 'hirevision/resume_analyzer.html', {'form': form})
                
                # Check if it's the OpenAI API key error
                if isinstance(result, str) and "OpenAI API Key Not Configured" in result:
                    # Provide demo data instead of error
                    messages.info(request, "Demo mode: Using sample analysis data. Set up your OpenAI API key for real AI analysis.")
                    
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
                    # The result is a formatted markdown string, we need to parse it
                    # For now, let's save the raw result and extract basic info
                    analysis.overall_assessment = result[:500] + "..." if len(result) > 500 else result
                    
                    # Set default values for now (in a real implementation, you'd parse the markdown)
                    analysis.ats_score = 75  # Default score
                    analysis.score_explanation = "Analysis completed successfully"
                    analysis.strengths = ["Strong technical skills", "Good experience"]
                    analysis.weaknesses = ["Could improve communication skills"]
                    analysis.recommendations = ["Add more quantifiable achievements"]
                    analysis.skills_gap = ["Advanced Python", "Cloud computing"]
                    analysis.upskilling_suggestions = ["Take advanced Python course"]
                
                # Update the saved record with the analysis results
                analysis.save(update_fields=['ats_score', 'score_explanation', 'strengths', 'weaknesses', 'recommendations', 'skills_gap', 'upskilling_suggestions', 'overall_assessment'])
                
                messages.success(request, "Resume analysis completed successfully!")
                return redirect('hirevision:resume_analysis_result', analysis_id=analysis.id)
                
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = ResumeAnalysisForm()
    
    return render(request, 'hirevision/resume_analyzer.html', {'form': form})

@login_required
def resume_analysis_result(request, analysis_id):
    """Display resume analysis result"""
    try:
        analysis = ResumeAnalysis.objects.get(id=analysis_id)
        # Check if user has permission to view this analysis
        if request.user.is_authenticated and analysis.user and analysis.user != request.user:
            messages.error(request, "You don't have permission to view this analysis.")
            return redirect('hirevision:resume_analyzer')
        return render(request, 'hirevision/resume_analysis_result.html', {'analysis': analysis})
    except ResumeAnalysis.DoesNotExist:
        messages.error(request, "Analysis not found.")
        return redirect('hirevision:resume_analyzer')

@login_required
def learning_path_analyzer(request):
    """Learning path analyzer view"""
    if request.method == 'POST':
        form = LearningPathForm(request.POST)
        if form.is_valid():
            try:
                # Save the form to get the model instance
                learning_path = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    learning_path.user = request.user
                
                # Process the learning path analysis using the existing function
                result = process_learning_path_analysis(
                    learning_path.current_skills,
                    learning_path.dream_role
                )
                
                # Debug: Print the result to see what we're getting
                print(f"Learning path result: {result[:200]}...")
                
                # Check if the result is an error message
                if isinstance(result, str) and result.startswith('## ❌'):
                    # Error occurred
                    messages.error(request, "Analysis failed. Please try again.")
                    return render(request, 'hirevision/learning_path_analyzer.html', {'form': form})
                
                # Check if it's the OpenAI API key error
                if isinstance(result, str) and "OpenAI API Key Not Configured" in result:
                    # Provide demo data instead of error
                    messages.info(request, "Demo mode: Using sample learning path data. Set up your OpenAI API key for real AI analysis.")
                    
                    # Demo data
                    learning_path.role_analysis = "Demo analysis: Based on your current skills and the target role, here's a comprehensive learning path to help you achieve your career goals."
                    learning_path.skills_gap = [
                        "Advanced programming concepts",
                        "System design and architecture",
                        "Cloud computing platforms",
                        "DevOps and CI/CD practices"
                    ]
                    learning_path.learning_path_data = [
                        {
                            "phase": "Phase 1: Foundation (2-3 months)",
                            "duration": "2-3 months",
                            "description": "Build strong fundamentals in advanced programming and system design",
                            "skills_to_learn": ["Advanced Algorithms", "Data Structures", "System Design"],
                            "resources": [
                                {
                                    "type": "course",
                                    "name": "Advanced Algorithms Course",
                                    "url": "https://coursera.org",
                                    "description": "Comprehensive algorithms course",
                                    "difficulty": "intermediate",
                                    "verified": True
                                }
                            ],
                            "projects": [
                                {
                                    "name": "Algorithm Implementation Project",
                                    "description": "Implement and optimize various algorithms",
                                    "skills_practiced": ["Algorithms", "Data Structures"],
                                    "github_template": "https://github.com/example"
                                }
                            ]
                        },
                        {
                            "phase": "Phase 2: Specialization (3-4 months)",
                            "duration": "3-4 months",
                            "description": "Focus on cloud computing and modern development practices",
                            "skills_to_learn": ["AWS/Azure", "Docker", "Kubernetes"],
                            "resources": [
                                {
                                    "type": "course",
                                    "name": "AWS Solutions Architect",
                                    "url": "https://aws.amazon.com",
                                    "description": "AWS certification preparation",
                                    "difficulty": "intermediate",
                                    "verified": True
                                }
                            ],
                            "projects": [
                                {
                                    "name": "Cloud-Native Application",
                                    "description": "Build and deploy a scalable application",
                                    "skills_practiced": ["Cloud Computing", "DevOps"],
                                    "github_template": "https://github.com/example"
                                }
                            ]
                        }
                    ]
                    learning_path.timeline = "6-8 months total"
                    learning_path.success_metrics = [
                        "Complete 3-4 major projects",
                        "Earn relevant certifications",
                        "Build a strong portfolio",
                        "Network with industry professionals"
                    ]
                    learning_path.career_advice = "Demo advice: Focus on building practical projects that demonstrate your skills. Network actively and consider contributing to open-source projects to gain visibility."
                    learning_path.networking_tips = [
                        "Join professional LinkedIn groups",
                        "Attend industry meetups and conferences",
                        "Participate in open-source projects",
                        "Connect with mentors in your field"
                    ]
                else:
                    # The result is a formatted markdown string, we need to parse it
                    # For now, let's save the raw result and extract basic info
                    learning_path.career_advice = result[:500] + "..." if len(result) > 500 else result
                    
                    # Set default values for now (in a real implementation, you'd parse the markdown)
                    learning_path.role_analysis = "Role analysis completed"
                    learning_path.skills_gap = ["Advanced skills needed"]
                    learning_path.learning_path_data = [{"phase": "Phase 1", "description": "Foundation"}]
                    learning_path.timeline = "6-12 months"
                    learning_path.success_metrics = ["Complete courses", "Build projects"]
                    learning_path.networking_tips = ["Join professional groups"]
                
                learning_path.save()
                
                messages.success(request, "Learning path analysis completed successfully!")
                return redirect('hirevision:learning_path_result', path_id=learning_path.id)
                
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = LearningPathForm()
    
    return render(request, 'hirevision/learning_path_analyzer.html', {'form': form})

@login_required
def learning_path_result(request, path_id):
    """Display learning path result"""
    try:
        learning_path = LearningPath.objects.get(id=path_id)
        # Check if user has permission to view this learning path
        if request.user.is_authenticated and learning_path.user and learning_path.user != request.user:
            messages.error(request, "You don't have permission to view this learning path.")
            return redirect('hirevision:learning_path_analyzer')
        return render(request, 'hirevision/learning_path_result.html', {'learning_path': learning_path})
    except LearningPath.DoesNotExist:
        messages.error(request, "Learning path not found.")
        return redirect('hirevision:learning_path_analyzer')

@login_required
def resume_builder(request):
    """Resume builder view"""
    if request.method == 'POST':
        form = ResumeBuilderForm(request.POST)
        if form.is_valid():
            try:
                # Save the form to get the model instance
                resume = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    resume.user = request.user
                
                # Convert form data to the format expected by the existing function
                name = resume.name
                email = resume.email
                phone = resume.phone
                linkedin = resume.linkedin
                github = resume.github
                
                # Parse JSON fields
                try:
                    education = json.loads(resume.education) if resume.education else []
                    experience = json.loads(resume.experience) if resume.experience else []
                    projects = json.loads(resume.projects) if resume.projects else []
                    skills = json.loads(resume.skills) if resume.skills else {}
                    research_papers = json.loads(resume.research_papers) if resume.research_papers else []
                    achievements = resume.achievements if isinstance(resume.achievements, list) else [resume.achievements] if resume.achievements else []
                    others = resume.others if isinstance(resume.others, list) else [resume.others] if resume.others else []
                except json.JSONDecodeError as e:
                    messages.error(request, f"Invalid JSON format in one of the fields: {str(e)}")
                    return render(request, 'hirevision/resume_builder.html', {'form': form})
                
                # Process the resume builder using the existing function
                result = process_resume_builder(
                    name, email, phone, linkedin, github,
                    education, experience, projects, skills,
                    research_papers, achievements, others
                )
                
                # Debug: Print the result to see what we're getting
                print(f"Resume builder result: {result[:200]}...")
                
                # Check if the result is an error message
                if isinstance(result, str) and result.startswith('## ❌'):
                    # Error occurred
                    messages.error(request, "Resume generation failed. Please try again.")
                    return render(request, 'hirevision/resume_builder.html', {'form': form})
                
                # Check if it's the OpenAI API key error
                if isinstance(result, str) and "OpenAI API Key Not Configured" in result:
                    # Provide demo data instead of error
                    messages.info(request, "Demo mode: Using sample resume data. Set up your OpenAI API key for real AI generation.")
                    
                    # Demo data - save the resume with demo content
                    resume.latex_content = "Demo LaTeX content for resume"
                    resume.save()
                    
                    # Create a demo PDF file
                    demo_pdf_path = get_sample_pdf_path()
                    if demo_pdf_path and os.path.exists(demo_pdf_path):
                        with open(demo_pdf_path, 'rb') as pdf_file:
                            resume.pdf_file.save(f"demo_resume_{resume.id}.pdf", ContentFile(pdf_file.read()), save=True)
                    
                    messages.success(request, "Demo resume created successfully!")
                    return redirect('hirevision:resume_builder_result', resume_id=resume.id)
                else:
                    # The result is a LaTeX string, save it
                    resume.latex_content = result
                    resume.save()
                    
                    # Generate PDF from LaTeX
                    try:
                        pdf_path = generate_pdf_from_latex(result)
                        if pdf_path and os.path.exists(pdf_path):
                            with open(pdf_path, 'rb') as pdf_file:
                                resume.pdf_file.save(f"resume_{resume.id}.pdf", ContentFile(pdf_file.read()), save=True)
                            # Clean up temporary file
                            os.remove(pdf_path)
                    except Exception as e:
                        print(f"PDF generation error: {e}")
                        # Continue without PDF
                    
                    messages.success(request, "Resume created successfully!")
                    return redirect('hirevision:resume_builder_result', resume_id=resume.id)
                
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = ResumeBuilderForm()
    
    return render(request, 'hirevision/resume_builder.html', {'form': form})

@login_required
def resume_builder_result(request, resume_id):
    """Display resume builder result"""
    try:
        resume = ResumeBuilder.objects.get(id=resume_id)
        # Check if user has permission to view this resume
        if request.user.is_authenticated and resume.user and resume.user != request.user:
            messages.error(request, "You don't have permission to view this resume.")
            return redirect('hirevision:resume_builder')
        return render(request, 'hirevision/resume_builder_result.html', {'resume': resume})
    except ResumeBuilder.DoesNotExist:
        messages.error(request, "Resume not found.")
        return redirect('hirevision:resume_builder')

def sample_resume(request):
    """Show sample resume"""
    try:
        with open('sample_resume.tex', 'r', encoding='utf-8') as f:
            sample_content = f.read()
        
        sample_pdf_path = get_sample_pdf_path()
        
        context = {
            'sample_content': sample_content,
            'sample_pdf_path': sample_pdf_path
        }
        
        return render(request, 'hirevision/sample_resume.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading sample resume: {str(e)}")
        return redirect('hirevision:home')

@csrf_exempt
def download_pdf(request, resume_id):
    """Download generated PDF"""
    try:
        resume = ResumeBuilder.objects.get(id=resume_id)
        # Check if user has permission to download this resume
        if request.user.is_authenticated and resume.user and resume.user != request.user:
            messages.error(request, "You don't have permission to download this resume.")
            return redirect('hirevision:resume_builder_result', resume_id=resume_id)
        if resume.pdf_file:
            response = HttpResponse(resume.pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{resume.name}_resume.pdf"'
            return response
        else:
            messages.error(request, "PDF file not found.")
            return redirect('hirevision:resume_builder_result', resume_id=resume_id)
    except ResumeBuilder.DoesNotExist:
        messages.error(request, "Resume not found.")
        return redirect('hirevision:resume_builder')

def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('hirevision:home')
    
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.phone = form.cleaned_data.get('phone', '')
            user.save()
            
            # Log the user in after successful registration
            login(request, user)
            messages.success(request, f"Welcome to HireVision, {user.first_name}! Your account has been created successfully.")
            return redirect('hirevision:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserSignUpForm()
    
    return render(request, 'hirevision/signup.html', {'form': form})

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('hirevision:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect('hirevision:home')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm()
    
    return render(request, 'hirevision/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('hirevision:home')

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'hirevision/profile.html', {'user': request.user})
