"""
Practical examples of integrating Pydantic schemas with Django views in HireVision

This file demonstrates how to use the Pydantic validation system throughout your application.
"""

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from ..validation import (
    validate_request_data, 
    validate_form_data,
    PydanticValidator,
    create_success_response,
    create_error_response
)
from ..schemas.user import UserRegistrationSchema, UserLoginSchema
from ..schemas.resume_analysis import ResumeAnalysisInputSchema
from ..schemas.learning_path import LearningPathInputSchema
from ..schemas.resume_builder import ResumeBuilderInputSchema
from ..forms import UserSignUpForm, ResumeAnalysisForm


# Example 1: API endpoint with Pydantic validation
@csrf_exempt
@require_http_methods(["POST"])
@validate_request_data(UserRegistrationSchema)
def api_register_user(request, validated_data):
    """
    API endpoint for user registration with Pydantic validation
    
    Usage:
    POST /api/users/register/
    {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password1": "securepassword123",
        "password2": "securepassword123",
        "phone": "+1234567890"
    }
    """
    try:
        # validated_data is already a UserRegistrationSchema instance
        # Create user with validated data
        user_data = validated_data.model_dump()
        
        # Your user creation logic here
        # user = User.objects.create_user(...)
        
        return create_success_response(
            message="User registered successfully",
            data={"user_id": "example-uuid", "username": user_data["username"]}
        )
    except Exception as e:
        return create_error_response(f"Registration failed: {str(e)}", status=500)


# Example 2: Form-based view with Pydantic validation
@validate_form_data(UserRegistrationSchema, UserSignUpForm)
def register_user_form(request, form, validated_data):
    """
    Form-based user registration with Django form + Pydantic validation
    
    This combines Django form handling with Pydantic validation
    """
    if request.method == 'POST':
        if validated_data:
            # Both Django form and Pydantic validation passed
            try:
                # Use validated_data (Pydantic model) for business logic
                user_data = validated_data.model_dump()
                
                # Your user creation logic here
                # user = User.objects.create_user(...)
                
                return redirect('hirevision:home')
            except Exception as e:
                form.add_error(None, f"Registration failed: {str(e)}")
        
        # If validation failed, form will have errors
        return render(request, 'hirevision/signup.html', {'form': form})
    
    return render(request, 'hirevision/signup.html', {'form': form})


# Example 3: Manual validation in view
@login_required
def resume_analysis_view(request):
    """
    Resume analysis view with manual Pydantic validation
    """
    if request.method == 'POST':
        # Get data from request
        data = {
            'job_description': request.POST.get('job_description'),
            'resume_file': None  # Handle file separately
        }
        
        # Validate with Pydantic
        is_valid, validated_data, errors = PydanticValidator.validate_data(
            ResumeAnalysisInputSchema, 
            data
        )
        
        if is_valid:
            # Process the validated data
            try:
                # Your resume analysis logic here
                # analysis = process_resume_analysis(validated_data)
                
                return render(request, 'hirevision/resume_analysis_result.html', {
                    'analysis': 'example-analysis-result'
                })
            except Exception as e:
                return render(request, 'hirevision/resume_analyzer.html', {
                    'form': ResumeAnalysisForm(),
                    'error': f"Analysis failed: {str(e)}"
                })
        else:
            # Show validation errors
            error_messages = [f"{error.field}: {error.message}" for error in errors]
            return render(request, 'hirevision/resume_analyzer.html', {
                'form': ResumeAnalysisForm(),
                'errors': error_messages
            })
    
    return render(request, 'hirevision/resume_analyzer.html', {
        'form': ResumeAnalysisForm()
    })


# Example 4: JSON API with detailed validation
@csrf_exempt
@require_http_methods(["POST"])
def api_create_learning_path(request):
    """
    API endpoint for creating learning paths with comprehensive validation
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Validate with Pydantic
        is_valid, validated_data, errors = PydanticValidator.validate_data(
            LearningPathInputSchema,
            data
        )
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'validation_errors': [
                    {
                        'field': error.field,
                        'message': error.message,
                        'value': error.value
                    }
                    for error in errors
                ]
            }, status=400)
        
        # Process validated data
        try:
            # Your learning path creation logic here
            # learning_path = create_learning_path(validated_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Learning path created successfully',
                'data': {
                    'id': 'example-uuid',
                    'current_skills': validated_data.current_skills,
                    'dream_role': validated_data.dream_role
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to create learning path: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }, status=500)


# Example 5: File upload with validation
@csrf_exempt
@require_http_methods(["POST"])
def api_upload_resume(request):
    """
    API endpoint for resume upload with file validation
    """
    from ..validation import validate_file_upload
    
    # Validate uploaded file
    resume_file = request.FILES.get('resume')
    file_errors = validate_file_upload(
        resume_file,
        max_size=10 * 1024 * 1024,  # 10MB
        allowed_types=['application/pdf', 'application/msword']
    )
    
    if file_errors:
        return JsonResponse({
            'success': False,
            'error': 'File validation failed',
            'validation_errors': [
                {
                    'field': error.field,
                    'message': error.message,
                    'value': error.value
                }
                for error in file_errors
            ]
        }, status=400)
    
    # Process file upload
    try:
        # Your file processing logic here
        # saved_file = save_resume_file(resume_file)
        
        return JsonResponse({
            'success': True,
            'message': 'Resume uploaded successfully',
            'data': {
                'filename': resume_file.name,
                'size': resume_file.size,
                'content_type': resume_file.content_type
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }, status=500)


# Example 6: Converting Django model to Pydantic for API responses
def api_get_user_profile(request, user_id):
    """
    API endpoint that converts Django model to Pydantic for response
    """
    from ..validation import convert_django_model_to_pydantic
    from ..schemas.user import UserProfileSchema
    from ..models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        # Convert Django model to Pydantic
        user_profile = convert_django_model_to_pydantic(user, UserProfileSchema)
        
        return JsonResponse({
            'success': True,
            'data': user_profile.model_dump()
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to get user profile: {str(e)}'
        }, status=500)


# Example 7: Form with Pydantic mixin
from ..validation import PydanticFormMixin
from django import forms

class PydanticResumeBuilderForm(PydanticFormMixin, forms.Form):
    """
    Example form using PydanticFormMixin for additional validation
    """
    pydantic_schema = ResumeBuilderInputSchema
    
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    experience = forms.CharField(widget=forms.Textarea)
    skills = forms.CharField(widget=forms.Textarea)
    
    def clean(self):
        """This will include both Django and Pydantic validation"""
        cleaned_data = super().clean()
        
        # After validation, you can access the Pydantic model
        pydantic_data = self.get_pydantic_data()
        if pydantic_data:
            # Use the validated Pydantic model for additional processing
            pass
        
        return cleaned_data


def resume_builder_with_pydantic_form(request):
    """
    View using the PydanticFormMixin form
    """
    if request.method == 'POST':
        form = PydanticResumeBuilderForm(request.POST)
        if form.is_valid():
            # Get the Pydantic validated data
            pydantic_data = form.get_pydantic_data()
            if pydantic_data:
                # Use pydantic_data for business logic
                # resume = create_resume(pydantic_data)
                return redirect('hirevision:resume_builder_result', resume_id='example-id')
        
        return render(request, 'hirevision/resume_builder.html', {'form': form})
    
    form = PydanticResumeBuilderForm()
    return render(request, 'hirevision/resume_builder.html', {'form': form}) 