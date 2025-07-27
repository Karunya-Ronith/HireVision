# 🚀 HireVision Windows Setup Guide

**Quick reference for getting HireVision running on Windows with WSL Redis**

## Prerequisites
- Python 3.8+ installed on Windows
- WSL with Redis installed
- OpenAI API key
- Git

## 📋 One-Time Setup

### 1. Clone and Setup Project
```bash
# In Windows PowerShell/Command Prompt
git clone <repository-url>
cd HireVision
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create Environment File
Create `.env` file in project root:
```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Django Configuration
SECRET_KEY=django-insecure-6re@kum6gicewy1@bj!@nf+-2-!5cm@8r^-)beuc6xn3wz9907
DEBUG=True

# Redis Configuration (WSL)
REDIS_URL=redis://localhost:6379/0
```

### 3. Initial Database Setup
```bash
# In Windows PowerShell/Command Prompt (with venv activated)
python manage.py migrate
```

## 🚀 Daily Startup Process

**You need 3 terminals running simultaneously:**

### Terminal 1: WSL Redis Server
```bash
# In WSL terminal
redis-server
```
*Keep this terminal open and running*

### Terminal 2: Windows Dramatiq Worker
```bash
# In Windows PowerShell/Command Prompt
cd HireVision
venv\Scripts\activate
python -m dramatiq hirevision.tasks
```
*Keep this terminal open and running*

### Terminal 3: Windows Django Server
```bash
# In Windows PowerShell/Command Prompt
cd HireVision
venv\Scripts\activate
python manage.py runserver
```
*Keep this terminal open and running*

## 🌐 Access Application
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 🔧 Quick Commands Reference

### Start All Services (Copy-Paste Commands)
```bash
# Terminal 1 (WSL): redis-server

# Terminal 2 (Windows): 
cd HireVision && venv\Scripts\activate && python -m dramatiq hirevision.tasks

# Terminal 3 (Windows):
cd HireVision && venv\Scripts\activate && python manage.py runserver
```

### Stop Services
- **Redis**: Ctrl+C in WSL terminal
- **Worker**: Ctrl+C in Windows terminal 2
- **Django**: Ctrl+C in Windows terminal 3

## 🚨 Troubleshooting

### Redis Connection Issues
```bash
# Test Redis in WSL
redis-cli ping
# Should return: PONG
```

### Worker Not Starting
- Ensure Redis is running in WSL
- Check virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements.txt`

### Django Server Issues
- Check if port 8000 is available
- Ensure virtual environment is activated
- Run migrations if needed: `python manage.py migrate`

### File Permission Issues
- Run PowerShell as Administrator if needed
- Check Windows Defender/antivirus isn't blocking

## 📝 Notes
- All 3 services must run simultaneously for full functionality
- Redis runs in WSL, Django and Worker run in Windows
- Keep all terminals open while using the application
- Async processing requires Redis + Worker to function properly

## 🎯 Success Indicators
- Redis: Shows "Ready to accept connections" in WSL
- Worker: Shows "Connected to Redis" and waits for tasks
- Django: Shows "Starting development server at http://127.0.0.1:8000/"

---
**Last Updated**: $(date)
**For**: Windows + WSL Redis Setup 