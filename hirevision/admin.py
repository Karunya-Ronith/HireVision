from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_staff', 'is_active', 'is_verified', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone', 'date_of_birth', 'profile_picture', 'bio', 'linkedin_url', 'github_url')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
        ('Status', {'fields': ('is_verified',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'ats_score', 'resume_file']
    list_filter = ['created_at', 'ats_score']
    search_fields = ['job_description', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'dream_role', 'timeline']
    list_filter = ['created_at']
    search_fields = ['dream_role', 'current_skills', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

@admin.register(ResumeBuilder)
class ResumeBuilderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'name', 'email', 'has_pdf']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    def has_pdf(self, obj):
        return bool(obj.pdf_file)
    has_pdf.boolean = True
    has_pdf.short_description = 'Has PDF'
