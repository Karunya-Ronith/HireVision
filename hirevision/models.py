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
