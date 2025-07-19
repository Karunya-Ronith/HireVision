from django.urls import path
from . import views

app_name = 'hirevision'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('resume-analyzer/', views.resume_analyzer, name='resume_analyzer'),
    path('resume-analysis/<uuid:analysis_id>/', views.resume_analysis_result, name='resume_analysis_result'),
    path('learning-path/', views.learning_path_analyzer, name='learning_path_analyzer'),
    path('learning-path/<uuid:path_id>/', views.learning_path_result, name='learning_path_result'),
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume-builder/<uuid:resume_id>/', views.resume_builder_result, name='resume_builder_result'),
    path('sample-resume/', views.sample_resume, name='sample_resume'),
    path('download-pdf/<uuid:resume_id>/', views.download_pdf, name='download_pdf'),
] 