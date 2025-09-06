#!/usr/bin/env python3
"""
Startup script for the entire SynergySphere application
This script will start both the backend and frontend servers
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def start_backend():
    """Start the backend server"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 Starting Backend Server...")
    try:
        subprocess.run([sys.executable, "start.py"], check=True)
    except KeyboardInterrupt:
        print("🛑 Backend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend: {e}")

def start_frontend():
    """Start the frontend server"""
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    print("🎨 Starting Frontend Server...")
    try:
        # Check if npm is available
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            subprocess.run(["npm", "start"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try yarn if npm is not available
            try:
                subprocess.run(["yarn", "--version"], check=True, capture_output=True)
                subprocess.run(["yarn", "start"], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ Neither npm nor yarn found. Please install Node.js and npm/yarn.")
                return
    except KeyboardInterrupt:
        print("🛑 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")

def main():
    print("🌟 SynergySphere - Project Management Application")
    print("=" * 50)
    print("This script will start both backend and frontend servers")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend in the main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        print("Thank you for using SynergySphere! 👋")

if __name__ == "__main__":
    main()
