from django.urls import path
from . import views

app_name = 'hirevision'

urlpatterns = [
    path('', views.home, name='home'),
    path('resume-analyzer/', views.resume_analyzer, name='resume_analyzer'),
    path('resume-analysis/<int:analysis_id>/', views.resume_analysis_result, name='resume_analysis_result'),
    path('learning-path/', views.learning_path_analyzer, name='learning_path_analyzer'),
    path('learning-path/<int:path_id>/', views.learning_path_result, name='learning_path_result'),
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume-builder/<int:resume_id>/', views.resume_builder_result, name='resume_builder_result'),
    path('sample-resume/', views.sample_resume, name='sample_resume'),
    path('download-pdf/<int:resume_id>/', views.download_pdf, name='download_pdf'),
] 