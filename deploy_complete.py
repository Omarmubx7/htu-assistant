#!/usr/bin/env python3
"""
Complete Deployment Script for HTU Assistant
Handles the entire deployment process from zero to 100%
"""

import os
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(message, status="INFO"):
    """Print a formatted status message."""
    timestamp = time.strftime("%H:%M:%S")
    if status == "SUCCESS":
        print(f"{Colors.OKGREEN}[{timestamp}] ✅ {message}{Colors.ENDC}")
    elif status == "ERROR":
        print(f"{Colors.FAIL}[{timestamp}] ❌ {message}{Colors.ENDC}")
    elif status == "WARNING":
        print(f"{Colors.WARNING}[{timestamp}] ⚠️ {message}{Colors.ENDC}")
    elif status == "INFO":
        print(f"{Colors.OKBLUE}[{timestamp}] ℹ️ {message}{Colors.ENDC}")
    else:
        print(f"[{timestamp}] {message}")

def check_python_version():
    """Check if Python version is compatible."""
    print_status("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status(f"Python {version.major}.{version.minor} detected. Python 3.8+ required.", "ERROR")
        return False
    print_status(f"Python {version.major}.{version.minor}.{version.micro} - Compatible", "SUCCESS")
    return True

def check_required_files():
    """Check if all required files exist."""
    print_status("Checking required files...")
    required_files = [
        'app.py',
        'requirements.txt',
        'office_hours.json',
        'full_subjects_study_plan.json',
        'static/index.html'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print_status(f"✅ {file}")
        else:
            print_status(f"❌ {file} - MISSING", "ERROR")
            missing_files.append(file)
    
    if missing_files:
        print_status(f"Missing required files: {missing_files}", "ERROR")
        return False
    
    print_status("All required files found!", "SUCCESS")
    return True

def validate_json_files():
    """Validate JSON files are properly formatted."""
    print_status("Validating JSON files...")
    json_files = ['office_hours.json', 'full_subjects_study_plan.json']
    
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                print_status(f"✅ {file} - Valid JSON ({len(data)} items)")
            else:
                print_status(f"✅ {file} - Valid JSON ({len(data.keys())} keys)")
        except json.JSONDecodeError as e:
            print_status(f"❌ {file} - Invalid JSON: {e}", "ERROR")
            return False
        except Exception as e:
            print_status(f"❌ {file} - Error: {e}", "ERROR")
            return False
    
    print_status("All JSON files are valid!", "SUCCESS")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print_status("Installing Python dependencies...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True, check=True)
        print_status("Dependencies installed successfully!", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install dependencies: {e.stderr}", "ERROR")
        return False

def test_flask_app():
    """Test the Flask application."""
    print_status("Testing Flask application...")
    try:
        # Import the app
        import app
        print_status("✅ Flask app imports successfully", "SUCCESS")
        
        # Test data loading
        if hasattr(app, 'subjects_data') and hasattr(app, 'office_hours_data'):
            print_status(f"✅ Data loaded: {len(app.subjects_data)} subjects, {len(app.office_hours_data)} professors", "SUCCESS")
        else:
            print_status("⚠️ Data not loaded properly", "WARNING")
        
        return True
    except Exception as e:
        print_status(f"❌ Flask app test failed: {e}", "ERROR")
        return False

def create_wsgi_file():
    """Create WSGI file for deployment."""
    print_status("Creating WSGI file...")
    wsgi_content = '''import sys
import os

# Add your project directory to the sys.path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
from app import app as application

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
'''
    
    try:
        with open('wsgi.py', 'w') as f:
            f.write(wsgi_content)
        print_status("✅ WSGI file created successfully!", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Failed to create WSGI file: {e}", "ERROR")
        return False

def create_procfile():
    """Create Procfile for Heroku deployment."""
    print_status("Creating Procfile...")
    procfile_content = "web: gunicorn app:app"
    
    try:
        with open('Procfile', 'w') as f:
            f.write(procfile_content)
        print_status("✅ Procfile created successfully!", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Failed to create Procfile: {e}", "ERROR")
        return False

def create_runtime_txt():
    """Create runtime.txt for Python version specification."""
    print_status("Creating runtime.txt...")
    runtime_content = "python-3.9.18"
    
    try:
        with open('runtime.txt', 'w') as f:
            f.write(runtime_content)
        print_status("✅ runtime.txt created successfully!", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Failed to create runtime.txt: {e}", "ERROR")
        return False

def run_local_test():
    """Run a local test of the application."""
    print_status("Starting local test server...")
    print_status("Press Ctrl+C to stop the test server", "INFO")
    
    try:
        # Start the Flask app
        result = subprocess.run([sys.executable, 'app.py'], 
                              capture_output=False, text=True)
        return True
    except KeyboardInterrupt:
        print_status("Test server stopped by user", "INFO")
        return True
    except Exception as e:
        print_status(f"❌ Local test failed: {e}", "ERROR")
        return False

def create_deployment_package():
    """Create a deployment package with all necessary files."""
    print_status("Creating deployment package...")
    
    # Create deployment directory
    deploy_dir = "deployment_package"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Files to include in deployment
    files_to_copy = [
        'app.py',
        'requirements.txt',
        'office_hours.json',
        'full_subjects_study_plan.json',
        'wsgi.py',
        'Procfile',
        'runtime.txt',
        'README.md',
        'PYTHONANYWHERE_DEPLOYMENT.md'
    ]
    
    # Directories to copy
    dirs_to_copy = ['static', 'templates']
    
    try:
        # Copy files
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, deploy_dir)
                print_status(f"✅ Copied {file}")
        
        # Copy directories
        for dir_name in dirs_to_copy:
            if os.path.exists(dir_name):
                shutil.copytree(dir_name, os.path.join(deploy_dir, dir_name))
                print_status(f"✅ Copied {dir_name}/")
        
        print_status(f"✅ Deployment package created in '{deploy_dir}/'", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Failed to create deployment package: {e}", "ERROR")
        return False

def generate_deployment_instructions():
    """Generate deployment instructions."""
    print_status("Generating deployment instructions...")
    
    instructions = """
🚀 HTU Assistant - Deployment Instructions
==========================================

✅ Your application is ready for deployment!

📁 Files Created:
- app.py (Main Flask application)
- requirements.txt (Python dependencies)
- wsgi.py (WSGI configuration)
- Procfile (Heroku configuration)
- runtime.txt (Python version)
- deployment_package/ (Complete deployment folder)

🌐 Deployment Options:

1. PYTHONANYWHERE (Recommended):
   - Follow instructions in PYTHONANYWHERE_DEPLOYMENT.md
   - Upload files from deployment_package/ folder

2. HEROKU:
   - Install Heroku CLI
   - Run: heroku create your-app-name
   - Run: git add . && git commit -m "Deploy"
   - Run: git push heroku main

3. RAILWAY:
   - Connect GitHub repository
   - Railway will auto-detect and deploy

4. VERCEL:
   - Install Vercel CLI
   - Run: vercel
   - Follow prompts

🧪 Testing:
- Run: python test_api.py
- Visit: http://localhost:5000/health
- Test chat functionality

📞 Support:
- Check README.md for detailed instructions
- Create GitHub issue for problems
- Use deployment guides for specific platforms

🎉 Your HTU Assistant is ready to help students!
"""
    
    try:
        with open('DEPLOYMENT_INSTRUCTIONS.txt', 'w') as f:
            f.write(instructions)
        print_status("✅ Deployment instructions saved to DEPLOYMENT_INSTRUCTIONS.txt", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Failed to create instructions: {e}", "ERROR")
        return False

def main():
    """Main deployment function."""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🎓 HTU Assistant - Complete Deployment Script")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    
    # Step 1: Environment Check
    print_status("Step 1: Environment Check", "INFO")
    if not check_python_version():
        return False
    
    # Step 2: File Validation
    print_status("Step 2: File Validation", "INFO")
    if not check_required_files():
        return False
    
    if not validate_json_files():
        return False
    
    # Step 3: Dependencies
    print_status("Step 3: Installing Dependencies", "INFO")
    if not install_dependencies():
        return False
    
    # Step 4: Application Test
    print_status("Step 4: Testing Application", "INFO")
    if not test_flask_app():
        return False
    
    # Step 5: Create Deployment Files
    print_status("Step 5: Creating Deployment Files", "INFO")
    if not create_wsgi_file():
        return False
    
    if not create_procfile():
        return False
    
    if not create_runtime_txt():
        return False
    
    # Step 6: Create Deployment Package
    print_status("Step 6: Creating Deployment Package", "INFO")
    if not create_deployment_package():
        return False
    
    # Step 7: Generate Instructions
    print_status("Step 7: Generating Instructions", "INFO")
    if not generate_deployment_instructions():
        return False
    
    # Success!
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
    print("🎉 DEPLOYMENT PREPARATION COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    
    print_status("Your HTU Assistant is ready for deployment!", "SUCCESS")
    print_status("Check DEPLOYMENT_INSTRUCTIONS.txt for next steps", "INFO")
    print_status("Deployment package is in 'deployment_package/' folder", "INFO")
    
    # Ask if user wants to test locally
    print(f"\n{Colors.OKCYAN}Would you like to test the application locally? (y/n): {Colors.ENDC}")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            print_status("Starting local test server...", "INFO")
            run_local_test()
    except KeyboardInterrupt:
        print_status("Skipping local test", "INFO")
    
    print(f"\n{Colors.OKGREEN}Thank you for using HTU Assistant! 🎓{Colors.ENDC}")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\nDeployment cancelled by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        sys.exit(1) 