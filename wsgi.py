import sys
import os

# Add your project directory to the sys.path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
from app import app as application

# Set environment variables
os.environ['FLASK_ENV'] = 'production' 