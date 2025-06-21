# HTU Info Bot - Deployment Guide

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open in browser
http://localhost:5000
```

### Replit Deployment
1. Go to [replit.com](https://replit.com) and create a new Python project
2. Upload all files to the project
3. Replit will automatically detect Flask and run the app
4. Your bot will be available at the Replit URL

### Render Deployment
1. Create a new Web Service on [render.com](https://render.com)
2. Connect your GitHub repository
3. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3
4. Deploy and get your public URL

### Heroku Deployment
1. Create a `Procfile` with content: `web: python app.py`
2. Install Heroku CLI and run:
   ```bash
   heroku create your-app-name
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

## 📁 Project Structure
```
htu-info-bot/
├── app.py                          # Main Flask application
├── templates/
│   └── index.html                  # Chat interface
├── full_subjects_study_plan.json   # Course data
├── office_hours.json              # Professor data
├── requirements.txt               # Dependencies
├── test_bot.py                    # Test script
├── README.md                      # Documentation
└── DEPLOYMENT.md                  # This file
```

## 🧪 Testing
Run the test script to verify functionality:
```bash
python test_bot.py
```

## 🔧 Customization

### Adding More Courses
Edit `full_subjects_study_plan.json`:
```json
{
    "New Major": {
        "Level 1": {
            "NEW101": {
                "name": "New Course",
                "description": "Course description",
                "credits": 3
            }
        }
    }
}
```

### Adding More Professors
Edit `office_hours.json`:
```json
{
    "Dr. New Professor": "Monday: 9:00 AM - 11:00 AM\nOffice: Building X, Room Y"
}
```

## 🌐 Environment Variables
For production, consider setting:
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`

## 📱 Features
- ✅ Course information lookup (CS201, CS101, etc.)
- ✅ Professor office hours (Dr. Ahmed Bataineh, etc.)
- ✅ Modern chat interface
- ✅ Mobile responsive
- ✅ Real-time responses
- ✅ Error handling

## 🐛 Troubleshooting

### Common Issues
1. **Port already in use**: Change port in `app.py`
2. **JSON file not found**: Ensure files are in the same directory
3. **Flask not installed**: Run `pip install -r requirements.txt`

### Logs
Check console output for error messages when running locally.

## 📞 Support
For issues, check the code comments or create an issue in the repository. 