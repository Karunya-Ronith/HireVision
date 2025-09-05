#!/usr/bin/env python3
"""
Script to start Django development server for LAN access
"""
import os
import sys
import subprocess
import socket

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "192.168.1.7"  # Fallback to detected IP

def main():
    print("🚀 Starting HireVision Django Server for LAN Access")
    print("=" * 50)
    
    local_ip = get_local_ip()
    port = 8000
    
    print(f"📍 Local IP Address: {local_ip}")
    print(f"🌐 Port: {port}")
    print(f"🔗 Local Access: http://localhost:{port}/")
    print(f"🔗 LAN Access: http://{local_ip}:{port}/")
    print("=" * 50)
    
    print("\n📱 Other devices on your network can access the app at:")
    print(f"   http://{local_ip}:{port}/")
    print("\n🔥 Make sure Windows Firewall allows Python through!")
    print("   If you have issues, temporarily disable Windows Firewall or")
    print("   add an exception for Python/Django.")
    print("\n" + "=" * 50)
    
    # Run the Django development server
    try:
        subprocess.run([
            sys.executable, 
            "manage.py", 
            "runserver", 
            f"0.0.0.0:{port}"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
