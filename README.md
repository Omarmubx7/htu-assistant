# 🎓 Athar Assistant - HTU University Bot

A smart, AI-powered chatbot for HTU (Al-Hussein Technical University) that helps students and staff find information about courses, professors, office hours, and study plans.

## ✨ Features

### 🤖 **Smart Chat Interface**
- **Natural Language Processing**: Understands conversational queries
- **Fuzzy Matching**: Finds professors and courses even with typos
- **Context Awareness**: Remembers previous conversations
- **Real-time Responses**: Instant answers to your questions

### 📚 **Course Information**
- **Course Search**: Find courses by code (e.g., CS101, CS201)
- **Detailed Information**: Credits, descriptions, prerequisites
- **Study Plans**: View curriculum for different years and majors
- **Program Information**: Complete course sequences

### 👨‍🏫 **Professor Directory**
- **Office Hours**: Complete schedules for all professors
- **Contact Information**: Email addresses and office locations
- **Department Info**: Find professors by department
- **Smart Search**: Find professors by name variations

### 🎨 **Modern UI/UX**
- **Dark/Light Mode**: Toggle between themes
- **Responsive Design**: Works on all devices
- **Autocomplete**: Smart suggestions as you type
- **Quick Actions**: One-click access to common queries
- **Real-time Status**: Connection health indicator

### 🔧 **Technical Features**
- **RESTful API**: Clean, documented endpoints
- **CORS Support**: Works across all domains
- **Error Handling**: Graceful error management
- **Health Monitoring**: Built-in health checks
- **Scalable Architecture**: Ready for production

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Omarmubx7/htu-assistant.git
   cd htu-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   - Visit: `http://localhost:5000`
   - The app will be running with full functionality

## 📁 Project Structure

```
htu-assistant/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── office_hours.json          # Professor data
├── full_subjects_study_plan.json  # Course data
├── static/
│   ├── index.html             # Main frontend interface
│   └── images/                # Static assets
├── templates/                 # Flask templates (if needed)
├── frontend/                  # React frontend (optional)
├── deploy.py                  # Deployment automation script
├── test_api.py               # API testing script
└── README.md                 # This file
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Main chat interface
- `GET /health` - Health check endpoint
- `POST /api/chat` - Main chat API
- `GET /api/professors` - Get all professors
- `GET /api/courses` - Get all courses

### Example API Usage
```bash
# Health check
curl https://your-domain.com/health

# Send a message
curl -X POST https://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find CS101"}'
```

## 🌐 Deployment

### Option 1: PythonAnywhere (Recommended)
Follow the detailed guide in `PYTHONANYWHERE_DEPLOYMENT.md`

### Option 2: Railway
1. Connect your GitHub repository
2. Railway will auto-detect Python
3. Deploy with one click

### Option 3: Heroku
1. Create a `Procfile`:
   ```
   web: gunicorn app:app
   ```
2. Deploy using Heroku CLI or GitHub integration

### Option 4: Vercel
1. Install Vercel CLI
2. Run `vercel` in project directory
3. Follow prompts

## 🧪 Testing

### Run API Tests
```bash
python test_api.py
```

### Manual Testing
1. Start the application
2. Visit the health endpoint: `/health`
3. Test chat functionality with various queries
4. Verify all features work correctly

## 📊 Data Sources

### Professor Data (`office_hours.json`)
- **50+ Professors** from School of Computing and Informatics
- **Complete office hours** for each professor
- **Contact information** including emails and office locations
- **Department affiliations** for easy searching

### Course Data (`full_subjects_study_plan.json`)
- **Comprehensive course catalog** for all programs
- **Study plans** for different years and majors
- **Course descriptions** and credit information
- **Prerequisites** and program requirements

## 🛠️ Customization

### Adding New Professors
1. Edit `office_hours.json`
2. Add new professor entry with required fields
3. Restart the application

### Adding New Courses
1. Edit `full_subjects_study_plan.json`
2. Add course information to appropriate program
3. Restart the application

### Modifying the UI
1. Edit `static/index.html`
2. Customize CSS variables in `:root`
3. Add new features to JavaScript

## 🔒 Security Features

- **CORS Protection**: Configured for secure cross-origin requests
- **Input Validation**: All user inputs are validated
- **Error Handling**: Graceful error responses
- **Rate Limiting**: Built-in protection against abuse

## 📈 Performance

- **Fast Response Times**: Optimized for quick responses
- **Efficient Data Loading**: JSON files loaded once at startup
- **Minimal Dependencies**: Lightweight and fast
- **Caching**: Built-in caching for better performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

### Getting Help
- **Documentation**: Check this README and deployment guides
- **Issues**: Create an issue on GitHub
- **Testing**: Use the provided test scripts

### Common Issues
- **CORS Errors**: Check CORS configuration in `app.py`
- **Data Not Loading**: Verify JSON files are valid
- **Deployment Issues**: Follow the deployment guides

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **HTU Faculty**: For providing course and professor data
- **Open Source Community**: For the amazing tools and libraries
- **Students**: For feedback and testing

---

**Made with ❤️ for HTU students and staff**

**Live Demo**: [Your deployed URL here]
**GitHub**: https://github.com/Omarmubx7/htu-assistant 