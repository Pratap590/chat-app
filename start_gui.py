#!/usr/bin/env python3
"""
Startup script for Multi-Agent Chatbot GUI Application
Handles dependency installation and application startup
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Install FastAPI and related packages first
        essential_packages = [
            "fastapi",
            "uvicorn[standard]", 
            "python-multipart",
            "jinja2"
        ]
        
        for package in essential_packages:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Install remaining packages from requirements.txt
        if Path("requirements.txt").exists():
            print("Installing remaining packages from requirements.txt...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("🔍 Checking environment...")
    
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with:")
        print("GOOGLE_API_KEY=your_google_api_key_here")
        print("HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2")
        print("GOOGLE_MODEL=gemini-2.0-flash")
        return False
    
    print("✅ Environment variables configured")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "static",
        "templates", 
        "uploads",
        "downloads",
        "generated_forms"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def check_main_system():
    """Check if main.py system is available"""
    print("🔍 Checking main chatbot system...")
    
    if not Path("main.py").exists():
        print("❌ main.py not found")
        print("Please ensure the main chatbot system is in the same directory")
        return False
    
    try:
        # Try importing main components
        import main
        print("✅ Main chatbot system available")
        return True
    except ImportError as e:
        print(f"❌ Failed to import main system: {e}")
        return False

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting Multi-Agent Chatbot GUI...")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔧 Interactive API: http://localhost:8000/redoc")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main startup function"""
    print("🎨 Multi-Agent Chatbot GUI Startup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return
    
    # Create directories
    create_directories()
    
    # Check main system
    if not check_main_system():
        return
    
    # Check environment (optional for demo)
    if not check_environment():
        print("⚠️  Environment not fully configured, but continuing...")
        print("Some features may not work without proper API keys")
        time.sleep(2)
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()
