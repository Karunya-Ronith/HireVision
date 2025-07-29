from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User, Thread, Comment, Conversation, Message

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
    list_display = ['id', 'user', 'task_status', 'ats_score', 'created_at']
    list_filter = ['task_status', 'created_at']
    search_fields = ['user__username', 'user__email', 'job_description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'task_id', 'task_error']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'resume_file', 'job_description', 'created_at')
        }),
        ('Task Information', {
            'fields': ('task_id', 'task_status', 'task_error')
        }),
        ('Results', {
            'fields': ('ats_score', 'score_explanation', 'strengths', 'weaknesses', 
                      'recommendations', 'skills_gap', 'upskilling_suggestions', 'overall_assessment'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'dream_role', 'task_status', 'created_at']
    list_filter = ['task_status', 'created_at']
    search_fields = ['user__username', 'user__email', 'dream_role', 'current_skills']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'task_id', 'task_error']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'current_skills', 'dream_role', 'created_at')
        }),
        ('Task Information', {
            'fields': ('task_id', 'task_status', 'task_error')
        }),
        ('Results', {
            'fields': ('role_analysis', 'skills_gap', 'learning_path_data', 'timeline',
                      'success_metrics', 'career_advice', 'networking_tips'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ResumeBuilder)
class ResumeBuilderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'task_status', 'created_at']
    list_filter = ['task_status', 'created_at']
    search_fields = ['user__username', 'user__email', 'name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'task_id', 'task_error']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'email', 'phone', 'linkedin', 'github', 'created_at')
        }),
        ('Content', {
            'fields': ('education', 'experience', 'projects', 'skills', 'research_papers', 
                      'achievements', 'others'),
            'classes': ('collapse',)
        }),
        ('Task Information', {
            'fields': ('task_id', 'task_status', 'task_error')
        }),
        ('Generated Content', {
            'fields': ('latex_content', 'pdf_file'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'comment_count', 'has_media', 'created_at', 'is_edited']
    list_filter = ['created_at', 'is_edited', 'user']
    search_fields = ['title', 'content', 'user__username', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'content', 'created_at', 'updated_at')
        }),
        ('Media', {
            'fields': ('image', 'article_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_edited',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'thread', 'has_media', 'created_at', 'is_edited']
    list_filter = ['created_at', 'is_edited', 'user', 'thread']
    search_fields = ['content', 'user__username', 'thread__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('thread', 'user', 'content', 'created_at', 'updated_at')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_edited',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participants_display', 'message_count', 'last_message_time', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participants__username', 'participants__email']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def participants_display(self, obj):
        return ', '.join([user.username for user in obj.participants.all()])
    participants_display.short_description = 'Participants'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def last_message_time(self, obj):
        last_msg = obj.last_message
        return last_msg.created_at if last_msg else 'No messages'
    last_message_time.short_description = 'Last Message'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'content_preview', 'has_media', 'is_read', 'created_at']
    list_filter = ['created_at', 'is_read', 'sender', 'conversation']
    search_fields = ['content', 'sender__username', 'conversation__id']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def has_media(self, obj):
        return bool(obj.image)
    has_media.boolean = True
    has_media.short_description = 'Has Media'
