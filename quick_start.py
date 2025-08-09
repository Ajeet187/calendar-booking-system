#!/usr/bin/env python3
"""
Quick Start Script for Calendar Booking System
This script helps you get the application running quickly.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Python 3.8+ is required")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def main():
    """Main quick start function"""
    print("Calendar Booking System")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\activate"
        pip_cmd = ".venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source .venv/bin/activate"
        pip_cmd = ".venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Test import
    print("Testing application import...")
    try:
        from app.main import app
        print("Application imports successfully")
    except ImportError as e:
        print(f"Application import failed: {e}")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
    
    print("Setup completed successfully!\n")

    print("Next steps:")
    print("1. Start the server:")
    print("   uvicorn app.main:app --reload")
    print("\n2. Open your browser to:")
    print("   http://localhost:8000")
    print("\n3. Run tests:")
    print("   pytest tests/ -v")


if __name__ == "__main__":
    main()
