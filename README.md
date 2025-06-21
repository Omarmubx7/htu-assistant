# HTU Assistant 🤖

A smart, interactive chatbot for HTU (Al-Hussein Technical University) students and staff. Get instant access to course information, professor office hours, and academic resources.

## ✨ Features

- **🎓 Course Information**: Search for courses by code (e.g., CS201, CS101)
- **👨‍🏫 Professor Office Hours**: Find professor schedules and contact information
- **🌙 Dark Mode**: Toggle between light and dark themes
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices
- **🔍 Smart Search**: Fuzzy matching for course codes and professor names
- **💬 Interactive Chat**: Natural language processing for better user experience

## 🚀 Live Demo

Visit the live application: [HTU Assistant](https://yourusername.github.io/atharprojects/)

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with CSS Variables for theming
- **Fonts**: Inter (Google Fonts)
- **Icons**: SVG icons and emojis
- **Hosting**: GitHub Pages

## 📁 Project Structure

```
atharprojects/
├── index.html              # Main application file
├── README.md               # Project documentation
├── app.py                  # Flask backend (for full version)
├── templates/              # Flask templates
├── static/                 # Static assets
├── office_hours.json       # Professor data
└── full_subjects_study_plan.json  # Course data
```

## 🎯 How to Use

1. **Course Information**: Type course codes like "CS101" or "CS201"
2. **Professor Search**: Search by name like "Dr. Ahmed Bataineh"
3. **Quick Actions**: Use the quick action buttons for common queries
4. **Dark Mode**: Click the moon/sun icon to toggle themes

## 🚀 Deployment

### GitHub Pages (Current)

This version is deployed on GitHub Pages as a static site:

1. Push your code to GitHub
2. Go to repository Settings > Pages
3. Select "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Your site will be available at `https://yourusername.github.io/atharprojects/`

### Custom Domain Setup

To use a custom domain like "htu-assistant.com":

1. **Purchase a domain** from a registrar (Namecheap, GoDaddy, etc.)
2. **Add CNAME record**:
   - Name: `@` or `www`
   - Value: `yourusername.github.io`
3. **In GitHub repository**:
   - Go to Settings > Pages
   - Add your custom domain in "Custom domain" field
   - Check "Enforce HTTPS"
4. **Create CNAME file** in your repository root:
   ```
   htu-assistant.com
   ```

### Full Flask Version

For the complete Flask application with server-side processing:

1. **Deploy to Heroku**:
   ```bash
   heroku create htu-assistant
   git push heroku main
   ```

2. **Deploy to Railway**:
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Deploy to Render**:
   - Connect your GitHub repository
   - Choose "Web Service"
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python app.py`

## 🔧 Local Development

### Static Version (GitHub Pages)
```bash
# Clone the repository
git clone https://github.com/yourusername/atharprojects.git
cd atharprojects

# Open index.html in your browser
# Or use a local server
python -m http.server 8000
```

### Flask Version
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Visit http://localhost:5000
```

## 📊 Data Sources

- **Course Information**: HTU Study Plans
- **Professor Office Hours**: HTU Faculty Schedules
- **Contact Information**: HTU Directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- HTU Faculty and Staff for providing data
- Inter font family for beautiful typography
- GitHub Pages for hosting

## 📞 Support

For support or questions:
- Create an issue on GitHub
- Contact: [your-email@example.com]

---

**Made with ❤️ for HTU Students** 