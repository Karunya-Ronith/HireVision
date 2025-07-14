# HireVision - Django Version

Your AI-Powered Career Success Platform built with Django.

## Features

### Resume ATS Analyzer
- Upload your resume and get AI-powered analysis
- ATS Score (0-100) evaluation
- Strengths & Weaknesses analysis
- Skills Gap Analysis
- Upskilling Recommendations

### Learning Path Analyzer
- Input current skills and dream role
- Get detailed step-by-step learning plan
- Curated resources and courses
- Hands-on projects for portfolio building
- Timeline and success metrics

### Resume Builder
- Create professional LaTeX resumes
- ATS-optimized formatting
- Customizable sections
- Easy PDF export
- Professional templates

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HireVision
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## Project Structure

```
HireVision/
├── hirevision_django/          # Django project settings
├── hirevision/                 # Main Django app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── forms.py               # Django forms
│   ├── urls.py                # URL routing
│   └── admin.py               # Admin interface
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   └── hirevision/            # App-specific templates
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
└── manage.py                   # Django management script
```

## Usage

### Resume Analysis
1. Navigate to "Resume Analyzer"
2. Upload your resume (PDF, DOCX, DOC)
3. Paste the job description
4. Get AI-powered analysis with ATS score and recommendations

### Learning Path
1. Navigate to "Learning Path Analyzer"
2. Describe your current skills and background
3. Specify your dream role
4. Get a detailed learning roadmap with resources and projects

### Resume Building
1. Navigate to "Resume Builder"
2. Fill in your personal information
3. Add education, experience, projects, and skills
4. Generate professional LaTeX resume and PDF

## Configuration

### OpenAI API Key
To use the AI features, you need an OpenAI API key:
1. Get your API key from https://platform.openai.com/api-keys
2. Add it to your `.env` file: `OPENAI_API_KEY=your_key_here`

### Django Settings
Key settings in `hirevision_django/settings.py`:
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Change in production
- `ALLOWED_HOSTS`: Add your domain in production
- `MEDIA_ROOT`: Directory for uploaded files
- `STATIC_ROOT`: Directory for static files

## Production Deployment

1. **Set up production settings**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'your-secure-secret-key'
   ```

2. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

3. **Set up a production database**
   - PostgreSQL recommended for production
   - Update `DATABASES` setting

4. **Set up a web server**
   - Nginx + Gunicorn recommended
   - Configure static and media file serving

## API Endpoints

The application provides the following main endpoints:

- `/` - Home page
- `/resume-analyzer/` - Resume analysis form
- `/resume-analysis/<id>/` - Analysis results
- `/learning-path/` - Learning path form
- `/learning-path/<id>/` - Learning path results
- `/resume-builder/` - Resume builder form
- `/resume-builder/<id>/` - Resume builder results
- `/sample-resume/` - Sample resume preview
- `/download-pdf/<id>/` - Download generated PDF
- `/admin/` - Django admin interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on the GitHub repository. 