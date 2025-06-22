# 🚀 PythonAnywhere Deployment Guide - HTU Assistant

This guide will help you deploy the HTU Assistant to PythonAnywhere and fix access issues.

## 📋 Prerequisites

- PythonAnywhere account (free or paid)
- Git access to your repository

## 🔧 Step 1: Set Up PythonAnywhere

1. **Go to PythonAnywhere.com** and create an account
2. **Log in** to your PythonAnywhere dashboard
3. **Go to "Web" tab** in the top navigation

## 📥 Step 2: Clone Your Repository

1. **Go to "Consoles" tab** and open a **Bash console**
2. **Clone your repository**:
   ```bash
   git clone https://github.com/Omarmubx7/htu-assistant.git
   cd htu-assistant
   ```

## 🐍 Step 3: Set Up Python Environment

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🌐 Step 4: Configure Web App

1. **Go back to "Web" tab**
2. **Click "Add a new web app"**
3. **Choose "Flask"** as the framework
4. **Select Python 3.9** or higher
5. **Set the path to your app**: `/home/YOUR_USERNAME/htu-assistant/app.py`

## ⚙️ Step 5: Configure WSGI File

1. **Click on your web app** in the Web tab
2. **Click "WSGI configuration file"**
3. **Replace the content** with:

```python
import sys
import os

# Add your project directory to the sys.path
path = '/home/YOUR_USERNAME/htu-assistant'
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
from app import app as application

# Optional: Set environment variables
os.environ['FLASK_ENV'] = 'production'
```

**Replace `YOUR_USERNAME` with your actual PythonAnywhere username**

## 🔧 Step 6: Configure Static Files

1. **In the Web tab**, scroll down to "Static files"
2. **Add static file mappings**:
   - **URL**: `/static/`
   - **Directory**: `/home/YOUR_USERNAME/htu-assistant/static/`

## 🚀 Step 7: Deploy Frontend

1. **Build the React frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Copy build files** to static directory:
   ```bash
   cp -r dist/* ../static/
   ```

## 🔄 Step 8: Reload Web App

1. **Go back to "Web" tab**
2. **Click "Reload"** button
3. **Wait for the reload to complete**

## 🧪 Step 9: Test Your Deployment

1. **Visit your site**: `https://YOUR_USERNAME.pythonanywhere.com`
2. **Test the health endpoint**: `https://YOUR_USERNAME.pythonanywhere.com/health`
3. **Test the API**: Send a POST request to `/api/chat`

## 🛠️ Troubleshooting Access Issues

### Issue 1: 404 Errors
- **Check WSGI file path** is correct
- **Verify app.py** is in the right location
- **Check file permissions** on PythonAnywhere

### Issue 2: CORS Errors
- **Verify CORS configuration** in app.py
- **Check allowed origins** include your domain
- **Test with different browsers**

### Issue 3: Import Errors
- **Check virtual environment** is activated
- **Verify all dependencies** are installed
- **Check Python version** compatibility

### Issue 4: File Access Errors
- **Check JSON file permissions**:
  ```bash
  chmod 644 *.json
  ```
- **Verify file paths** are absolute
- **Check file encoding** is UTF-8

### Issue 5: API Not Responding
- **Check server logs** in Web tab
- **Verify app.py** has proper error handling
- **Test endpoints** individually

## 📊 Monitoring

1. **Check error logs** in Web tab
2. **Monitor server logs** for issues
3. **Test API endpoints** regularly
4. **Check file permissions** periodically

## 🔄 Updating Your App

To update your deployed app:

1. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

2. **Install new dependencies** (if any):
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Rebuild frontend** (if changed):
   ```bash
   cd frontend
   npm run build
   cp -r dist/* ../static/
   ```

4. **Reload web app** in Web tab

## 🎉 Success!

Your HTU Assistant should now be accessible at:
- **Main site**: `https://YOUR_USERNAME.pythonanywhere.com`
- **Health check**: `https://YOUR_USERNAME.pythonanywhere.com/health`
- **API endpoint**: `https://YOUR_USERNAME.pythonanywhere.com/api/chat`

## 📞 Support

If you encounter issues:
1. **Check PythonAnywhere logs** in Web tab
2. **Verify all configuration** steps
3. **Test endpoints** individually
4. **Contact PythonAnywhere support** if needed

---

**Remember**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username throughout this guide. 