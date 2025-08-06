from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import json
import uuid
import time
from logging_config import get_logger, log_function_call, log_performance

# Initialize logger for models
logger = get_logger('models')

class User(AbstractUser):
    """Custom User model with additional fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        logger.debug(f"User string representation called for user ID: {self.id}")
        return self.email
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        logger.info(f"Saving user with email: {self.email}")
        
        # Ensure username is unique
        if not self.username:
            logger.debug(f"Generating username for user with email: {self.email}")
            # Generate a unique username based on email if not provided
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
            logger.info(f"Generated username: {username} for user: {self.email}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("User save operation", duration, f"User: {self.email}")
            logger.info(f"User saved successfully: {self.email}")
            return result
        except Exception as e:
            logger.error(f"Failed to save user {self.email}: {str(e)}", exc_info=True)
            raise

class ResumeAnalysis(models.Model):
    """Model to store resume analysis results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    resume_file = models.FileField(upload_to='resumes/')
    job_description = models.TextField()
    
    # Task tracking fields
    task_id = models.CharField(max_length=255, null=True, blank=True)
    task_status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    task_error = models.TextField(blank=True, null=True)
    
    ats_score = models.IntegerField(null=True, blank=True)
    score_explanation = models.TextField(blank=True)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    skills_gap = models.JSONField(default=list)
    upskilling_suggestions = models.JSONField(default=list)
    overall_assessment = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Resume Analyses"
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = f"User: {self.user.email}" if self.user else "Anonymous"
        logger.debug(f"ResumeAnalysis string representation called for ID: {self.id}, {user_info}")
        return f"Resume Analysis - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        user_info = f"User: {self.user.email}" if self.user else "Anonymous"
        logger.info(f"Saving ResumeAnalysis for {user_info}, task_status: {self.task_status}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("ResumeAnalysis save operation", duration, f"User: {user_info}")
            logger.info(f"ResumeAnalysis saved successfully for {user_info}")
            return result
        except Exception as e:
            logger.error(f"Failed to save ResumeAnalysis for {user_info}: {str(e)}", exc_info=True)
            raise

class LearningPath(models.Model):
    """Model to store learning path analysis results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    current_skills = models.TextField()
    dream_role = models.CharField(max_length=500)
    
    # Task tracking fields
    task_id = models.CharField(max_length=255, null=True, blank=True)
    task_status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    task_error = models.TextField(blank=True, null=True)
    
    role_analysis = models.TextField(blank=True)
    skills_gap = models.JSONField(default=list)
    learning_path_data = models.JSONField(default=list)
    timeline = models.TextField(blank=True)
    success_metrics = models.JSONField(default=list)
    career_advice = models.TextField(blank=True)
    networking_tips = models.JSONField(default=list)
    
    class Meta:
        verbose_name_plural = "Learning Paths"
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = f"User: {self.user.email}" if self.user else "Anonymous"
        logger.debug(f"LearningPath string representation called for ID: {self.id}, {user_info}")
        return f"Learning Path - {self.dream_role} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        user_info = f"User: {self.user.email}" if self.user else "Anonymous"
        logger.info(f"Saving LearningPath for {user_info}, dream_role: {self.dream_role}, task_status: {self.task_status}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("LearningPath save operation", duration, f"User: {user_info}, Role: {self.dream_role}")
            logger.info(f"LearningPath saved successfully for {user_info}")
            return result
        except Exception as e:
            logger.error(f"Failed to save LearningPath for {user_info}: {str(e)}", exc_info=True)
            raise

class ResumeBuilder(models.Model):
    """Model to store resume builder data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    
    # Task tracking fields
    task_id = models.CharField(max_length=255, null=True, blank=True)
    task_status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    task_error = models.TextField(blank=True, null=True)
    
    education = models.JSONField(default=list)
    experience = models.JSONField(default=list)
    projects = models.JSONField(default=list)
    skills = models.JSONField(default=dict)
    research_papers = models.JSONField(default=list)
    achievements = models.JSONField(default=list)
    others = models.JSONField(default=list)
    latex_content = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='generated_resumes/', blank=True)
    
    class Meta:
        verbose_name_plural = "Resume Builders"
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = f"User: {self.user.email}" if self.user else "Anonymous"
        logger.debug(f"ResumeBuilder string representation called for ID: {self.id}, {user_info}")
        return f"Resume - {self.name} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        user_info = f"User: {self.user.email}" if self.user else "Anonymous"
        logger.info(f"Saving ResumeBuilder for {user_info}, name: {self.name}, task_status: {self.task_status}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("ResumeBuilder save operation", duration, f"User: {user_info}, Name: {self.name}")
            logger.info(f"ResumeBuilder saved successfully for {user_info}")
            return result
        except Exception as e:
            logger.error(f"Failed to save ResumeBuilder for {user_info}: {str(e)}", exc_info=True)
            raise

class Thread(models.Model):
    """Model for discussion forum threads"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='thread_images/', blank=True, null=True)
    article_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Threads"
        ordering = ['-created_at']
    
    def __str__(self):
        logger.debug(f"Thread string representation called for ID: {self.id}, User: {self.user.email}")
        return f"{self.title} by {self.user.username}"
    
    @property
    def comment_count(self):
        count = self.comments.count()
        logger.debug(f"Comment count calculated for thread {self.id}: {count}")
        return count
    
    @property
    def has_media(self):
        has_media = bool(self.image or self.article_url)
        logger.debug(f"Has media check for thread {self.id}: {has_media}")
        return has_media
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        logger.info(f"Saving Thread by user: {self.user.email}, title: {self.title}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("Thread save operation", duration, f"User: {self.user.email}, Title: {self.title}")
            logger.info(f"Thread saved successfully by {self.user.email}")
            return result
        except Exception as e:
            logger.error(f"Failed to save Thread by {self.user.email}: {str(e)}", exc_info=True)
            raise

class Comment(models.Model):
    """Model for comments on threads"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Comments"
        ordering = ['created_at']
    
    def __str__(self):
        logger.debug(f"Comment string representation called for ID: {self.id}, User: {self.user.email}")
        return f"Comment by {self.user.username} on {self.thread.title}"
    
    @property
    def has_media(self):
        has_media = bool(self.image)
        logger.debug(f"Has media check for comment {self.id}: {has_media}")
        return has_media
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        logger.info(f"Saving Comment by user: {self.user.email}, thread: {self.thread.title}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("Comment save operation", duration, f"User: {self.user.email}, Thread: {self.thread.title}")
            logger.info(f"Comment saved successfully by {self.user.email}")
            return result
        except Exception as e:
            logger.error(f"Failed to save Comment by {self.user.email}: {str(e)}", exc_info=True)
            raise

class Conversation(models.Model):
    """Model for conversations between two users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Conversations"
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = [user.username for user in self.participants.all()]
        logger.debug(f"Conversation string representation called for ID: {self.id}, Participants: {participant_names}")
        return f"Conversation between {' and '.join(participant_names)}"
    
    @property
    def last_message(self):
        last_msg = self.messages.order_by('-created_at').first()
        logger.debug(f"Last message retrieved for conversation {self.id}: {last_msg.id if last_msg else 'None'}")
        return last_msg
    
    def get_unread_count(self, user):
        count = self.messages.filter(is_read=False).exclude(sender=user).count()
        logger.debug(f"Unread count calculated for conversation {self.id}, user {user.email}: {count}")
        return count
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        participant_names = [user.username for user in self.participants.all()]
        logger.info(f"Saving Conversation between: {participant_names}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("Conversation save operation", duration, f"Participants: {participant_names}")
            logger.info(f"Conversation saved successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to save Conversation: {str(e)}", exc_info=True)
            raise

class Message(models.Model):
    """Model for individual messages in conversations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Messages"
        ordering = ['created_at']
    
    def __str__(self):
        logger.debug(f"Message string representation called for ID: {self.id}, Sender: {self.sender.email}")
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def has_media(self):
        has_media = bool(self.image)
        logger.debug(f"Has media check for message {self.id}: {has_media}")
        return has_media
    
    @log_function_call
    def save(self, *args, **kwargs):
        start_time = time.time()
        logger.info(f"Saving Message from user: {self.sender.email}, conversation: {self.conversation.id}")
        
        try:
            result = super().save(*args, **kwargs)
            duration = time.time() - start_time
            log_performance("Message save operation", duration, f"Sender: {self.sender.email}, Conversation: {self.conversation.id}")
            logger.info(f"Message saved successfully from {self.sender.email}")
            return result
        except Exception as e:
            logger.error(f"Failed to save Message from {self.sender.email}: {str(e)}", exc_info=True)
            raise