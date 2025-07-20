# HireVision 🚀

**Your AI-Powered Career Success Platform**

HireVision is a comprehensive Django-based web application that leverages artificial intelligence to help users optimize their career development through resume analysis, personalized learning paths, and professional resume building.

![HireVision](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)
![Dramatiq](https://img.shields.io/badge/Dramatiq-Async-red.svg)
![Redis](https://img.shields.io/badge/Redis-Queue-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Quick Start

Get HireVision running with async processing in 3 steps:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database  
python manage.py migrate

# 3. Run all services (requires 3 terminals)
# Terminal 1: Redis
redis-server

# Terminal 2: Worker  
python -m dramatiq hirevision.tasks

# Terminal 3: Django
python manage.py runserver
```

**Then visit**: http://localhost:8000

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
- **Async Processing**: Dramatiq + Redis for background tasks
- **Task Queue**: Redis as message broker
- **PDF Processing**: PyPDF2, ReportLab, LaTeX
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Authentication**: Django's built-in authentication system
- **File Handling**: Django's FileField for resume uploads
- **Real-time Updates**: JavaScript polling with status endpoints

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

### 7. Start Redis Server
Redis is required for the async task queue:

```bash
# On Windows (if Redis is installed)
redis-server

# On macOS (using Homebrew)
brew services start redis

# On Linux (using package manager)
sudo systemctl start redis
```

**Note**: If Redis is not installed, download it from [Redis Downloads](https://redis.io/download) or use Docker:
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 8. Start Dramatiq Worker
In a **new terminal window**, start the background task worker:

```bash
# Navigate to project directory
cd HireVision

# Start the worker
python -m dramatiq hirevision.tasks
```

**Important**: Keep this terminal running - it processes all AI analysis tasks in the background.

### 9. Start Django Development Server
In a **third terminal window**, start the Django server:

```bash
# Navigate to project directory
cd HireVision

# Start Django server
python manage.py runserver
```

### 10. Access the Application
- **Main Application**: http://127.0.0.1:8000/
- **Admin Interface**: http://127.0.0.1:8000/admin/

## ⚡ **NEW: Asynchronous Processing**

HireVision now features **enterprise-grade asynchronous processing** using Dramatiq:

### 🚀 **Benefits:**
- **No More Timeouts**: AI processing happens in the background
- **Better User Experience**: Immediate feedback with loading states
- **Scalable**: Add more workers to handle increased load
- **Reliable**: Built-in retries and error handling

### 🔄 **How It Works:**
1. **Submit Request** → Task queued immediately
2. **Background Worker** → Processes AI analysis asynchronously
3. **Real-time Updates** → Frontend polls for completion every 3 seconds
4. **Automatic Results** → Page refreshes when analysis completes

### 🛠️ **Required Services:**
You need **3 services running** for full functionality:
1. **Redis Server** (Message broker for task queue)
2. **Dramatiq Worker** (Processes background tasks)
3. **Django Server** (Web application)

### 📊 **Task Status Monitoring:**
- **Pending**: Task queued, waiting for worker
- **Running**: AI analysis in progress
- **Completed**: Results ready and displayed
- **Failed**: Error occurred, user notified

### 🎯 **Production Deployment:**
For production, use a process manager like **systemd** or **supervisor** to manage Redis and Dramatiq workers:

```bash
# Example supervisor config for Dramatiq worker
[program:hirevision-worker]
command=python -m dramatiq hirevision.tasks
directory=/path/to/HireVision
user=www-data
autostart=true
autorestart=true
```

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
| `/api/resume-analysis/<id>/status/` | Check resume analysis task status | GET |
| `/api/learning-path/<id>/status/` | Check learning path task status | GET |
| `/api/resume-builder/<id>/status/` | Check resume builder task status | GET |

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
- **Task tracking fields** (task_id, task_status, task_error)

### LearningPath Model
- Personalized learning roadmaps
- Skills gap identification
- Timeline and success metrics
- Career advice and networking tips
- **Async processing support** with status tracking

### ResumeBuilder Model
- Resume data storage
- LaTeX content generation
- PDF file management
- Multiple section support
- **Background processing** for LaTeX compilation

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

### Async Processing Issues

**Tasks stuck in "pending" status:**
- Check if Redis server is running: `redis-cli ping`
- Verify Dramatiq worker is active: `python -m dramatiq hirevision.tasks`
- Check Redis connection in Django settings

**Dramatiq worker errors:**
- Ensure `DJANGO_SETTINGS_MODULE` is set: `export DJANGO_SETTINGS_MODULE=hirevision_django.settings`
- Check Redis connectivity: `python -c "import redis; redis.Redis().ping()"`
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Tasks failing with errors:**
- Check Dramatiq worker logs for detailed error messages
- Verify OpenAI API key is configured correctly
- Ensure file permissions for media uploads are correct

**Redis connection issues:**
- Install Redis if not available: Visit [Redis Downloads](https://redis.io/download)
- Check if Redis is running on default port 6379
- Use Docker as alternative: `docker run -d -p 6379:6379 redis:alpine`

**Frontend not updating:**
- Check browser console for JavaScript errors
- Verify status API endpoints are accessible
- Clear browser cache and reload page

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
- **v1.4.0** - **🚀 MAJOR UPDATE**: Added asynchronous processing with Dramatiq
  - Enterprise-grade async task processing
  - Real-time status updates and loading states
  - Background AI analysis with Redis message broker
  - Improved scalability and user experience
  - No more timeout errors during long operations

---

**Made with ❤️ by the HireVision Team**

*Empowering careers through AI-driven insights and professional development tools.* 