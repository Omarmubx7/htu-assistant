from flask import Flask, request, jsonify, send_from_directory
import json
import re
from difflib import SequenceMatcher
from datetime import datetime
import random
from typing import Optional
import unicodedata
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'htu_info_bot_secret_key_2024'

def load_data():
    """Loads data from JSON files."""
    try:
        with open('full_subjects_study_plan.json', 'r', encoding='utf-8') as f:
            subjects_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        subjects_data = {}
    
    try:
        with open('office_hours.json', 'r', encoding='utf-8') as f:
            office_hours_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        office_hours_data = [] # Now a list
    
    return subjects_data, office_hours_data

subjects_data, office_hours_data = load_data()

class ConversationContext:
    def __init__(self):
        self.last_query_type: Optional[str] = None
        self.last_subject: Optional[str] = None
        self.last_professor: Optional[str] = None
        self.query_count: int = 0
        self.preferences: dict = {}

context = ConversationContext()

def parse_office_hours(raw_text):
    """Parses the raw office hours string into a structured dictionary."""
    data = {'raw': raw_text}
    lines = raw_text.split('\n')
    
    key_mapping = {
        "Name": "name",
        "Academic School": "school",
        "Department": "department",
        "Email": "email",
        "Office number": "office_number",
        "Office Number": "office_number",
    }
    
    schedule_started = False
    schedule = {}
    current_day = None
    days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    for line in lines:
        if not line.strip():
            continue
            
        if "Office Hours" in line and len(line) < 20:
             continue

        if "Time/Day:" in line:
            schedule_started = True
            continue
            
        if schedule_started:
            line_content = line.strip()
            found_day = False
            for day in days:
                if line_content.startswith(day):
                    parts = line_content.split(':', 1)
                    current_day = parts[0].strip()
                    schedule[current_day] = parts[1].strip() if len(parts) > 1 else ""
                    found_day = True
                    break
            if not found_day and current_day:
                 schedule[current_day] += " " + line_content

        else:
            for key, value in key_mapping.items():
                if line.startswith(key + ":"):
                    data[value] = line.split(":", 1)[1].strip()
                    break
    
    data['schedule'] = schedule
    
    if 'name' in data and '(' in data['name']:
        data['name'] = re.sub(r'\s*\([^)]*\)', '', data['name'])

    return data

def calculate_similarity(a, b):
    """Calculates the similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_name(name):
    if not isinstance(name, str):
        return ''
    # Lowercase, strip, replace all dashes with '-', collapse spaces, remove diacritics
    name = name.lower().strip()
    name = re.sub(r'[\u2010-\u2015\u2212\uFE58\uFE63\uFF0D\u2013\u2014\u2015]', '-', name)  # all dash-like chars
    name = re.sub(r'\s+', ' ', name)
    name = ''.join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
    return name

def find_subject_info_smart(subject_code):
    """Finds subject information with fuzzy matching."""
    for major, levels in subjects_data.items():
        for level, subjects in levels.items():
            if subject_code.upper() in subjects:
                subject_info = subjects[subject_code.upper()]
                return {
                    'major': major,
                    'level': level,
                    'name': subject_info['name'],
                    'description': subject_info['description'],
                    'credits': subject_info['credits'],
                    'match_type': 'exact'
                }
    
    best_match = None
    best_score = 0.6
    
    for major, levels in subjects_data.items():
        for level, subjects in levels.items():
            for code in subjects.keys():
                similarity = calculate_similarity(subject_code, code)
                if similarity > best_score:
                    best_score = similarity
                    subject_info = subjects[code]
                    best_match = {
                        'major': major,
                        'level': level,
                        'name': subject_info['name'],
                        'description': subject_info['description'],
                        'credits': subject_info['credits'],
                        'match_type': 'fuzzy',
                        'original_code': code,
                        'similarity': similarity
                    }
    return best_match

def find_professor_office_hours_smart(professor_name):
    """Finds professor information from the structured list."""
    clean_input = normalize_name(professor_name)
    potential_matches = []
    for prof in office_hours_data:
        prof_name_from_data = normalize_name(prof.get('name', ''))
        if not prof_name_from_data:
            continue
        similarity = calculate_similarity(clean_input, prof_name_from_data)
        if clean_input == prof_name_from_data:
            prof['match_type'] = 'exact'
            prof['similarity'] = 1.0
            return [prof] # Exact match found, return immediately
        if clean_input in prof_name_from_data or similarity > 0.6:
            prof['match_type'] = 'contains' if clean_input in prof_name_from_data else 'fuzzy'
            prof['similarity'] = similarity
            potential_matches.append(prof)
    potential_matches.sort(key=lambda x: x.get('similarity', 0), reverse=True)
    return potential_matches

def extract_intent(user_message):
    """Extracts user intent from the message."""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return 'greeting'
    if any(word in message_lower for word in ['course', 'subject', 'class', 'credit', 'prerequisite', 'syllabus']):
        return 'subject_info'
    if any(word in message_lower for word in ['professor', 'doctor', 'dr', 'eng', 'teacher', 'instructor', 'office', 'hours', 'schedule']):
        return 'professor_info'
    if any(word in message_lower for word in ['help', 'what can you do', 'how to use', 'guide']):
        return 'help'
    if any(word in message_lower for word in ['what', 'how', 'when', 'where', 'why', 'who']):
        return 'general_question'
    
    return 'unknown'

def generate_smart_response(intent, user_message, subject_result=None, professor_results=None):
    """Generates a response based on intent and results."""
    if intent == 'greeting':
        greetings = [
            "👋 Hello! I'm your HTU Info Assistant. How can I help you today?",
            "🎓 Welcome to HTU Info Bot! I can help you find course information and professor office hours.",
            "Hi there! I'm here to help with HTU academic information. What would you like to know?"
        ]
        return random.choice(greetings)
    
    elif intent == 'help':
        return """
🤖 **HTU Info Bot - Smart Assistant**

I can help you with:

📚 **Course Information:**
• Search by subject code (e.g., CS201, CS101)
• Get course details, credits, and descriptions
• Find prerequisites and program information

👨‍🏫 **Professor Office Hours:**
• Search by professor name (e.g., Dr. Ahmed Bataineh)
• Get office hours, locations, and contact info
• Find department and email information

💡 **Smart Features:**
• Fuzzy matching for similar names/codes
• Context-aware responses
• Natural language understanding

Try asking me about any course or professor!
        """.strip()
    
    elif subject_result:
        if subject_result['match_type'] == 'fuzzy':
            response = f"🔍 I found a similar course: **{subject_result['original_code']}**\n\n"
            response += f"📚 **{subject_result['original_code']} - {subject_result['name']}**\n\n"
        else:
            response = f"📚 **{user_message.upper()} - {subject_result['name']}**\n\n"
        
        response += f"**Description:** {subject_result['description']}\n"
        response += f"**Credits:** {subject_result['credits']}\n"
        response += f"**Level:** {subject_result['level']}\n"
        response += f"**Program:** {subject_result['major']}\n\n"
        
        if subject_result['match_type'] == 'fuzzy':
            response += f"💡 *Did you mean {subject_result['original_code']} instead of your search?*"
        else:
            response += f"🎯 This course is part of {subject_result['level']} in the {subject_result['major']} program."
        
        response += "\n\n💡 **You can also ask:**\n• Which professors teach this course?\n• Are there prerequisites?"
        return response

    elif professor_results:
        # Handle multiple potential matches
        if len(professor_results) > 1:
            response = f"🤔 I found a few people matching **{user_message}**. Who are you looking for?\n\n"
            for prof in professor_results[:4]: # Limit to 4 to avoid overwhelming
                response += f"• {prof.get('name', 'N/A')}\n"
            return response

        # Handle a single match
        details = professor_results[0]
        prof_display_name = details.get('name', 'N/A')

        response = f"👨‍🏫 **Professor {prof_display_name}**\n\n"

        if details.get('department'):
            response += f"**Department:** {details.get('department')}\n"
        if details.get('office'):
            response += f"**Office:** {details.get('office')}\n"
        if details.get('email'):
            response += f"**Email:** {details.get('email')}\n"

        schedule = details.get('office_hours')
        if schedule and isinstance(schedule, dict):
            office_hours_output = ""
            days_order = {day: i for i, day in enumerate(["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])}
            sorted_schedule = sorted(schedule.items(), key=lambda item: days_order.get(item[0], 99))

            for day, times in sorted_schedule:
                if times:
                    office_hours_output += f"• **{day}:** {times}\n"

            if office_hours_output:
                response += "\n**Office Hours Schedule:**\n" + office_hours_output
            else:
                response += "\nNo specific office hours are listed for this professor."
        else:
            response += "\nNo schedule information found for this professor."
        
        response += "\n\n💡 **You can also ask:**\n• What courses does this professor teach?\n• Who else is in this department?"
        return response

    else:
        suggestions = [
            "🤔 I'm not sure I understood. Here are some things you can ask me:",
            "❓ Let me help you find what you're looking for. Try one of these:",
            "💭 I didn't find an exact match. Here are some suggestions:"
        ]
        
        response = random.choice(suggestions) + "\n\n"
        response += "📚 **For Course Information:**\n"
        response += "• \"Tell me about CS201\"\n\n"
        response += "👨‍🏫 **For Professor Information:**\n"
        response += "• \"Office hours for Dr. Ahmed Bataineh\"\n\n"
        response += "💡 **Or try:**\n"
        response += "• \"Help\" - to see all features"
        
        return response

@app.route('/')
def index():
    # Serve the static index.html for the frontend
    return app.send_static_file('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    # Serve static assets (images, CSS, JS)
    static_folder = app.static_folder or 'static'
    return send_from_directory(static_folder, filename)

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat messages."""
    if not request.json or 'message' not in request.json:
        return jsonify({'response': 'Invalid request.'})
    
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})

    intent = extract_intent(user_message)

    # Prioritize subject code search if pattern matches
    subject_match = re.search(r'\b[A-Z]{2,3}\d{3}\b', user_message.upper())
    if subject_match:
        subject_code = subject_match.group()
        subject_result = find_subject_info_smart(subject_code)
        if subject_result:
            response = generate_smart_response(intent, user_message, subject_result=subject_result)
            return jsonify({'response': response})

    # Fallback to professor search
    professor_results = find_professor_office_hours_smart(user_message)
    if professor_results:
        response = generate_smart_response(intent, user_message, professor_results=professor_results)
        return jsonify({'response': response})
    
    # Handle greeting or help intents if no specific results found
    if intent in ['greeting', 'help']:
        response = generate_smart_response(intent, user_message)
        return jsonify({'response': response})

    # Default fallback response
    response = generate_smart_response('unknown', user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    # Add both JSON files to 'extra_files' to trigger auto-reload on change
    json_files = ['office_hours.json', 'full_subjects_study_plan.json']
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, extra_files=json_files)