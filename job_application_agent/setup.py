#!/usr/bin/env python3
"""
Setup script for Job Application Agent
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_chrome():
    """Check if Chrome is installed"""
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print("✅ Chrome/Chromium found")
            return True
    
    # Try which command
    success, _, _ = run_command("which google-chrome")
    if success:
        print("✅ Chrome found via PATH")
        return True
    
    success, _, _ = run_command("which chromium-browser")
    if success:
        print("✅ Chromium found via PATH")
        return True
    
    print("⚠️ Chrome/Chromium not found. Please install Chrome or Chromium browser")
    return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        print(f"Error: {stderr}")
        return False

def setup_env_file():
    """Setup environment file"""
    print("\n🔧 Setting up environment file...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    if env_file.exists():
        overwrite = input("📄 .env file already exists. Overwrite? (y/n): ").lower().startswith('y')
        if not overwrite:
            print("ℹ️ Keeping existing .env file")
            return True
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ .env file created")
        print("⚠️ Please edit .env file with your credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["logs", "data"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def show_configuration_info():
    """Show information about configuration"""
    print("\n" + "="*60)
    print("📋 CONFIGURATION REQUIRED")
    print("="*60)
    print("1. Edit .env file with your credentials:")
    print("   - LinkedIn email and password")
    print("   - Naukri.com email and password")
    print("   - Resume file path")
    print()
    print("2. Edit config/profile_config.py with your details:")
    print("   - Personal information")
    print("   - Target job roles")
    print("   - Preferred locations")
    print("   - Skills and experience")
    print()
    print("3. Make sure your resume is in PDF format and accessible")
    print("="*60)

def run_test():
    """Run a test to check if everything is working"""
    print("\n🧪 Running test...")
    
    success, stdout, stderr = run_command("python main.py --config")
    
    if success:
        print("✅ Basic test passed")
        return True
    else:
        print("❌ Test failed")
        print(f"Error: {stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Job Application Agent Setup")
    print("="*40)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    check_chrome()
    
    # Setup steps
    steps = [
        ("Install dependencies", install_dependencies),
        ("Setup environment file", setup_env_file),
        ("Create directories", create_directories),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Show results
    print("\n" + "="*60)
    print("📊 SETUP SUMMARY")
    print("="*60)
    
    if not failed_steps:
        print("✅ Setup completed successfully!")
        show_configuration_info()
        print("\n🎯 Next steps:")
        print("1. Configure your credentials and profile")
        print("2. Run: python main.py --config (to verify)")
        print("3. Run: python main.py --run-once (test run)")
        print("4. Run: python main.py --start (start scheduler)")
    else:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease fix the errors and run setup again")
    
    print("="*60)

if __name__ == "__main__":
    main()