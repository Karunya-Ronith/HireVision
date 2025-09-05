@echo off
echo Starting HireVision Django Server for LAN Access
echo ================================================
echo.
echo Make sure you have:
echo 1. Activated your virtual environment (if using one)
echo 2. Installed all requirements (pip install -r requirements.txt)
echo 3. Applied database migrations (python manage.py migrate)
echo.
pause
echo.
python start_lan_server.py
pause
