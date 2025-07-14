from django.db import models
from django.utils import timezone
import json

class ResumeAnalysis(models.Model):
    """Model to store resume analysis results"""
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
