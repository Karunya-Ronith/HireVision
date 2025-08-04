from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User, Thread, Comment, Conversation, Message
import time
from logging_config import get_logger, log_function_call, log_performance

# Initialize logger for admin
logger = get_logger('admin')

# Log admin registration
logger.info("Registering Django admin models for HireVision")

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
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        if change:
            logger.info(f"Admin updating user: {obj.email}")
        else:
            logger.info(f"Admin creating new user: {obj.email}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin user save", duration, f"User: {obj.email}, Change: {change}")
            logger.info(f"Admin user save successful: {obj.email}")
            return result
        except Exception as e:
            logger.error(f"Admin user save failed: {obj.email}, Error: {str(e)}", exc_info=True)
            raise

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
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        user_info = f"User: {obj.user.email}" if obj.user else "Anonymous"
        if change:
            logger.info(f"Admin updating resume analysis: {obj.id}, {user_info}")
        else:
            logger.info(f"Admin creating new resume analysis: {user_info}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin resume analysis save", duration, f"ID: {obj.id}, User: {user_info}")
            logger.info(f"Admin resume analysis save successful: {obj.id}")
            return result
        except Exception as e:
            logger.error(f"Admin resume analysis save failed: {obj.id}, Error: {str(e)}", exc_info=True)
            raise

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
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        user_info = f"User: {obj.user.email}" if obj.user else "Anonymous"
        if change:
            logger.info(f"Admin updating learning path: {obj.id}, {user_info}, Role: {obj.dream_role}")
        else:
            logger.info(f"Admin creating new learning path: {user_info}, Role: {obj.dream_role}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin learning path save", duration, f"ID: {obj.id}, User: {user_info}, Role: {obj.dream_role}")
            logger.info(f"Admin learning path save successful: {obj.id}")
            return result
        except Exception as e:
            logger.error(f"Admin learning path save failed: {obj.id}, Error: {str(e)}", exc_info=True)
            raise

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
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        user_info = f"User: {obj.user.email}" if obj.user else "Anonymous"
        if change:
            logger.info(f"Admin updating resume builder: {obj.id}, {user_info}, Name: {obj.name}")
        else:
            logger.info(f"Admin creating new resume builder: {user_info}, Name: {obj.name}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin resume builder save", duration, f"ID: {obj.id}, User: {user_info}, Name: {obj.name}")
            logger.info(f"Admin resume builder save successful: {obj.id}")
            return result
        except Exception as e:
            logger.error(f"Admin resume builder save failed: {obj.id}, Error: {str(e)}", exc_info=True)
            raise

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
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        if change:
            logger.info(f"Admin updating thread: {obj.id}, User: {obj.user.email}, Title: {obj.title}")
        else:
            logger.info(f"Admin creating new thread: User: {obj.user.email}, Title: {obj.title}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin thread save", duration, f"ID: {obj.id}, User: {obj.user.email}, Title: {obj.title}")
            logger.info(f"Admin thread save successful: {obj.id}")
            return result
        except Exception as e:
            logger.error(f"Admin thread save failed: {obj.id}, Error: {str(e)}", exc_info=True)
            raise

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
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        if change:
            logger.info(f"Admin updating comment: {obj.id}, User: {obj.user.email}, Thread: {obj.thread.title}")
        else:
            logger.info(f"Admin creating new comment: User: {obj.user.email}, Thread: {obj.thread.title}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin comment save", duration, f"ID: {obj.id}, User: {obj.user.email}, Thread: {obj.thread.title}")
            logger.info(f"Admin comment save successful: {obj.id}")
            return result
        except Exception as e:
            logger.error(f"Admin comment save failed: {obj.id}, Error: {str(e)}", exc_info=True)
            raise

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participants_display', 'message_count', 'last_message_time', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participants__username', 'participants__email']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    @log_function_call
    def participants_display(self, obj):
        participants = [user.username for user in obj.participants.all()]
        logger.debug(f"Getting participants display for conversation {obj.id}: {participants}")
        return ', '.join(participants)
    participants_display.short_description = 'Participants'
    
    @log_function_call
    def message_count(self, obj):
        count = obj.messages.count()
        logger.debug(f"Getting message count for conversation {obj.id}: {count}")
        return count
    message_count.short_description = 'Messages'
    
    @log_function_call
    def last_message_time(self, obj):
        last_msg = obj.last_message
        result = last_msg.created_at if last_msg else 'No messages'
        logger.debug(f"Getting last message time for conversation {obj.id}: {result}")
        return result
    last_message_time.short_description = 'Last Message'
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        participant_names = [user.username for user in obj.participants.all()]
        if change:
            logger.info(f"Admin updating conversation: {obj.id}, Participants: {participant_names}")
        else:
            logger.info(f"Admin creating new conversation: Participants: {participant_names}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin conversation save", duration, f"ID: {obj.id}, Participants: {participant_names}")
            logger.info(f"Admin conversation save successful: {obj.id}")
            return result
        except Exception as e:
            logger.error(f"Admin conversation save failed: {obj.id}, Error: {str(e)}", exc_info=True)
            raise

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'content_preview', 'has_media', 'is_read', 'created_at']
    list_filter = ['created_at', 'is_read', 'sender', 'conversation']
    search_fields = ['content', 'sender__username', 'conversation__id']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    @log_function_call
    def content_preview(self, obj):
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        logger.debug(f"Getting content preview for message {obj.id}: {preview}")
        return preview
    content_preview.short_description = 'Content'
    
    @log_function_call
    def has_media(self, obj):
        has_media = bool(obj.image)
        logger.debug(f"Checking if message {obj.id} has media: {has_media}")
        return has_media
    has_media.boolean = True
    has_media.short_description = 'Has Media'
    
    def save_model(self, request, obj, form, change):
        start_time = time.time()
        if change:
            logger.info(f"Admin updating message: {obj.id}, Sender: {obj.sender.email}, Conversation: {obj.conversation.id}")
        else:
            logger.info(f"Admin creating new message: Sender: {obj.sender.email}, Conversation: {obj.conversation.id}")
        
        try:
            result = super().save_model(request, obj, form, change)
            duration = time.time() - start_time
            log_performance("Admin message save", duration, f"ID: {obj.id}, Sender: {obj.sender.email}, Conversation: {obj.conversation.id}")
            logger.info(f"Admin message save successful: {obj.id}")
            return result
        except Exception as e:
            logger.error(f"Admin message save failed: {obj.id}, Error: {str(e)}", exc_info=True)
            raise

logger.info("Django admin registration completed successfully")
