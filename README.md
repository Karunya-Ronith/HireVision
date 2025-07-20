# HireVision 🚀

**Your AI-Powered Career Success Platform**

HireVision is a comprehensive Django-based web application that leverages artificial intelligence to help users optimize their career development through resume analysis, personalized learning paths, and professional resume building.

![HireVision](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 📄 **Resume ATS Analyzer**
- **AI-powered resume analysis** with ATS (Applicant Tracking System) scoring
- **Comprehensive evaluation** (0-100 score) with detailed explanations
- **Strengths & Weaknesses analysis** to identify areas for improvement
- **Skills Gap Analysis** comparing your resume to job requirements
- **Upskilling Recommendations** with actionable suggestions
- **Support for multiple formats**: PDF, DOCX, DOC

### 🎯 **Learning Path Analyzer**
- **Personalized learning roadmaps** based on your current skills and dream role
- **Step-by-step learning plans** with curated resources and courses
- **Hands-on project suggestions** for portfolio building
- **Timeline estimation** with realistic milestones
- **Success metrics** to track your progress
- **Career advice and networking tips**

### 📝 **Resume Builder**
- **Professional LaTeX resume generation** with ATS-optimized formatting
- **Customizable sections**: Education, Experience, Projects, Skills, Achievements
- **Multiple template options** for different industries
- **Easy PDF export** with high-quality output
- **Real-time preview** of your resume
- **Professional formatting** that passes ATS systems

### 👤 **User Management**
- **Secure user authentication** with email-based login
- **Profile management** with customizable user profiles
- **Resume history** to track all your analyses and builds
- **Learning path tracking** to monitor your career development progress

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Integration**: OpenAI GPT-4 API
- **PDF Processing**: PyPDF2, ReportLab
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Authentication**: Django's built-in authentication system
- **File Handling**: Django's FileField for resume uploads

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git
- OpenAI API key (for AI features)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd HireVision
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root directory:
```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Django Configuration
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

**Note**: Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
python manage.py runserver
```

### 8. Access the Application
- **Main Application**: http://127.0.0.1:8000/
- **Admin Interface**: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
HireVision/
├── hirevision_django/          # Django project settings
│   ├── __init__.py
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── hirevision/                 # Main Django app
│   ├── __init__.py
│   ├── models.py              # Database models
│   ├── views.py               # View functions and logic
│   ├── forms.py               # Django forms
│   ├── urls.py                # App-specific URL routing
│   ├── admin.py               # Admin interface configuration
│   └── migrations/            # Database migrations
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   └── hirevision/            # App-specific templates
│       ├── home.html          # Home page
│       ├── dashboard.html     # User dashboard
│       ├── resume_analyzer.html
│       ├── learning_path_analyzer.html
│       ├── resume_builder.html
│       └── ...                # Other templates
├── media/                      # Uploaded files
│   ├── resumes/               # Uploaded resumes
│   └── generated_resumes/     # Generated PDFs
├── static/                     # Static files (CSS, JS, images)
├── resume_analyzer.py          # Resume analysis logic
├── learning_path_analyzer.py   # Learning path logic
├── resume_builder.py           # Resume building logic
├── pdf_generator.py            # PDF generation utilities
├── utils.py                    # Utility functions
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
└── README.md                   # This file
```

## 🎯 Usage Guide

### Resume Analysis
1. Navigate to **"Resume Analyzer"** from the main menu
2. Upload your resume file (PDF, DOCX, or DOC format)
3. Paste the job description you're targeting
4. Click **"Analyze Resume"** to get AI-powered insights
5. Review your ATS score, strengths, weaknesses, and recommendations

### Learning Path Analysis
1. Navigate to **"Learning Path Analyzer"**
2. Describe your current skills, experience, and background
3. Specify your dream role or target position
4. Click **"Generate Learning Path"** to get a personalized roadmap
5. Follow the step-by-step plan with curated resources and projects

### Resume Building
1. Navigate to **"Resume Builder"**
2. Fill in your personal information (name, contact details, etc.)
3. Add your education history, work experience, and projects
4. Include your skills, achievements, and any additional sections
5. Click **"Generate Resume"** to create a professional LaTeX resume
6. Download the generated PDF for your job applications

## 🔧 Configuration

### OpenAI API Setup
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Add the key to your `.env` file: `OPENAI_API_KEY=your_key_here`

### Django Settings
Key settings in `hirevision_django/settings.py`:
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Change in production for security
- `ALLOWED_HOSTS`: Add your domain in production
- `MEDIA_ROOT`: Directory for uploaded files
- `STATIC_ROOT`: Directory for static files

## 🚀 Production Deployment

### 1. Production Settings
Update `hirevision_django/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = 'your-secure-secret-key'
```

### 2. Database Setup
For production, use PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Static Files
```bash
python manage.py collectstatic
```

### 4. Web Server Setup
Recommended: Nginx + Gunicorn
```bash
pip install gunicorn
gunicorn hirevision_django.wsgi:application
```

## 📊 API Endpoints

| Endpoint | Description | Method |
|----------|-------------|--------|
| `/` | Home page | GET |
| `/signup/` | User registration | GET, POST |
| `/login/` | User login | GET, POST |
| `/logout/` | User logout | GET |
| `/dashboard/` | User dashboard | GET |
| `/resume-analyzer/` | Resume analysis form | GET, POST |
| `/resume-analysis/<id>/` | Analysis results | GET |
| `/learning-path/` | Learning path form | GET, POST |
| `/learning-path/<id>/` | Learning path results | GET |
| `/resume-builder/` | Resume builder form | GET, POST |
| `/resume-builder/<id>/` | Resume builder results | GET |
| `/download-pdf/<id>/` | Download generated PDF | GET |
| `/admin/` | Django admin interface | GET |

## 🗄️ Database Models

### User Model
- Custom user model with email-based authentication
- Profile information (phone, bio, social links)
- Verification status and timestamps

### ResumeAnalysis Model
- Stores resume analysis results
- ATS scores and explanations
- Strengths, weaknesses, and recommendations
- Skills gap analysis

### LearningPath Model
- Personalized learning roadmaps
- Skills gap identification
- Timeline and success metrics
- Career advice and networking tips

### ResumeBuilder Model
- Resume data storage
- LaTeX content generation
- PDF file management
- Multiple section support

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and add tests if applicable
4. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
5. **Push to the branch**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update documentation for new features
- Test your changes thoroughly

## 🐛 Troubleshooting

### Common Issues

**"Analysis failed" errors:**
- Check your OpenAI API key in `.env` file
- Ensure you have sufficient API credits
- Verify the API key is correct and active

**File upload issues:**
- Check file size limits in Django settings
- Ensure proper file permissions on media directory
- Verify supported file formats

**Database errors:**
- Run `python manage.py migrate` to apply migrations
- Check database connection settings
- Verify database file permissions

**Static files not loading:**
- Run `python manage.py collectstatic`
- Check `STATIC_URL` and `STATIC_ROOT` settings
- Verify web server configuration

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT-4 API
- **Django** community for the excellent web framework
- **Bootstrap** for the responsive UI components
- **LaTeX** community for document formatting capabilities

## 📞 Support

- **Documentation**: Check the inline code comments and docstrings
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join our community discussions
- **Email**: Contact us at support@hirevision.com

## 🔄 Version History

- **v1.0.0** - Initial release with core features
- **v1.1.0** - Added user authentication and profiles
- **v1.2.0** - Enhanced AI analysis capabilities
- **v1.3.0** - Improved resume builder with LaTeX support

---

**Made with ❤️ by the HireVision Team**

*Empowering careers through AI-driven insights and professional development tools.* 