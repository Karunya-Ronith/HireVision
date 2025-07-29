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

from .forms import ResumeAnalysisForm, LearningPathForm, ResumeBuilderForm, UserSignUpForm, UserLoginForm, ThreadForm, CommentForm, MessageForm, UserSearchForm
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User, Thread, Comment, Message, Conversation
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
                
                messages.success(request, "Learning path analysis started! Your analysis is being processed in the background.")
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
                
                messages.success(request, "Resume generation started! Your resume is being processed in the background.")
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
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related(
        'participants', 'messages__sender'
    ).order_by('-updated_at')
    
    # Get unread counts for each conversation
    for conversation in conversations:
        conversation.unread_count = conversation.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
    
    return render(request, 'hirevision/messages_list.html', {'conversations': conversations})

@login_required
def conversation_detail(request, conversation_id):
    """Display a conversation and its messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    messages = conversation.messages.all().select_related('sender').order_by('created_at')
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Update conversation timestamp
            conversation.save()
            
            messages.success(request, "Message sent successfully!")
            return redirect('hirevision:conversation_detail', conversation_id=conversation_id)
    else:
        form = MessageForm()
    
    # Get other participant
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    
    context = {
        'conversation': conversation,
        'messages': messages,
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
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        return redirect('hirevision:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
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
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        return redirect('hirevision:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
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
