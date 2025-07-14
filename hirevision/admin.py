from django.contrib import admin
from .models import ResumeAnalysis, LearningPath, ResumeBuilder

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'ats_score', 'resume_file']
    list_filter = ['created_at', 'ats_score']
    search_fields = ['job_description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'dream_role', 'timeline']
    list_filter = ['created_at']
    search_fields = ['dream_role', 'current_skills']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(ResumeBuilder)
class ResumeBuilderAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'name', 'email', 'has_pdf']
    list_filter = ['created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def has_pdf(self, obj):
        return bool(obj.pdf_file)
    has_pdf.boolean = True
    has_pdf.short_description = 'Has PDF'
