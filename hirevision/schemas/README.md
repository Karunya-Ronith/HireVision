# HireVision Pydantic Validation System

This document explains the comprehensive Pydantic validation system implemented for the HireVision application.

## Overview

The Pydantic validation system provides robust, type-safe validation for all data inputs and outputs in the HireVision application. It replaces and enhances the existing Django form validation with more powerful and flexible validation capabilities.

## Architecture

### Directory Structure

```
hirevision/schemas/
├── __init__.py              # Main exports and schema registry
├── base.py                  # Base schemas and common utilities
├── user.py                  # User-related schemas
├── resume_analysis.py       # Resume analysis schemas
├── learning_path.py         # Learning path schemas
├── resume_builder.py        # Resume builder schemas
├── api_responses.py         # API response schemas
├── integration_examples.py  # Usage examples
└── README.md               # This documentation
```

### Core Components

1. **Base Schemas** (`base.py`): Common validation utilities and base classes
2. **Domain Schemas**: Specific validation for each feature area
3. **API Response Schemas**: Standardized response formats
4. **Integration Utilities** (`validation.py`): Django-Pydantic bridge functions

## Schema Categories

### 1. User Schemas (`user.py`)

- `UserRegistrationSchema`: User registration validation
- `UserLoginSchema`: Login credential validation  
- `UserProfileSchema`: User profile data validation
- `UserUpdateSchema`: Profile update validation
- Password change and reset schemas

### 2. Resume Analysis Schemas (`resume_analysis.py`)

- `ResumeAnalysisInputSchema`: Input validation for resume analysis
- `ResumeAnalysisOutputSchema`: Structured analysis results
- `ResumeFileSchema`: File upload validation
- `SkillGapSchema`: Skill gap analysis structure
- `RecommendationSchema`: Improvement recommendations

### 3. Learning Path Schemas (`learning_path.py`)

- `LearningPathInputSchema`: Learning path request validation
- `LearningPathOutputSchema`: Structured learning roadmap
- `LearningPhaseSchema`: Individual learning phases
- `LearningResourceSchema`: Educational resources
- `SkillAssessmentSchema`: Skill level assessments

### 4. Resume Builder Schemas (`resume_builder.py`)

- `ResumeBuilderInputSchema`: Resume creation input
- `ResumeBuilderOutputSchema`: Generated resume data
- `EducationSchema`: Education entries
- `ExperienceSchema`: Work experience entries
- `ProjectSchema`: Project descriptions
- `SkillsSchema`: Skills categorization

### 5. API Response Schemas (`api_responses.py`)

- `SuccessResponse`: Standard success response
- `ErrorResponse`: Error response with details
- `TaskStatusResponse`: Async task status
- `ValidationResponse`: Validation results
- `ListResponse`: Paginated list responses

## Usage Examples

### 1. Basic Validation

```python
from hirevision.schemas.user import UserRegistrationSchema
from hirevision.validation import PydanticValidator

# Validate user registration data
data = {
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password1": "securepass123",
    "password2": "securepass123"
}

is_valid, validated_data, errors = PydanticValidator.validate_data(
    UserRegistrationSchema, 
    data
)

if is_valid:
    # Use validated_data (Pydantic model instance)
    user = create_user(validated_data)
else:
    # Handle validation errors
    for error in errors:
        print(f"{error.field}: {error.message}")
```

### 2. Decorator-Based Validation

```python
from hirevision.validation import validate_request_data
from hirevision.schemas.resume_analysis import ResumeAnalysisInputSchema

@validate_request_data(ResumeAnalysisInputSchema)
def analyze_resume_api(request, validated_data):
    """API endpoint with automatic validation"""
    # validated_data is already a Pydantic model
    job_description = validated_data.job_description
    
    # Process the analysis
    analysis = process_resume_analysis(validated_data)
    
    return JsonResponse({
        'success': True,
        'data': analysis.model_dump()
    })
```

### 3. Form Integration

```python
from hirevision.validation import PydanticFormMixin
from hirevision.schemas.user import UserRegistrationSchema

class UserRegistrationForm(PydanticFormMixin, forms.Form):
    pydantic_schema = UserRegistrationSchema
    
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    # ... other fields
    
    def clean(self):
        """Combines Django + Pydantic validation"""
        cleaned_data = super().clean()
        
        # Access validated Pydantic data
        pydantic_data = self.get_pydantic_data()
        if pydantic_data:
            # Use for additional business logic
            pass
        
        return cleaned_data
```

### 4. File Upload Validation

```python
from hirevision.validation import validate_file_upload

def upload_resume(request):
    resume_file = request.FILES.get('resume')
    
    # Validate file
    errors = validate_file_upload(
        resume_file,
        max_size=10 * 1024 * 1024,  # 10MB
        allowed_types=['application/pdf', 'application/msword']
    )
    
    if errors:
        return JsonResponse({
            'success': False,
            'errors': [error.model_dump() for error in errors]
        }, status=400)
    
    # Process file
    process_resume_file(resume_file)
```

## Key Features

### 1. Type Safety
- All data is validated against strict type definitions
- Automatic type conversion where appropriate
- Clear error messages for type mismatches

### 2. Comprehensive Validation
- Field-level validation (length, format, etc.)
- Cross-field validation (password confirmation)
- Custom business logic validation
- File upload validation

### 3. Error Handling
- Structured error responses
- Field-specific error messages
- Validation error aggregation
- Consistent error formats

### 4. Django Integration
- Seamless integration with Django forms
- Decorator-based view validation
- Model conversion utilities
- Response helpers

### 5. API Standardization
- Consistent API response formats
- Standardized error structures
- Task status tracking
- Pagination support

## Validation Patterns

### Input Validation Pattern
```python
# 1. Define schema
class MyInputSchema(BaseModel):
    field: str = Field(..., min_length=1, max_length=100)

# 2. Validate in view
is_valid, data, errors = PydanticValidator.validate_data(
    MyInputSchema, 
    request_data
)

# 3. Handle results
if is_valid:
    process_data(data)
else:
    return error_response(errors)
```

### Output Serialization Pattern
```python
# 1. Define output schema
class MyOutputSchema(BaseModel):
    id: UUID
    result: str
    created_at: datetime

# 2. Convert Django model
output_data = convert_django_model_to_pydantic(
    django_instance, 
    MyOutputSchema
)

# 3. Return structured response
return JsonResponse(output_data.model_dump())
```

### Form Enhancement Pattern
```python
# 1. Add Pydantic to Django form
class MyForm(PydanticFormMixin, forms.Form):
    pydantic_schema = MySchema
    # ... Django fields

# 2. Enhanced validation
if form.is_valid():
    pydantic_data = form.get_pydantic_data()
    # Use both Django cleaned_data and Pydantic validation
```

## Benefits

### For Developers
- **Type Safety**: Catch errors at validation time
- **Documentation**: Schemas serve as living documentation
- **Consistency**: Standardized validation across the application
- **Maintainability**: Centralized validation logic

### For Users
- **Better Errors**: Clear, specific error messages
- **Data Integrity**: Robust input validation
- **Consistent Experience**: Standardized response formats
- **Performance**: Efficient validation and serialization

### For APIs
- **Documentation**: Auto-generated API docs from schemas
- **Validation**: Comprehensive input/output validation
- **Standardization**: Consistent response formats
- **Type Hints**: Better IDE support and tooling

## Best Practices

### 1. Schema Design
- Use descriptive field names and descriptions
- Implement appropriate validation constraints
- Group related fields into nested schemas
- Use enums for fixed value sets

### 2. Error Handling
- Provide clear, actionable error messages
- Include field context in error responses
- Use appropriate HTTP status codes
- Log validation errors for debugging

### 3. Performance
- Use Pydantic's efficient validation
- Cache schema instances where possible
- Validate early in the request pipeline
- Use lazy validation for large datasets

### 4. Testing
- Test all validation scenarios
- Include edge cases and boundary conditions
- Test error message quality
- Validate schema changes don't break existing data

## Migration Guide

### From Django Forms Only
1. Create corresponding Pydantic schemas
2. Add PydanticFormMixin to existing forms
3. Update views to use Pydantic validation
4. Test thoroughly with existing data

### Adding to New Features
1. Design Pydantic schemas first
2. Use validation decorators for new views
3. Implement consistent error handling
4. Document schema usage

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all schema files are in the correct location
- Check __init__.py imports are correct
- Verify Pydantic is installed

**Validation Failures**
- Check field types match schema definitions
- Verify required fields are provided
- Review custom validation logic

**Performance Issues**
- Cache Pydantic schema instances
- Use lazy validation for large datasets
- Profile validation performance

### Debugging Tips

1. **Use Pydantic's built-in debugging**:
   ```python
   try:
       validated = MySchema(**data)
   except ValidationError as e:
       print(e.json(indent=2))
   ```

2. **Check schema field definitions**:
   ```python
   print(MySchema.model_fields)
   ```

3. **Validate incrementally**:
   ```python
   # Test each field individually
   for field, value in data.items():
       try:
           MySchema.model_validate({field: value})
       except ValidationError as e:
           print(f"Error in {field}: {e}")
   ```

## Future Enhancements

### Planned Features
- JSON Schema generation for API documentation
- GraphQL integration
- Advanced validation rules
- Performance optimizations
- Additional file format support

### Extension Points
- Custom validators for business logic
- Integration with external validation services
- Advanced error formatting
- Localization support

This Pydantic validation system provides a robust foundation for data validation in the HireVision application, ensuring data integrity, improving developer experience, and providing better user feedback. 