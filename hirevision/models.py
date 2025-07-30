from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import json
import uuid

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
        return self.email
    
    def save(self, *args, **kwargs):
        # Ensure username is unique
        if not self.username:
            # Generate a unique username based on email if not provided
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)

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
        return f"Resume Analysis - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class LearningPath(models.Model):
    """Model to store learning path analysis results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    current_skills = models.TextField()
    dream_role = models.CharField(max_length=200)
    
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
        return f"Learning Path - {self.dream_role} ({self.created_at.strftime('%Y-%m-%d')})"

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
        return f"Resume - {self.name} ({self.created_at.strftime('%Y-%m-%d')})"

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
        return f"{self.title} by {self.user.username}"
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    @property
    def has_media(self):
        return bool(self.image or self.article_url)

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
        return f"Comment by {self.user.username} on {self.thread.title}"
    
    @property
    def has_media(self):
        return bool(self.image)

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
        return f"Conversation between {' and '.join(participant_names)}"
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    @property
    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

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
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def has_media(self):
        return bool(self.image)
