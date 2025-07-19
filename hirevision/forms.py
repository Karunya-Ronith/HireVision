from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import ResumeAnalysis, LearningPath, ResumeBuilder, User

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
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
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
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            # Try to authenticate with email
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive.")
        
        return self.cleaned_data

class ResumeAnalysisForm(forms.ModelForm):
    """Form for resume analysis"""
    class Meta:
        model = ResumeAnalysis
        fields = ['resume_file', 'job_description']
        exclude = ['user']  # User will be set automatically
        widgets = {
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Paste the job description here...'
            }),
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.doc'
            })
        }
    
    def clean_resume_file(self):
        file = self.cleaned_data.get('resume_file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.docx', '.doc']
            file_extension = file.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Please upload a PDF, DOCX, or DOC file.")
        
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
                'placeholder': 'e.g., Senior Software Engineer, Data Scientist, Product Manager...'
            })
        }

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
    
    def clean_education(self):
        education = self.cleaned_data.get('education')
        try:
            if education:
                # Try to parse as JSON, if it's a string
                if isinstance(education, str):
                    import json
                    json.loads(education)
        except json.JSONDecodeError:
            raise forms.ValidationError("Education must be in valid JSON format.")
        return education
    
    def clean_experience(self):
        experience = self.cleaned_data.get('experience')
        try:
            if experience:
                if isinstance(experience, str):
                    import json
                    json.loads(experience)
        except json.JSONDecodeError:
            raise forms.ValidationError("Experience must be in valid JSON format.")
        return experience
    
    def clean_projects(self):
        projects = self.cleaned_data.get('projects')
        try:
            if projects:
                if isinstance(projects, str):
                    import json
                    json.loads(projects)
        except json.JSONDecodeError:
            raise forms.ValidationError("Projects must be in valid JSON format.")
        return projects
    
    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        try:
            if skills:
                if isinstance(skills, str):
                    import json
                    json.loads(skills)
        except json.JSONDecodeError:
            raise forms.ValidationError("Skills must be in valid JSON format.")
        return skills 