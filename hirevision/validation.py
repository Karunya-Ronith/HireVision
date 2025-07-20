"""
Django-Pydantic integration utilities for HireVision application

This module provides utilities to integrate Pydantic validation with Django views and forms.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Type, Union

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import JsonResponse
from django.forms import Form
from pydantic import BaseModel, ValidationError as PydanticValidationError

from .schemas.api_responses import ErrorResponse, SuccessResponse, ValidationResponse
from .schemas.base import ValidationError

logger = logging.getLogger(__name__)


class PydanticValidator:
    """Utility class for Pydantic validation in Django"""

    @staticmethod
    def validate_data(schema: Type[BaseModel], data: Dict[str, Any]) -> tuple[bool, Optional[BaseModel], List[ValidationError]]:
        """
        Validate data against a Pydantic schema
        
        Args:
            schema: Pydantic model class
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, validated_data, errors)
        """
        try:
            validated_data = schema(**data)
            return True, validated_data, []
        except PydanticValidationError as e:
            errors = []
            for error in e.errors():
                field_path = '.'.join(str(loc) for loc in error['loc'])
                errors.append(ValidationError(
                    field=field_path,
                    message=error['msg'],
                    value=error.get('input')
                ))
            return False, None, errors

    @staticmethod
    def validate_json_data(schema: Type[BaseModel], json_data: str) -> tuple[bool, Optional[BaseModel], List[ValidationError]]:
        """
        Validate JSON string against a Pydantic schema
        
        Args:
            schema: Pydantic model class
            json_data: JSON string to validate
            
        Returns:
            Tuple of (is_valid, validated_data, errors)
        """
        try:
            data = json.loads(json_data)
            return PydanticValidator.validate_data(schema, data)
        except json.JSONDecodeError as e:
            errors = [ValidationError(
                field='json',
                message=f"Invalid JSON: {str(e)}",
                value=json_data
            )]
            return False, None, errors

    @staticmethod
    def django_form_to_pydantic(form: Form, schema: Type[BaseModel]) -> tuple[bool, Optional[BaseModel], List[ValidationError]]:
        """
        Convert Django form data to Pydantic model
        
        Args:
            form: Django form instance
            schema: Pydantic model class
            
        Returns:
            Tuple of (is_valid, validated_data, errors)
        """
        if not form.is_valid():
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(ValidationError(
                        field=field,
                        message=error,
                        value=form.data.get(field)
                    ))
            return False, None, errors
        
        return PydanticValidator.validate_data(schema, form.cleaned_data)

    @staticmethod
    def create_validation_response(errors: List[ValidationError]) -> ValidationResponse:
        """Create a validation response from errors"""
        return ValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )


def validate_request_data(schema: Type[BaseModel]):
    """
    Decorator to validate request data using Pydantic schemas
    
    Usage:
        @validate_request_data(UserRegistrationSchema)
        def register_user(request, validated_data):
            # validated_data is a Pydantic model instance
            pass
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                if request.method == 'POST':
                    if request.content_type == 'application/json':
                        data = json.loads(request.body)
                    else:
                        data = request.POST.dict()
                elif request.method == 'GET':
                    data = request.GET.dict()
                else:
                    data = {}

                is_valid, validated_data, errors = PydanticValidator.validate_data(schema, data)
                
                if not is_valid:
                    error_response = ErrorResponse(
                        error="Validation failed",
                        validation_errors=errors
                    )
                    return JsonResponse(error_response.model_dump(), status=400)
                
                return view_func(request, validated_data, *args, **kwargs)
                
            except json.JSONDecodeError:
                error_response = ErrorResponse(
                    error="Invalid JSON format"
                )
                return JsonResponse(error_response.model_dump(), status=400)
            except Exception as e:
                logger.error(f"Validation error: {str(e)}")
                error_response = ErrorResponse(
                    error="Internal validation error"
                )
                return JsonResponse(error_response.model_dump(), status=500)
        
        return wrapper
    return decorator


def validate_form_data(schema: Type[BaseModel], form_class: Type[Form]):
    """
    Decorator to validate Django form data with Pydantic
    
    Usage:
        @validate_form_data(UserRegistrationSchema, UserSignUpForm)
        def register_user(request, form, validated_data):
            # form is Django form, validated_data is Pydantic model
            pass
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                form = form_class(request.POST, request.FILES)
                is_valid, validated_data, errors = PydanticValidator.django_form_to_pydantic(form, schema)
                
                if not is_valid:
                    # Add Pydantic errors to form
                    for error in errors:
                        form.add_error(error.field, error.message)
                
                return view_func(request, form, validated_data if is_valid else None, *args, **kwargs)
            else:
                form = form_class()
                return view_func(request, form, None, *args, **kwargs)
        
        return wrapper
    return decorator


def convert_django_model_to_pydantic(django_instance, schema: Type[BaseModel]) -> BaseModel:
    """
    Convert Django model instance to Pydantic model
    
    Args:
        django_instance: Django model instance
        schema: Pydantic model class
        
    Returns:
        Pydantic model instance
    """
    data = {}
    for field in schema.model_fields:
        if hasattr(django_instance, field):
            value = getattr(django_instance, field)
            # Handle special cases like UUIDs, dates, etc.
            if hasattr(value, 'isoformat'):  # datetime/date objects
                value = value.isoformat()
            elif hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool)):
                value = str(value)
            data[field] = value
    
    return schema(**data)


def create_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> JsonResponse:
    """Create a successful JSON response"""
    response = SuccessResponse(
        message=message,
        data=data or {}
    )
    return JsonResponse(response.model_dump())


def create_error_response(
    error: str, 
    status: int = 400, 
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> JsonResponse:
    """Create an error JSON response"""
    response = ErrorResponse(
        error=error,
        error_code=error_code,
        details=details
    )
    return JsonResponse(response.model_dump(), status=status)


class PydanticFormMixin:
    """
    Mixin for Django forms to add Pydantic validation
    
    Usage:
        class UserForm(PydanticFormMixin, forms.Form):
            pydantic_schema = UserRegistrationSchema
            
            # ... form fields ...
    """
    pydantic_schema: Optional[Type[BaseModel]] = None
    
    def clean(self):
        """Add Pydantic validation to Django form clean method"""
        cleaned_data = super().clean()
        
        if self.pydantic_schema and not self.errors:
            is_valid, validated_data, errors = PydanticValidator.validate_data(
                self.pydantic_schema, 
                cleaned_data
            )
            
            if not is_valid:
                for error in errors:
                    self.add_error(error.field, error.message)
            else:
                # Store validated Pydantic model for later use
                self._pydantic_data = validated_data
        
        return cleaned_data
    
    def get_pydantic_data(self) -> Optional[BaseModel]:
        """Get the validated Pydantic model instance"""
        return getattr(self, '_pydantic_data', None)


def validate_file_upload(file, max_size: int = 10485760, allowed_types: Optional[List[str]] = None):
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file object
        max_size: Maximum file size in bytes (default 10MB)
        allowed_types: List of allowed content types
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if not file:
        errors.append(ValidationError(
            field='file',
            message='No file provided',
            value=None
        ))
        return errors
    
    # Check file size
    if file.size > max_size:
        errors.append(ValidationError(
            field='file',
            message=f'File size ({file.size} bytes) exceeds maximum allowed size ({max_size} bytes)',
            value=file.size
        ))
    
    # Check content type
    if allowed_types and file.content_type not in allowed_types:
        errors.append(ValidationError(
            field='file',
            message=f'File type {file.content_type} not allowed. Allowed types: {", ".join(allowed_types)}',
            value=file.content_type
        ))
    
    return errors


def get_validation_errors_from_exception(e: PydanticValidationError) -> List[ValidationError]:
    """Convert Pydantic validation errors to our format"""
    errors = []
    for error in e.errors():
        field_path = '.'.join(str(loc) for loc in error['loc'])
        errors.append(ValidationError(
            field=field_path,
            message=error['msg'],
            value=error.get('input')
        ))
    return errors


def validate_json_field(value: str, field_name: str = 'data') -> tuple[bool, Any, List[ValidationError]]:
    """Validate JSON field value"""
    if not value:
        return True, None, []
    
    try:
        parsed_data = json.loads(value)
        return True, parsed_data, []
    except json.JSONDecodeError as e:
        errors = [ValidationError(
            field=field_name,
            message=f"Invalid JSON format: {str(e)}",
            value=value
        )]
        return False, None, errors 