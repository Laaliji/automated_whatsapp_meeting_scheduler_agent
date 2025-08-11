#!/usr/bin/env python3
"""
Setup script for WhatsApp RAG Scheduler
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 Setting up WhatsApp RAG Scheduler...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Create virtual environment
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies"):
        sys.exit(1)
    
    # Copy .env.example to .env if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("copy .env.example .env" if os.name == 'nt' else "cp .env.example .env", "Creating .env file")
            print("📝 Please edit .env file with your API keys and configuration")
        else:
            print("⚠️  .env.example not found")
    
    # Create database
    if not run_command(f"{pip_cmd} install alembic", "Installing Alembic"):
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Set up Qdrant vector database:")
    print("   docker run -p 6333:6333 qdrant/qdrant")
    print("3. Activate virtual environment and run the application:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
        print("   uvicorn app.main:app --reload")
    else:  # Unix/Linux/MacOS
        print("   source venv/bin/activate")
        print("   uvicorn app.main:app --reload")
    print("4. Set up Twilio webhook to point to your /api/v1/webhook/whatsapp endpoint")
    print("\n🔗 Authentication URLs:")
    print("- Google Calendar: http://localhost:8000/api/v1/auth/google?phone=YOUR_PHONE")
    print("- Todoist: http://localhost:8000/api/v1/auth/todoist?phone=YOUR_PHONE")

if __name__ == "__main__":
    main()