# 🌐 LAN Access Configuration for HireVision

This guide will help you set up HireVision Django app for Local Area Network (LAN) access, allowing other devices on your network to access the application.

## 🔧 Configuration Applied

### 1. Django Settings Updated
- Modified `ALLOWED_HOSTS` in `hirevision_django/settings.py` to include:
  - `localhost` and `127.0.0.1` (local access)
  - `192.168.1.7` (your current IP address)
  - `192.168.1.*` (any device on your local network)
  - `*` (all hosts - development only)

### 2. Server Scripts Created
- `start_lan_server.py` - Python script to start server with proper configuration
- `start_lan_server.bat` - Windows batch file for easy execution

## 🚀 How to Start the Server

### Option 1: Using the Python Script
```bash
python start_lan_server.py
```

### Option 2: Using the Batch File (Windows)
Double-click `start_lan_server.bat` or run:
```cmd
start_lan_server.bat
```

### Option 3: Manual Command
```bash
python manage.py runserver 0.0.0.0:8000
```

## 📱 Accessing from Other Devices

Once the server is running, other devices on your network can access the app at:

**🔗 http://192.168.1.7:8000/**

### From Different Device Types:
- **Mobile Phones**: Open browser, go to `http://192.168.1.7:8000/`
- **Tablets**: Same URL in any browser
- **Other Computers**: Same URL in any browser
- **Smart TVs**: If they have a browser, same URL

## 🛡️ Firewall Configuration

### Windows Firewall
If other devices can't access the app, you may need to:

1. **Temporarily disable Windows Firewall** (easiest for testing):
   - Go to Control Panel > System and Security > Windows Defender Firewall
   - Click "Turn Windows Defender Firewall on or off"
   - Temporarily turn off for Private networks

2. **Or create a firewall rule** (recommended):
   - Go to Windows Defender Firewall > Advanced settings
   - Click "Inbound Rules" > "New Rule"
   - Select "Port" > Next
   - Select "TCP" and enter "8000" > Next
   - Select "Allow the connection" > Next
   - Apply to all profiles > Next
   - Name it "Django HireVision" > Finish

## 🔍 Troubleshooting

### Can't Access from Other Devices?
1. **Check if server is running**: You should see Django's development server output
2. **Verify IP address**: Run `ipconfig` to confirm your IP is still `192.168.1.7`
3. **Test locally first**: Make sure `http://localhost:8000` works
4. **Check firewall**: Temporarily disable Windows Firewall to test
5. **Network connectivity**: Make sure devices are on the same network

### Different IP Address?
If your IP address changes, update the `ALLOWED_HOSTS` in `settings.py`:
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'YOUR_NEW_IP_ADDRESS',  # Update this
    '192.168.1.*',
    '*',
]
```

### Port Already in Use?
If port 8000 is busy, use a different port:
```bash
python manage.py runserver 0.0.0.0:8080
```
Then access via `http://192.168.1.7:8080/`

## ⚠️ Security Notes

**IMPORTANT**: These settings are for development only!

- The `ALLOWED_HOSTS = ['*']` setting allows any host to access your application
- Only use this in a trusted network environment
- For production, always specify exact allowed hosts
- Never deploy to production with `DEBUG = True` and `ALLOWED_HOSTS = ['*']`

## 📋 Quick Checklist

Before starting:
- [ ] Virtual environment activated (if using one)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Windows Firewall configured
- [ ] All devices on same network

## 🎯 Expected Behavior

When everything is working correctly:
1. Server starts and shows: `Starting development server at http://0.0.0.0:8000/`
2. Local access works: `http://localhost:8000/`
3. LAN access works: `http://192.168.1.7:8000/` from other devices
4. All features function normally across devices

## 📞 Need Help?

If you encounter issues:
1. Check the server console for error messages
2. Verify network connectivity between devices
3. Ensure firewall isn't blocking connections
4. Try accessing from the same device first
5. Check if the IP address has changed

Happy coding! 🚀
