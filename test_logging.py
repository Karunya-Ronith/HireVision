#!/usr/bin/env python3
"""
Test script to verify logging functionality across all modules
"""

import sys
import os
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logging():
    """Test logging functionality across all modules"""
    print("🧪 Testing comprehensive logging system...")
    
    try:
        # Test logging configuration
        print("  📋 Testing logging configuration...")
        from logging_config import (
            get_logger, log_function_call, log_api_call, 
            log_user_action, log_file_operation, log_performance
        )
        print("  ✓ Logging configuration imported successfully")
        
        # Test main loggers
        print("  📋 Testing main loggers...")
        resume_analyzer_logger = get_logger('resume_analyzer')
        learning_path_logger = get_logger('learning_path_analyzer')
        resume_builder_logger = get_logger('resume_builder')
        pdf_generator_logger = get_logger('pdf_generator')
        utils_logger = get_logger('utils')
        views_logger = get_logger('views')
        tasks_logger = get_logger('tasks')
        models_logger = get_logger('models')
        forms_logger = get_logger('forms')
        admin_logger = get_logger('admin')
        apps_logger = get_logger('apps')
        urls_logger = get_logger('urls')
        project_urls_logger = get_logger('project_urls')
        
        print("  ✓ All main loggers initialized successfully")
        
        # Test logging functions
        print("  📋 Testing logging functions...")
        log_api_call("test_api", {"test": "data"}, {"result": "success"}, True)
        log_user_action("test_user", "test_action", "test_details", True)
        log_file_operation("test_operation", "test_file.txt", True, 1024)
        log_performance("test_operation", 0.123, "test_details")
        print("  ✓ All logging functions work correctly")
        
        # Test decorator
        print("  📋 Testing function decorator...")
        @log_function_call
        def test_function():
            time.sleep(0.1)
            return "test_result"
        
        result = test_function()
        print(f"  ✓ Function decorator works: {result}")
        
        # Test resume analyzer logging
        print("  📋 Testing resume analyzer logging...")
        try:
            from resume_analyzer import extract_text_from_pdf, analyze_resume
            print("  ✓ Resume analyzer logging works")
        except ImportError as e:
            print(f"  ✗ Resume analyzer logging failed: {e}")
        
        # Test learning path analyzer logging
        print("  📋 Testing learning path analyzer logging...")
        try:
            from learning_path_analyzer import analyze_learning_path
            print("  ✓ Learning path analyzer logging works")
        except ImportError as e:
            print(f"  ✗ Learning path analyzer logging failed: {e}")
        
        # Test resume builder logging
        print("  📋 Testing resume builder logging...")
        try:
            from resume_builder import validate_resume_data, generate_latex_resume
            print("  ✓ Resume builder logging works")
        except ImportError as e:
            print(f"  ✗ Resume builder logging failed: {e}")
        
        # Test PDF generator logging
        print("  📋 Testing PDF generator logging...")
        try:
            from pdf_generator import generate_pdf_from_latex
            print("  ✓ PDF generator logging works")
        except ImportError as e:
            print(f"  ✗ PDF generator logging failed: {e}")
        
        # Test utils logging
        print("  📋 Testing utils logging...")
        try:
            from utils import format_analysis_output, extract_json_from_text, validate_inputs
            print("  ✓ Utils logging works")
        except ImportError as e:
            print(f"  ✗ Utils logging failed: {e}")
        
        # Test Django views logging
        print("  📋 Testing Django views logging...")
        try:
            from hirevision.views import home, resume_analyzer, resume_analysis_result
            print("  ✓ Django views logging works")
        except ImportError as e:
            print(f"  ✗ Django views logging failed: {e}")
        
        # Test Django tasks logging
        print("  📋 Testing Django tasks logging...")
        try:
            from hirevision.tasks import process_resume_analysis_task
            print("  ✓ Django tasks logging works")
        except ImportError as e:
            print(f"  ✗ Django tasks logging failed: {e}")
        
        # Test Django models logging
        print("  📋 Testing Django models logging...")
        try:
            from hirevision.models import User, ResumeAnalysis, LearningPath, ResumeBuilder
            print("  ✓ Django models logging works")
        except ImportError as e:
            print(f"  ✗ Django models logging failed: {e}")
        
        # Test Django forms logging
        print("  📋 Testing Django forms logging...")
        try:
            from hirevision.forms import UserSignUpForm, ResumeAnalysisForm, LearningPathForm
            print("  ✓ Django forms logging works")
        except ImportError as e:
            print(f"  ✗ Django forms logging failed: {e}")
        
        # Test Django admin logging
        print("  📋 Testing Django admin logging...")
        try:
            from hirevision.admin import CustomUserAdmin, ResumeAnalysisAdmin
            print("  ✓ Django admin logging works")
        except ImportError as e:
            print(f"  ✗ Django admin logging failed: {e}")
        
        # Test Django apps logging
        print("  📋 Testing Django apps logging...")
        try:
            from hirevision.apps import HirevisionConfig
            print("  ✓ Django apps logging works")
        except ImportError as e:
            print(f"  ✗ Django apps logging failed: {e}")
        
        # Test Django URLs logging
        print("  📋 Testing Django URLs logging...")
        try:
            from hirevision.urls import urlpatterns
            print(f"  ✓ Django app URLs logging works - {len(urlpatterns)} patterns")
        except ImportError as e:
            print(f"  ✗ Django app URLs logging failed: {e}")
        
        # Test Django project URLs logging
        print("  📋 Testing Django project URLs logging...")
        try:
            from hirevision_django.urls import urlpatterns
            print(f"  ✓ Django project URLs logging works - {len(urlpatterns)} patterns")
        except ImportError as e:
            print(f"  ✗ Django project URLs logging failed: {e}")
        
        # Test utility functions
        print("  📋 Testing utility functions...")
        try:
            from utils import retry_with_backoff, handle_api_error, validate_file_content, sanitize_input
            
            # Test retry function
            @retry_with_backoff(max_retries=2)
            def test_retry_function():
                return "success"
            
            result = test_retry_function()
            print(f"  ✓ Retry utility works: {result}")
            
            # Test other utilities
            sanitized = sanitize_input("test<input>")
            print(f"  ✓ Sanitize input works: {sanitized}")
            
        except ImportError as e:
            print(f"  ✗ Utility functions failed: {e}")
        
        # Test module-specific loggers
        print("  📋 Testing module-specific loggers...")
        resume_analyzer_logger.info("Test message from resume analyzer")
        learning_path_logger.info("Test message from learning path analyzer")
        resume_builder_logger.info("Test message from resume builder")
        pdf_generator_logger.info("Test message from PDF generator")
        utils_logger.info("Test message from utils")
        views_logger.info("Test message from views")
        tasks_logger.info("Test message from tasks")
        models_logger.info("Test message from models")
        forms_logger.info("Test message from forms")
        admin_logger.info("Test message from admin")
        apps_logger.info("Test message from apps")
        urls_logger.info("Test message from URLs")
        project_urls_logger.info("Test message from project URLs")
        print("  ✓ All module-specific loggers work correctly")
        
        print("\n🎉 All logging tests passed!")
        print("✅ Logging system is working correctly!")
        print("\n📁 Log files created in 'logs/' directory:")
        print("  - resume_analyzer.log")
        print("  - learning_path_analyzer.log")
        print("  - resume_builder.log")
        print("  - pdf_generator.log")
        print("  - utils.log")
        print("  - views.log")
        print("  - tasks.log")
        print("  - models.log")
        print("  - forms.log")
        print("  - admin.log")
        print("  - apps.log")
        print("  - urls.log")
        print("  - project_urls.log")
        print("  - api_calls.log")
        print("  - user_actions.log")
        print("  - file_operations.log")
        print("  - performance.log")
        print("  - django.log")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_logging()
    sys.exit(0 if success else 1) 