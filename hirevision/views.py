from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404
from django.db.models import Q
import json
import os
import time

from .forms import ResumeAnalysisForm, LearningPathForm, ResumeBuilderForm, UserSignUpForm, UserLoginForm, ThreadForm, CommentForm, MessageForm, UserSearchForm
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User, Thread, Comment, Message, Conversation
from .tasks import process_resume_analysis_task, process_learning_path_task, process_resume_builder_task

# Import the existing modules
from resume_analyzer import process_resume_analysis
from learning_path_analyzer import process_learning_path_analysis
from resume_builder import process_resume_builder
from pdf_generator import get_sample_pdf_path, generate_pdf_from_latex

# Import logging
from logging_config import get_logger, log_user_action, log_performance

# Initialize logger
logger = get_logger(__name__)

def home(request):
    """Home page view"""
    start_time = time.time()
    user_id = request.user.id if request.user.is_authenticated else 'anonymous'
    logger.info(f"Home page accessed by user: {user_id}")
    
    if request.user.is_authenticated:
        # Show dashboard for logged-in users
        logger.debug(f"Rendering dashboard for authenticated user: {user_id}")
        log_user_action(str(user_id), "view_dashboard", "User accessed dashboard")
        
        # Enhanced data for god-level dashboard
        user = request.user
        
        # Get user statistics
        resume_analyses = user.resumeanalysis_set.all()
        learning_paths = user.learningpath_set.all()
        resume_builders = user.resumebuilder_set.all()
        
        # Calculate success rates and performance metrics
        successful_analyses = resume_analyses.filter(task_status='completed')
        successful_paths = learning_paths.filter(task_status='completed')
        successful_builders = resume_builders.filter(task_status='completed')
        
        # Get recent activities (preserving the 3 recent learning paths as requested)
        recent_analyses = resume_analyses.order_by('-created_at')[:3]
        recent_paths = learning_paths.order_by('-created_at')[:3]  # Preserving these 3
        recent_builders = resume_builders.order_by('-created_at')[:3]
        
        # Calculate average ATS scores
        avg_ats_score = 0
        if successful_analyses.exists():
            avg_ats_score = sum(analysis.ats_score or 0 for analysis in successful_analyses) / successful_analyses.count()
        
        # Get community stats
        total_threads = user.threads.count()
        total_comments = user.comments.count()
        total_messages = user.sent_messages.count()
        
        # Prepare context with enhanced data
        context = {
            'user': user,
            'stats': {
                'resume_analyses_count': resume_analyses.count(),
                'learning_paths_count': learning_paths.count(),
                'resume_builders_count': resume_builders.count(),
                'successful_analyses_count': successful_analyses.count(),
                'successful_paths_count': successful_paths.count(),
                'successful_builders_count': successful_builders.count(),
                'avg_ats_score': round(avg_ats_score, 1),
                'total_threads': total_threads,
                'total_comments': total_comments,
                'total_messages': total_messages,
            },
            'recent_analyses': recent_analyses,
            'recent_paths': recent_paths,  # These 3 are preserved for your demo
            'recent_builders': recent_builders,
            'performance_metrics': {
                'analysis_success_rate': round((successful_analyses.count() / resume_analyses.count() * 100) if resume_analyses.count() > 0 else 0, 1),
                'path_success_rate': round((successful_paths.count() / learning_paths.count() * 100) if learning_paths.count() > 0 else 0, 1),
                'builder_success_rate': round((successful_builders.count() / resume_builders.count() * 100) if resume_builders.count() > 0 else 0, 1),
            }
        }
        
        duration = time.time() - start_time
        log_performance("Home page (dashboard)", duration, f"Dashboard rendered for user {user_id}")
        
        return render(request, 'hirevision/dashboard.html', context)
    else:
        # Show landing page for non-logged-in users
        logger.debug("Rendering landing page for anonymous user")
        log_user_action('anonymous', "view_landing", "Anonymous user accessed landing page")
        
        duration = time.time() - start_time
        log_performance("Home page (landing)", duration, "Landing page rendered for anonymous user")
        
        return render(request, 'hirevision/landing.html')

@login_required
def resume_analyzer(request):
    """Resume analyzer view with async processing"""
    start_time = time.time()
    user_id = request.user.id
    logger.info(f"Resume analyzer accessed by user: {user_id}")
    
    if request.method == 'POST':
        logger.info(f"Resume analysis form submitted by user: {user_id}")
        form = ResumeAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                logger.debug("Form validation successful, processing resume analysis")
                
                # Save the form to get the model instance
                analysis = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    analysis.user = request.user
                
                # Save the file first so it exists on disk
                analysis.save()
                logger.info(f"Resume analysis record created with ID: {analysis.id}")
                
                # Start async processing
                logger.info(f"Starting async task for analysis ID: {analysis.id}")
                task = process_resume_analysis_task.send(str(analysis.id))
                analysis.task_id = task.message_id
                analysis.task_status = 'pending'
                analysis.save(update_fields=['task_id', 'task_status'])
                
                log_user_action(str(user_id), "start_resume_analysis", f"Started analysis for file: {analysis.resume_file.name}")
                
                messages.success(request, "Resume analysis started! Your analysis is being processed in the background.")
                
                duration = time.time() - start_time
                log_performance("Resume analyzer POST", duration, f"Analysis started for user {user_id}, analysis ID: {analysis.id}")
                
                return redirect('hirevision:resume_analysis_result', analysis_id=analysis.id)
                
            except Exception as e:
                logger.error(f"Error in resume analyzer for user {user_id}: {str(e)}", exc_info=True)
                log_user_action(str(user_id), "resume_analysis_error", f"Error: {str(e)}", success=False)
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            logger.warning(f"Form validation failed for user {user_id}")
            log_user_action(str(user_id), "resume_analysis_validation_failed", "Form validation failed", success=False)
    else:
        logger.debug(f"Resume analyzer form displayed for user: {user_id}")
        form = ResumeAnalysisForm()
    
    duration = time.time() - start_time
    log_performance("Resume analyzer", duration, f"Resume analyzer page rendered for user {user_id}")
    
    return render(request, 'hirevision/resume_analyzer.html', {'form': form})

@login_required
def resume_analysis_result(request, analysis_id):
    """Display resume analysis result"""
    start_time = time.time()
    user_id = request.user.id
    logger.info(f"Resume analysis result accessed by user: {user_id}, analysis ID: {analysis_id}")
    
    try:
        analysis = ResumeAnalysis.objects.get(id=analysis_id)
        logger.debug(f"Analysis found: {analysis_id}, status: {analysis.task_status}")
        
        # Check if user has permission to view this analysis
        if request.user.is_authenticated and analysis.user and analysis.user != request.user:
            logger.warning(f"Permission denied: user {user_id} tried to access analysis {analysis_id} owned by user {analysis.user.id}")
            log_user_action(str(user_id), "unauthorized_access", f"Tried to access analysis {analysis_id}", success=False)
            messages.error(request, "You don't have permission to view this analysis.")
            return redirect('hirevision:resume_analyzer')
        
        log_user_action(str(user_id), "view_resume_analysis", f"Viewed analysis result: {analysis_id}")
        
        duration = time.time() - start_time
        log_performance("Resume analysis result", duration, f"Analysis result displayed for user {user_id}, analysis {analysis_id}")
        
        return render(request, 'hirevision/resume_analysis_result.html', {'analysis': analysis})
        
    except ResumeAnalysis.DoesNotExist:
        logger.error(f"Analysis not found: {analysis_id} for user: {user_id}")
        log_user_action(str(user_id), "analysis_not_found", f"Tried to access non-existent analysis: {analysis_id}", success=False)
        messages.error(request, "Analysis not found.")
        return redirect('hirevision:resume_analyzer')

@login_required
def learning_path_analyzer(request):
    """Learning path analyzer view with async processing and proper error handling"""
    start_time = time.time()
    user_id = request.user.id
    logger.info(f"Learning path analyzer accessed by user: {user_id}")
    
    if request.method == 'POST':
        logger.info(f"Learning path form submitted by user: {user_id}")
        form = LearningPathForm(request.POST)
        if form.is_valid():
            try:
                logger.debug("Form validation successful, processing learning path analysis")
                
                # Save the form to get the model instance
                learning_path = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    learning_path.user = request.user
                
                # Validate inputs before saving
                if not learning_path.current_skills or not learning_path.dream_role:
                    error_msg = "Please provide both your current skills and dream role"
                    logger.warning(f"Validation failed for user {user_id}: {error_msg}")
                    messages.error(request, error_msg)
                    return render(request, 'hirevision/learning_path_analyzer.html', {'form': form})
                
                # Save the model first
                learning_path.save()
                logger.info(f"Learning path record created with ID: {learning_path.id}")
                
                # Start async processing
                logger.info(f"Starting async task for learning path ID: {learning_path.id}")
                task = process_learning_path_task.send(str(learning_path.id))
                learning_path.task_id = task.message_id
                learning_path.task_status = 'pending'
                learning_path.save(update_fields=['task_id', 'task_status'])
                
                log_user_action(str(user_id), "start_learning_path_analysis", 
                              f"Started learning path analysis for skills: {len(learning_path.current_skills)} chars, role: {len(learning_path.dream_role)} chars")
                
                messages.success(request, "Learning path analysis started! Your personalized learning path is being generated in the background.")
                
                duration = time.time() - start_time
                log_performance("Learning path analyzer POST", duration, 
                              f"Learning path analysis started for user {user_id}, path ID: {learning_path.id}")
                
                return redirect('hirevision:learning_path_result', path_id=learning_path.id)
                
            except Exception as e:
                logger.error(f"Error in learning path analyzer for user {user_id}: {str(e)}", exc_info=True)
                log_user_action(str(user_id), "learning_path_analysis_error", f"Error: {str(e)}", success=False)
                messages.error(request, f"An error occurred while starting the learning path analysis. Please try again.")
        else:
            logger.warning(f"Form validation failed for user {user_id}: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = LearningPathForm()
        log_user_action(str(user_id), "view_learning_path_analyzer", "User accessed learning path analyzer")
    
    duration = time.time() - start_time
    log_performance("Learning path analyzer", duration, f"Learning path analyzer rendered for user {user_id}")
    
    return render(request, 'hirevision/learning_path_analyzer.html', {'form': form})

@login_required
def learning_path_result(request, path_id):
    """Display learning path result with proper error handling and user feedback"""
    start_time = time.time()
    user_id = request.user.id
    logger.info(f"Learning path result accessed by user: {user_id} for path ID: {path_id}")
    
    try:
        learning_path = LearningPath.objects.get(id=path_id)
        
        # Check if user has permission to view this learning path
        if learning_path.user and learning_path.user != request.user:
            logger.warning(f"User {user_id} attempted to access learning path {path_id} owned by user {learning_path.user.id}")
            messages.error(request, "You don't have permission to view this learning path.")
            return redirect('hirevision:learning_path_analyzer')
        
        # Log the access
        log_user_action(str(user_id), "view_learning_path_result", f"Viewed learning path result: {path_id}")
        
        # Check task status and provide appropriate feedback
        if learning_path.task_status == 'failed':
            logger.warning(f"Learning path {path_id} failed for user {user_id}: {learning_path.task_error}")
            messages.error(request, "The learning path analysis failed. Please try again or contact support if the issue persists.")
        elif learning_path.task_status == 'pending':
            logger.info(f"Learning path {path_id} still pending for user {user_id}")
            # No notification needed - user already got success message when analysis started
        elif learning_path.task_status == 'running':
            logger.info(f"Learning path {path_id} running for user {user_id}")
            # No notification needed - user already got success message when analysis started
        elif learning_path.task_status == 'completed':
            logger.info(f"Learning path {path_id} completed successfully for user {user_id}")
            # Check if we have meaningful data
            if not learning_path.role_analysis or len(learning_path.role_analysis.strip()) < 50:
                logger.warning(f"Learning path {path_id} completed but has insufficient data")
                messages.warning(request, "The learning path analysis completed but the results may be incomplete. Please try again.")
        
        duration = time.time() - start_time
        log_performance("Learning path result", duration, f"Learning path result rendered for user {user_id}, path ID: {path_id}")
        
        return render(request, 'hirevision/learning_path_result.html', {'learning_path': learning_path})
        
    except LearningPath.DoesNotExist:
        logger.error(f"Learning path {path_id} not found for user {user_id}")
        messages.error(request, "Learning path not found. It may have been deleted or you may have an invalid link.")
        return redirect('hirevision:learning_path_analyzer')
    except Exception as e:
        logger.error(f"Error accessing learning path result for user {user_id}, path ID {path_id}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading the learning path result. Please try again.")
        return redirect('hirevision:learning_path_analyzer')

@login_required
def resume_builder(request):
    """Resume builder view with step-by-step wizard and proper error handling"""
    start_time = time.time()
    user_id = request.user.id
    logger.info(f"Resume builder accessed by user: {user_id}")
    
    if request.method == 'POST':
        logger.info(f"Resume builder form submitted by user: {user_id}")
        form = ResumeBuilderForm(request.POST)
        if form.is_valid():
            try:
                logger.debug("Form validation successful, processing resume builder")
                
                # Save the form to get the model instance
                resume = form.save(commit=False)
                
                # Associate with current user if logged in
                if request.user.is_authenticated:
                    resume.user = request.user
                
                # Validate required fields
                required_fields = ['name', 'email']
                for field in required_fields:
                    if not getattr(resume, field):
                        error_msg = f"Please provide your {field.replace('_', ' ')}"
                        logger.warning(f"Validation failed for user {user_id}: {error_msg}")
                        messages.error(request, error_msg)
                        return render(request, 'hirevision/resume_builder.html', {'form': form})
                
                # Save the model first
                resume.save()
                logger.info(f"Resume builder record created with ID: {resume.id}")
                
                # Start async processing
                logger.info(f"Starting async task for resume builder ID: {resume.id}")
                task = process_resume_builder_task.send(str(resume.id))
                resume.task_id = task.message_id
                resume.task_status = 'pending'
                resume.save(update_fields=['task_id', 'task_status'])
                
                log_user_action(str(user_id), "start_resume_builder", 
                              f"Started resume builder for user: {resume.name}")
                
                messages.success(request, "Resume generation started! Your professional resume is being created in the background.")
                
                duration = time.time() - start_time
                log_performance("Resume builder POST", duration, 
                              f"Resume builder started for user {user_id}, resume ID: {resume.id}")
                
                return redirect('hirevision:resume_builder_result', resume_id=resume.id)
                
            except Exception as e:
                logger.error(f"Error in resume builder for user {user_id}: {str(e)}", exc_info=True)
                log_user_action(str(user_id), "resume_builder_error", f"Error: {str(e)}", success=False)
                messages.error(request, f"An error occurred while starting the resume generation. Please try again.")
        else:
            logger.warning(f"Form validation failed for user {user_id}: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ResumeBuilderForm()
        log_user_action(str(user_id), "view_resume_builder", "User accessed resume builder")
    
    duration = time.time() - start_time
    log_performance("Resume builder", duration, f"Resume builder rendered for user {user_id}")
    
    return render(request, 'hirevision/resume_builder.html', {'form': form})

@login_required
def resume_builder_result(request, resume_id):
    """Display resume builder result with proper error handling"""
    start_time = time.time()
    user_id = request.user.id
    logger.info(f"Resume builder result accessed by user: {user_id} for resume ID: {resume_id}")
    
    try:
        resume = ResumeBuilder.objects.get(id=resume_id)
        logger.debug(f"Resume found: {resume_id}, status: {resume.task_status}")
        
        # Check if user has permission to view this resume
        if request.user.is_authenticated and resume.user and resume.user != request.user:
            logger.warning(f"Permission denied: user {user_id} tried to access resume {resume_id} owned by user {resume.user.id}")
            log_user_action(str(user_id), "unauthorized_access", f"Tried to access resume {resume_id}", success=False)
            messages.error(request, "You don't have permission to view this resume.")
            return redirect('hirevision:resume_builder')
        
        log_user_action(str(user_id), "view_resume_builder_result", f"Viewed resume result: {resume_id}")
        
        # Check task status and provide appropriate feedback
        if resume.task_status == 'failed':
            logger.warning(f"Resume {resume_id} failed for user {user_id}: {resume.task_error}")
            messages.error(request, "The resume generation failed. Please try again or contact support if the issue persists.")
        elif resume.task_status == 'pending':
            logger.info(f"Resume {resume_id} still pending for user {user_id}")
            # No notification needed - user already got success message when generation started
        elif resume.task_status == 'running':
            logger.info(f"Resume {resume_id} running for user {user_id}")
            # No notification needed - user already got success message when generation started
        elif resume.task_status == 'completed':
            logger.info(f"Resume {resume_id} completed successfully for user {user_id}")
            # Check if we have meaningful data
            if not resume.latex_content or len(resume.latex_content.strip()) < 100:
                logger.warning(f"Resume {resume_id} completed but has insufficient data")
                messages.warning(request, "The resume generation completed but the results may be incomplete. Please try again.")
        
        duration = time.time() - start_time
        log_performance("Resume builder result", duration, f"Resume result displayed for user {user_id}, resume {resume_id}")
        
        return render(request, 'hirevision/resume_builder_result.html', {'resume': resume})
        
    except ResumeBuilder.DoesNotExist:
        logger.error(f"Resume {resume_id} not found for user {user_id}")
        log_user_action(str(user_id), "resume_not_found", f"Tried to access non-existent resume: {resume_id}", success=False)
        messages.error(request, "Resume not found. It may have been deleted or you may have an invalid link.")
        return redirect('hirevision:resume_builder')
    except Exception as e:
        logger.error(f"Error accessing resume builder result for user {user_id}, resume ID {resume_id}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading the resume result. Please try again.")
        return redirect('hirevision:resume_builder')

def sample_resume(request):
    """Sample resume view"""
    try:
        sample_pdf_path = get_sample_pdf_path()
        if os.path.exists(sample_pdf_path):
            with open(sample_pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="sample_resume.pdf"'
                return response
        else:
            messages.error(request, "Sample resume not found.")
            return redirect('hirevision:home')
    except Exception as e:
        messages.error(request, f"Error loading sample resume: {str(e)}")
        return redirect('hirevision:home')

@csrf_exempt
def download_pdf(request, resume_id):
    """Download generated PDF resume"""
    try:
        resume = ResumeBuilder.objects.get(id=resume_id)
        if resume.pdf_file and os.path.exists(resume.pdf_file.path):
            with open(resume.pdf_file.path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
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
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
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

# Thread and Comment Views
@login_required
def threads_list(request):
    """Display all threads"""
    threads = Thread.objects.all().select_related('user').prefetch_related('comments')
    return render(request, 'hirevision/threads_list.html', {'threads': threads})

@login_required
def thread_detail(request, thread_id):
    """Display a single thread with its comments"""
    thread = get_object_or_404(Thread, id=thread_id)
    comments = thread.comments.all().select_related('user')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.thread = thread
            comment.user = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('hirevision:thread_detail', thread_id=thread_id)
    else:
        comment_form = CommentForm()
    
    context = {
        'thread': thread,
        'comments': comments,
        'comment_form': comment_form
    }
    return render(request, 'hirevision/thread_detail.html', context)

@login_required
def create_thread(request):
    """Create a new thread"""
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.user = request.user
            thread.save()
            messages.success(request, "Thread created successfully!")
            return redirect('hirevision:thread_detail', thread_id=thread.id)
    else:
        form = ThreadForm()
    
    return render(request, 'hirevision/create_thread.html', {'form': form})

@login_required
def edit_thread(request, thread_id):
    """Edit a thread (only by creator)"""
    thread = get_object_or_404(Thread, id=thread_id)
    
    # Check if user is the creator
    if thread.user != request.user:
        messages.error(request, "You can only edit your own threads.")
        return redirect('hirevision:thread_detail', thread_id=thread_id)
    
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES, instance=thread)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.is_edited = True
            thread.save()
            messages.success(request, "Thread updated successfully!")
            return redirect('hirevision:thread_detail', thread_id=thread_id)
    else:
        form = ThreadForm(instance=thread)
    
    return render(request, 'hirevision/edit_thread.html', {'form': form, 'thread': thread})

@login_required
def delete_thread(request, thread_id):
    """Delete a thread (only by creator)"""
    thread = get_object_or_404(Thread, id=thread_id)
    
    # Check if user is the creator
    if thread.user != request.user:
        messages.error(request, "You can only delete your own threads.")
        return redirect('hirevision:thread_detail', thread_id=thread_id)
    
    if request.method == 'POST':
        thread.delete()
        messages.success(request, "Thread deleted successfully!")
        return redirect('hirevision:threads_list')
    
    return render(request, 'hirevision/delete_thread.html', {'thread': thread})

@login_required
def edit_comment(request, comment_id):
    """Edit a comment (only by creator)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user is the creator
    if comment.user != request.user:
        messages.error(request, "You can only edit your own comments.")
        return redirect('hirevision:thread_detail', thread_id=comment.thread.id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.is_edited = True
            comment.save()
            messages.success(request, "Comment updated successfully!")
            return redirect('hirevision:thread_detail', thread_id=comment.thread.id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'hirevision/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    """Delete a comment (only by creator)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user is the creator
    if comment.user != request.user:
        messages.error(request, "You can only delete your own comments.")
        return redirect('hirevision:thread_detail', thread_id=comment.thread.id)
    
    if request.method == 'POST':
        thread_id = comment.thread.id
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
        return redirect('hirevision:thread_detail', thread_id=thread_id)
    
    return render(request, 'hirevision/delete_comment.html', {'comment': comment})

# Messaging Views
@login_required
def messages_list(request):
    """Display all conversations for the current user"""
    # Get conversations with proper prefetching
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related(
        'participants', 'messages__sender'
    ).order_by('-updated_at')
    
    # Process each conversation to add computed fields
    for conversation in conversations:
        # Get unread count for the current user
        conversation.unread_count = conversation.get_unread_count(request.user)
        
        # Get other participant (not the current user)
        conversation.other_participant = conversation.participants.exclude(id=request.user.id).first()
    
    return render(request, 'hirevision/messages_list.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    """Display a conversation and its messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Get conversation messages
    conversation_messages = conversation.messages.all().select_related('sender').order_by('created_at')
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Update conversation timestamp
            conversation.save()
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                from django.http import JsonResponse
                from django.utils import timezone
                
                message_data = {
                    'id': str(message.id),
                    'content': message.content or '',
                    'image_url': message.image.url if message.image else None,
                    'sender_id': str(message.sender.id),
                    'sender_name': message.sender.get_full_name() or message.sender.username,
                    'created_at': message.created_at.strftime('%b %d, %I:%M %p'),
                    'is_read': message.is_read
                }
                
                return JsonResponse({
                    'success': True,
                    'message': message_data
                })
            else:
                # Regular form submission
                messages.success(request, "Message sent successfully!")
                return redirect('hirevision:conversation_detail', conversation_id=conversation_id)
        else:
            # Form validation failed
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid message data. Please check your input.'
                })
            else:
                # Regular form submission with errors
                pass
    else:
        form = MessageForm()
    
    # Get other participant
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    
    context = {
        'conversation': conversation,
        'messages': conversation_messages,
        'message_form': form,
        'other_participant': other_participant
    }
    return render(request, 'hirevision/conversation_detail.html', context)

@login_required
def new_message(request):
    """Start a new conversation or find existing one"""
    if request.method == 'POST':
        search_form = UserSearchForm(request.POST)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']
            
            # Search for users by username or full name
            users = User.objects.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            ).exclude(id=request.user.id)[:10]
            
            return render(request, 'hirevision/new_message.html', {
                'search_form': search_form,
                'users': users,
                'search_query': search_query
            })
    else:
        search_form = UserSearchForm()
    
    return render(request, 'hirevision/new_message.html', {'search_form': search_form})

@login_required
def start_conversation(request, user_id):
    """Start a conversation with a specific user"""
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, "You cannot message yourself.")
        return redirect('hirevision:new_message')
    
    # Check if conversation already exists between these two users
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        # Redirect to existing conversation
        return redirect('hirevision:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    # Update the conversation timestamp
    conversation.save()
    
    messages.success(request, f"Started conversation with {other_user.get_full_name() or other_user.username}")
    return redirect('hirevision:conversation_detail', conversation_id=conversation.id)

@login_required
def message_from_thread(request, thread_id, user_id):
    """Start a conversation with a user from a thread"""
    thread = get_object_or_404(Thread, id=thread_id)
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, "You cannot message yourself.")
        return redirect('hirevision:thread_detail', thread_id=thread_id)
    
    # Check if conversation already exists between these two users
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        # Redirect to existing conversation
        return redirect('hirevision:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    # Update the conversation timestamp
    conversation.save()
    
    messages.success(request, f"Started conversation with {other_user.get_full_name() or other_user.username}")
    return redirect('hirevision:conversation_detail', conversation_id=conversation.id)

@login_required
def delete_conversation(request, conversation_id):
    """Delete a conversation (remove current user from participants)"""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    if request.method == 'POST':
        conversation.participants.remove(request.user)
        
        # If no participants left, delete the conversation
        if conversation.participants.count() == 0:
            conversation.delete()
        
        messages.success(request, "Conversation deleted successfully!")
        return redirect('hirevision:messages_list')
    
    return render(request, 'hirevision/delete_conversation.html', {'conversation': conversation})

@login_required
def search_users_ajax(request):
    """AJAX endpoint for searching users"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if len(query) >= 2:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            ).exclude(id=request.user.id)[:10]
            
            user_list = []
            for user in users:
                user_list.append({
                    'id': str(user.id),
                    'username': user.username,
                    'full_name': user.get_full_name() or user.username,
                    'email': user.email
                })
            
            return JsonResponse({'users': user_list})
    
    return JsonResponse({'users': []})
