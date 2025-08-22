from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User, Thread, Comment, Message, Conversation
import time
import json
from logging_config import get_logger, log_function_call, log_performance

# Initialize logger for forms
logger = get_logger('forms')

class UserSignUpForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        }),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    @log_function_call
    def clean_email(self):
        start_time = time.time()
        email = self.cleaned_data.get('email')
        logger.info(f"Validating email: {email}")
        
        if User.objects.filter(email=email).exists():
            logger.warning(f"Email already registered: {email}")
            raise forms.ValidationError("This email is already registered.")
        
        duration = time.time() - start_time
        log_performance("Email validation", duration, f"Email: {email}")
        logger.info(f"Email validation successful: {email}")
        return email

class UserLoginForm(AuthenticationForm):
    """Form for user login"""
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your password'
        })
    )
    
    @log_function_call
    def clean(self):
        start_time = time.time()
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        logger.info(f"Validating login credentials for email: {email}")
        
        if email and password:
            # Try to authenticate with email
            user = authenticate(username=email, password=password)
            if user is None:
                logger.warning(f"Invalid login attempt for email: {email}")
                raise forms.ValidationError("Invalid email or password.")
            self.user_cache = user
            logger.info(f"Login validation successful for user: {email}")
        else:
            logger.warning("Login validation failed: missing email or password")
        
        duration = time.time() - start_time
        log_performance("Login validation", duration, f"Email: {email}")
        return self.cleaned_data

class ResumeAnalysisForm(forms.ModelForm):
    """Form for resume analysis"""
    
    class Meta:
        model = ResumeAnalysis
        fields = ['resume_file', 'job_description']
        exclude = ['user']  # User will be set automatically
        widgets = {
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Paste the job description here...'
            })
        }
    
    @log_function_call
    def clean_resume_file(self):
        start_time = time.time()
        file = self.cleaned_data.get('resume_file')
        
        if file:
            logger.info(f"Validating resume file: {file.name}, size: {file.size} bytes")
            
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                logger.warning(f"Resume file too large: {file.name}, size: {file.size} bytes")
                raise forms.ValidationError("File size must be under 5MB.")
            
            # Check file extension
            if not file.name.lower().endswith('.pdf'):
                logger.warning(f"Invalid file extension for resume: {file.name}")
                raise forms.ValidationError("Only PDF files are allowed.")
            
            logger.info(f"Resume file validation successful: {file.name}")
        else:
            logger.warning("No resume file provided")
        
        duration = time.time() - start_time
        log_performance("Resume file validation", duration, f"File: {file.name if file else 'None'}")
        return file

class LearningPathForm(forms.ModelForm):
    """Form for learning path analysis"""
    
    class Meta:
        model = LearningPath
        fields = ['current_skills', 'dream_role']
        exclude = ['user']  # User will be set automatically
        widgets = {
            'current_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe your current skills, experience, and background...'
            }),
            'dream_role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer, Data Scientist, Product Manager'
            })
        }
    
    @log_function_call
    def clean(self):
        start_time = time.time()
        cleaned_data = super().clean()
        current_skills = cleaned_data.get('current_skills')
        dream_role = cleaned_data.get('dream_role')
        
        logger.info(f"Validating learning path form - Dream role: {dream_role}")
        logger.debug(f"Current skills length: {len(current_skills) if current_skills else 0} characters")
        
        if not current_skills or len(current_skills.strip()) < 10:
            logger.warning("Learning path validation failed: insufficient current skills description")
            raise forms.ValidationError("Please provide a detailed description of your current skills.")
        
        if not dream_role or len(dream_role.strip()) < 3:
            logger.warning("Learning path validation failed: insufficient dream role description")
            raise forms.ValidationError("Please provide a valid dream role.")
        
        duration = time.time() - start_time
        log_performance("Learning path form validation", duration, f"Dream role: {dream_role}")
        logger.info(f"Learning path form validation successful")
        return cleaned_data

class ResumeBuilderForm(forms.ModelForm):
    """Form for resume builder"""
    
    class Meta:
        model = ResumeBuilder
        fields = [
            'name', 'email', 'phone', 'linkedin', 'github',
            'education', 'experience', 'projects', 'skills',
            'research_papers', 'achievements', 'others'
        ]
        exclude = ['user']  # User will be set automatically
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'github': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/yourusername'
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your education details in JSON format...'
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter your work experience in JSON format...'
            }),
            'projects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter your projects in JSON format...'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your skills in JSON format...'
            }),
            'research_papers': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your research papers in JSON format...'
            }),
            'achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your achievements (one per line)...'
            }),
            'others': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any other relevant information...'
            })
        }
    
    @log_function_call
    def clean_education(self):
        start_time = time.time()
        education = self.cleaned_data.get('education')
        logger.info("Validating education JSON format")
        
        try:
            if education:
                # Try to parse as JSON, if it's a string
                if isinstance(education, str):
                    json.loads(education)
                    logger.info("Education JSON validation successful")
        except json.JSONDecodeError as e:
            logger.error(f"Education JSON validation failed: {str(e)}")
            raise forms.ValidationError("Education must be in valid JSON format.")
        
        duration = time.time() - start_time
        log_performance("Education JSON validation", duration)
        return education
    
    @log_function_call
    def clean_experience(self):
        start_time = time.time()
        experience = self.cleaned_data.get('experience')
        logger.info("Validating experience JSON format")
        
        try:
            if experience:
                if isinstance(experience, str):
                    json.loads(experience)
                    logger.info("Experience JSON validation successful")
        except json.JSONDecodeError as e:
            logger.error(f"Experience JSON validation failed: {str(e)}")
            raise forms.ValidationError("Experience must be in valid JSON format.")
        
        duration = time.time() - start_time
        log_performance("Experience JSON validation", duration)
        return experience
    
    @log_function_call
    def clean_projects(self):
        start_time = time.time()
        projects = self.cleaned_data.get('projects')
        logger.info("Validating projects JSON format")
        
        try:
            if projects:
                if isinstance(projects, str):
                    json.loads(projects)
                    logger.info("Projects JSON validation successful")
        except json.JSONDecodeError as e:
            logger.error(f"Projects JSON validation failed: {str(e)}")
            raise forms.ValidationError("Projects must be in valid JSON format.")
        
        duration = time.time() - start_time
        log_performance("Projects JSON validation", duration)
        return projects
    
    @log_function_call
    def clean_skills(self):
        start_time = time.time()
        skills = self.cleaned_data.get('skills')
        logger.info("Validating skills JSON format")
        
        try:
            if skills:
                if isinstance(skills, str):
                    json.loads(skills)
                    logger.info("Skills JSON validation successful")
        except json.JSONDecodeError as e:
            logger.error(f"Skills JSON validation failed: {str(e)}")
            raise forms.ValidationError("Skills must be in valid JSON format.")
        
        duration = time.time() - start_time
        log_performance("Skills JSON validation", duration)
        return skills

class ThreadForm(forms.ModelForm):
    """Form for creating and editing threads"""
    
    class Meta:
        model = Thread
        fields = ['title', 'content', 'image', 'article_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter thread title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share your thoughts, questions, or insights...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'article_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/article (optional)'
            })
        }
    
    @log_function_call
    def clean_image(self):
        start_time = time.time()
        image = self.cleaned_data.get('image')
        
        if image:
            logger.info(f"Validating thread image: {image.name}, size: {image.size} bytes")
            
            # Check file size (10MB limit)
            if image.size > 10 * 1024 * 1024:
                logger.warning(f"Thread image too large: {image.name}, size: {image.size} bytes")
                raise forms.ValidationError("Image size must be under 10MB.")
            
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = image.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                logger.warning(f"Invalid file extension for thread image: {image.name}")
                raise forms.ValidationError("Only JPG, PNG, GIF, and WebP images are allowed.")
            
            logger.info(f"Thread image validation successful: {image.name}")
        else:
            logger.debug("No thread image provided")
        
        duration = time.time() - start_time
        log_performance("Thread image validation", duration, f"Image: {image.name if image else 'None'}")
        return image
    
    @log_function_call
    def clean(self):
        start_time = time.time()
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        
        logger.info(f"Validating thread form - Title: {title}")
        logger.debug(f"Content length: {len(content) if content else 0} characters")
        
        if not title or len(title.strip()) < 3:
            logger.warning("Thread validation failed: insufficient title")
            raise forms.ValidationError("Please provide a valid thread title.")
        
        if not content or len(content.strip()) < 10:
            logger.warning("Thread validation failed: insufficient content")
            raise forms.ValidationError("Please provide meaningful content for your thread.")
        
        duration = time.time() - start_time
        log_performance("Thread form validation", duration, f"Title: {title}")
        logger.info(f"Thread form validation successful")
        return cleaned_data

class CommentForm(forms.ModelForm):
    """Form for creating and editing comments"""
    
    class Meta:
        model = Comment
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    @log_function_call
    def clean_image(self):
        start_time = time.time()
        image = self.cleaned_data.get('image')
        
        if image:
            logger.info(f"Validating comment image: {image.name}, size: {image.size} bytes")
            
            # Check file size (5MB limit for comments)
            if image.size > 5 * 1024 * 1024:
                logger.warning(f"Comment image too large: {image.name}, size: {image.size} bytes")
                raise forms.ValidationError("Image size must be under 5MB.")
            
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = image.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                logger.warning(f"Invalid file extension for comment image: {image.name}")
                raise forms.ValidationError("Only JPG, PNG, GIF, and WebP images are allowed.")
            
            logger.info(f"Comment image validation successful: {image.name}")
        else:
            logger.debug("No comment image provided")
        
        duration = time.time() - start_time
        log_performance("Comment image validation", duration, f"Image: {image.name if image else 'None'}")
        return image
    
    @log_function_call
    def clean(self):
        start_time = time.time()
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        
        logger.info("Validating comment form")
        logger.debug(f"Content length: {len(content) if content else 0} characters")
        
        if not content or len(content.strip()) < 1:
            logger.warning("Comment validation failed: empty content")
            raise forms.ValidationError("Please provide content for your comment.")
        
        duration = time.time() - start_time
        log_performance("Comment form validation", duration)
        logger.info(f"Comment form validation successful")
        return cleaned_data

class MessageForm(forms.ModelForm):
    """Form for sending messages"""
    
    class Meta:
        model = Message
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    @log_function_call
    def clean_image(self):
        start_time = time.time()
        image = self.cleaned_data.get('image')
        
        if image:
            logger.info(f"Validating message image: {image.name}, size: {image.size} bytes")
            
            # Check file size (5MB limit for messages)
            if image.size > 5 * 1024 * 1024:
                logger.warning(f"Message image too large: {image.name}, size: {image.size} bytes")
                raise forms.ValidationError("Image size must be under 5MB.")
            
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = image.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                logger.warning(f"Invalid file extension for message image: {image.name}")
                raise forms.ValidationError("Only JPG, PNG, GIF, and WebP images are allowed.")
            
            logger.info(f"Message image validation successful: {image.name}")
        else:
            logger.debug("No message image provided")
        
        duration = time.time() - start_time
        log_performance("Message image validation", duration, f"Image: {image.name if image else 'None'}")
        return image
    
    @log_function_call
    def clean(self):
        start_time = time.time()
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        
        logger.info("Validating message form")
        logger.debug(f"Content length: {len(content) if content else 0} characters")
        
        if not content or len(content.strip()) < 1:
            logger.warning("Message validation failed: empty content")
            raise forms.ValidationError("Please provide content for your message.")
        
        duration = time.time() - start_time
        log_performance("Message form validation", duration)
        logger.info(f"Message form validation successful")
        return cleaned_data

class UserSearchForm(forms.Form):
    """Form for searching users to message"""
    search_query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by username or full name...',
            'id': 'user-search-input'
        })
    )
    
    @log_function_call
    def clean_search_query(self):
        start_time = time.time()
        search_query = self.cleaned_data.get('search_query')
        
        logger.info(f"Validating user search query: {search_query}")
        
        if not search_query or len(search_query.strip()) < 2:
            logger.warning("User search validation failed: query too short")
            raise forms.ValidationError("Search query must be at least 2 characters long.")
        
        duration = time.time() - start_time
        log_performance("User search validation", duration, f"Query: {search_query}")
        logger.info(f"User search validation successful")
        return search_query.strip() 