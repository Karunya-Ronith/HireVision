from django.urls import path
from . import views
from logging_config import get_logger

# Initialize logger for URLs
logger = get_logger('urls')

app_name = 'hirevision'

# Log URL pattern registration
logger.info("Registering HireVision URL patterns")

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Resume Analysis
    path('resume-analyzer/', views.resume_analyzer, name='resume_analyzer'),
    path('resume-analysis/<uuid:analysis_id>/', views.resume_analysis_result, name='resume_analysis_result'),
    path('check-resume-status/<uuid:analysis_id>/', views.check_resume_analysis_status, name='check_resume_analysis_status'),
    
    # API endpoints for status checking (frontend compatibility)
    path('api/resume-analysis/<uuid:analysis_id>/status/', views.check_resume_analysis_status, name='api_resume_analysis_status'),
    path('api/learning-path/<uuid:path_id>/status/', views.check_learning_path_status, name='api_learning_path_status'),
    path('api/resume-builder/<uuid:resume_id>/status/', views.check_resume_builder_status, name='api_resume_builder_status'),
    
    # Learning Path
    path('learning-path/', views.learning_path_analyzer, name='learning_path_analyzer'),
    path('learning-path/<uuid:path_id>/', views.learning_path_result, name='learning_path_result'),
    path('check-learning-status/<uuid:path_id>/', views.check_learning_path_status, name='check_learning_path_status'),
    
    # Resume Builder
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume-builder/<uuid:resume_id>/', views.resume_builder_result, name='resume_builder_result'),
    path('check-resume-builder-status/<uuid:resume_id>/', views.check_resume_builder_status, name='check_resume_builder_status'),
    path('download-pdf/<uuid:resume_id>/', views.download_pdf, name='download_pdf'),
    
    # Sample Resume
    path('sample-resume/', views.sample_resume, name='sample_resume'),
    
    # Threads and Comments
    path('threads/', views.threads_list, name='threads_list'),
    path('threads/create/', views.create_thread, name='create_thread'),
    path('threads/<uuid:thread_id>/', views.thread_detail, name='thread_detail'),
    path('threads/<uuid:thread_id>/edit/', views.edit_thread, name='edit_thread'),
    path('threads/<uuid:thread_id>/delete/', views.delete_thread, name='delete_thread'),
    path('threads/<uuid:thread_id>/like/', views.like_thread, name='like_thread'),
    path('threads/<uuid:thread_id>/likes/', views.get_thread_likes, name='get_thread_likes'),
    path('comments/<uuid:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<uuid:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Messaging
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/new/', views.new_message, name='new_message'),
    path('messages/conversation/<uuid:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('messages/conversation/<uuid:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('messages/conversation/<uuid:conversation_id>/new-messages/', views.get_new_messages, name='get_new_messages'),
    path('messages/start/<uuid:user_id>/', views.start_conversation, name='start_conversation'),
    path('messages/from-thread/<uuid:thread_id>/<uuid:user_id>/', views.message_from_thread, name='message_from_thread'),
    path('messages/search-users/', views.search_users_ajax, name='search_users_ajax'),
]

logger.info(f"Registered {len(urlpatterns)} URL patterns for HireVision app")
logger.debug("URL patterns include: main pages, resume analysis, learning path, resume builder, threads, comments, messaging, and API endpoints") 