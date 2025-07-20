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
from .tasks import process_resume_analysis_task, process_learning_path_task, process_resume_builder_task

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
    """Resume analyzer view with async processing"""
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
                
                # Start async processing
                task = process_resume_analysis_task.send(str(analysis.id))
                analysis.task_id = task.message_id
                analysis.task_status = 'pending'
                analysis.save(update_fields=['task_id', 'task_status'])
                
                messages.success(request, "Resume analysis started! Your analysis is being processed in the background.")
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
    """Learning path analyzer view with async processing"""
    if request.method == 'POST':
        form = LearningPathForm(request.POST)
        if form.is_valid():
            try:
                # Save the form to get the model instance
                learning_path = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    learning_path.user = request.user
                
                # Save the model first
                learning_path.save()
                
                # Start async processing
                task = process_learning_path_task.send(str(learning_path.id))
                learning_path.task_id = task.message_id
                learning_path.task_status = 'pending'
                learning_path.save(update_fields=['task_id', 'task_status'])
                
                messages.success(request, "Learning path analysis started! Your personalized roadmap is being generated in the background.")
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
    """Resume builder view with async processing"""
    if request.method == 'POST':
        form = ResumeBuilderForm(request.POST)
        if form.is_valid():
            try:
                # Save the form to get the model instance
                resume = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    resume.user = request.user
                
                # Save the model first
                resume.save()
                
                # Start async processing
                task = process_resume_builder_task.send(str(resume.id))
                resume.task_id = task.message_id
                resume.task_status = 'pending'
                resume.save(update_fields=['task_id', 'task_status'])
                
                messages.success(request, "Resume building started! Your professional resume is being generated in the background.")
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

# Status checking endpoints for async tasks
@login_required
def check_resume_analysis_status(request, analysis_id):
    """Check the status of a resume analysis task"""
    try:
        analysis = ResumeAnalysis.objects.get(id=analysis_id)
        # Check if user has permission to view this analysis
        if request.user.is_authenticated and analysis.user and analysis.user != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return JsonResponse({
            'status': analysis.task_status,
            'error': analysis.task_error,
            'has_results': analysis.task_status == 'completed' and analysis.ats_score is not None
        })
    except ResumeAnalysis.DoesNotExist:
        return JsonResponse({'error': 'Analysis not found'}, status=404)

@login_required
def check_learning_path_status(request, path_id):
    """Check the status of a learning path analysis task"""
    try:
        learning_path = LearningPath.objects.get(id=path_id)
        # Check if user has permission to view this learning path
        if request.user.is_authenticated and learning_path.user and learning_path.user != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return JsonResponse({
            'status': learning_path.task_status,
            'error': learning_path.task_error,
            'has_results': learning_path.task_status == 'completed' and learning_path.role_analysis
        })
    except LearningPath.DoesNotExist:
        return JsonResponse({'error': 'Learning path not found'}, status=404)

@login_required
def check_resume_builder_status(request, resume_id):
    """Check the status of a resume builder task"""
    try:
        resume = ResumeBuilder.objects.get(id=resume_id)
        # Check if user has permission to view this resume
        if request.user.is_authenticated and resume.user and resume.user != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        return JsonResponse({
            'status': resume.task_status,
            'error': resume.task_error,
            'has_results': resume.task_status == 'completed' and resume.latex_content
        })
    except ResumeBuilder.DoesNotExist:
        return JsonResponse({'error': 'Resume not found'}, status=404)
