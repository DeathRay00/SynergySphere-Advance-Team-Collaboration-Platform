#!/usr/bin/env python3
"""
Startup script for the SynergySphere backend
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Starting SynergySphere Backend...")
    print("📍 Backend directory:", backend_dir)
    
    # Check if database exists, if not initialize it
    db_path = backend_dir / "app.db"
    if not db_path.exists():
        print("📊 Initializing database...")
        try:
            subprocess.run([sys.executable, "init_db.py"], check=True)
            print("✅ Database initialized successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing database: {e}")
            return
    
    # Start the server
    print("🌐 Starting FastAPI server...")
    print("🔗 Backend will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
