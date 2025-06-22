#!/usr/bin/env python3
"""
Deployment script for HTU Assistant
Helps automate the deployment process and fix common access issues
"""

import os
import json
import shutil
import subprocess
import sys

def check_requirements():
    """Check if all required files exist."""
    required_files = [
        'app.py',
        'requirements.txt',
        'office_hours.json',
        'full_subjects_study_plan.json'
    ]
    
    print("🔍 Checking required files...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files found!")
    return True

def check_json_files():
    """Check if JSON files are valid and accessible."""
    json_files = ['office_hours.json', 'full_subjects_study_plan.json']
    
    print("\n🔍 Validating JSON files...")
    
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ {file} - Valid JSON ({len(data) if isinstance(data, list) else len(data.keys())} items)")
        except json.JSONDecodeError as e:
            print(f"❌ {file} - Invalid JSON: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {file} - File not found")
            return False
        except PermissionError:
            print(f"❌ {file} - Permission denied")
            return False
    
    return True

def build_frontend():
    """Build the React frontend."""
    print("\n🔨 Building frontend...")
    
    if not os.path.exists('frontend'):
        print("❌ Frontend directory not found")
        return False
    
    try:
        # Change to frontend directory
        os.chdir('frontend')
        
        # Install dependencies
        print("📦 Installing frontend dependencies...")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm install failed: {result.stderr}")
            return False
        
        # Build the project
        print("🔨 Building React app...")
        result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False
        
        # Copy build files to static directory
        print("📁 Copying build files to static directory...")
        if os.path.exists('dist'):
            if not os.path.exists('../static'):
                os.makedirs('../static')
            
            # Copy all files from dist to static
            for item in os.listdir('dist'):
                src = os.path.join('dist', item)
                dst = os.path.join('../static', item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
            print("✅ Frontend built and copied successfully!")
        else:
            print("❌ Build directory not found")
            return False
        
        # Go back to root directory
        os.chdir('..')
        return True
        
    except Exception as e:
        print(f"❌ Frontend build error: {e}")
        os.chdir('..')  # Make sure we go back to root
        return False

def create_wsgi_file():
    """Create a WSGI file for deployment."""
    print("\n📝 Creating WSGI file...")
    
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
        print("✅ WSgi file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create WSGI file: {e}")
        return False

def check_permissions():
    """Check and fix file permissions."""
    print("\n🔐 Checking file permissions...")
    
    files_to_check = [
        'app.py',
        'office_hours.json',
        'full_subjects_study_plan.json',
        'requirements.txt'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            try:
                # Try to read the file
                with open(file, 'r') as f:
                    f.read(1)
                print(f"✅ {file} - Readable")
            except PermissionError:
                print(f"❌ {file} - Permission denied")
                return False
    
    return True

def main():
    """Main deployment function."""
    print("🚀 HTU Assistant Deployment Script")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Deployment failed: Missing required files")
        sys.exit(1)
    
    # Check JSON files
    if not check_json_files():
        print("\n❌ Deployment failed: JSON validation failed")
        sys.exit(1)
    
    # Check permissions
    if not check_permissions():
        print("\n❌ Deployment failed: Permission issues")
        sys.exit(1)
    
    # Build frontend
    if not build_frontend():
        print("\n❌ Deployment failed: Frontend build failed")
        sys.exit(1)
    
    # Create WSGI file
    if not create_wsgi_file():
        print("\n❌ Deployment failed: WSGI file creation failed")
        sys.exit(1)
    
    print("\n🎉 Deployment preparation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Upload all files to your hosting platform")
    print("2. Install Python dependencies: pip install -r requirements.txt")
    print("3. Configure your web server to use wsgi.py")
    print("4. Set up static file serving for the /static/ directory")
    print("5. Test your deployment at /health endpoint")

if __name__ == "__main__":
    main() 