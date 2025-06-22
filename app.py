from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import re
from difflib import SequenceMatcher
from datetime import datetime
import random
from typing import Optional
import unicodedata
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, origins=[
    'http://localhost:5173', 
    'http://127.0.0.1:5173', 
    'https://omarmubaidin.pythonanywhere.com'
])  # Allow React dev server and deployed site
app.secret_key = 'htu_info_bot_secret_key_2024'

def load_data():
    """Loads data from JSON files."""
    # Construct the absolute path to the data files
    project_root = os.path.dirname(os.path.abspath(__file__))
    subjects_path = os.path.join(project_root, 'full_subjects_study_plan.json')
    office_hours_path = os.path.join(project_root, 'office_hours.json')
    
    try:
        with open(subjects_path, 'r', encoding='utf-8') as f:
            subjects_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        subjects_data = {}
    
    try:
        with open(office_hours_path, 'r', encoding='utf-8') as f:
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

def find_study_plan(major, level_query):
    """Finds the study plan for a given major and level."""
    normalized_major = major.lower().replace("engineering", "eng").strip()
    
    # Find the best matching major key
    best_major_match = None
    highest_similarity = 0.7 
    for major_key in subjects_data.keys():
        similarity = calculate_similarity(normalized_major, major_key.lower())
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_major_match = major_key

    if not best_major_match:
        return None

    # Match level query (first, second, etc.)
    level_map = {
        'first': 'First Year', '1st': 'First Year',
        'second': 'Second Year', '2nd': 'Second Year',
        'third': 'Third Year', '3rd': 'Third Year',
        'fourth': 'Fourth Year', '4th': 'Fourth Year',
        'fifth': 'Fifth Year', '5th': 'Fifth Year',
    }
    
    normalized_level = None
    for key, value in level_map.items():
        if key in level_query.lower():
            normalized_level = value
            break
            
    if not normalized_level or normalized_level not in subjects_data[best_major_match]:
        return None
        
    plan = subjects_data[best_major_match][normalized_level]
    return {'major': best_major_match, 'level': normalized_level, 'plan': plan}

def format_schedule(schedule_dict):
    """Formats the schedule dictionary into a readable string."""
    if not schedule_dict:
        return "No schedule information available."
    
    formatted_lines = []
    days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    for day in days:
        if day in schedule_dict:
            times = schedule_dict[day]
            if times and str(times).strip().lower() not in ['none', 'n/a', 'office hours']:
                # Format each line for better readability in chat
                formatted_lines.append(f"&bull; **{day}:** {times}")

    if not formatted_lines:
        return "No specific office hours are listed."
        
    return "\n".join(formatted_lines)

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
        return {'text': random.choice(greetings)}
    
    elif intent == 'help':
        return {
            'text': """
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
        }
    
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
        
        response += "\n\n💡 **You can also ask:**\n• Which professors teach this course?\n• Are there prerequisites?"
        return {'text': response}

    elif professor_results:
        # Handle multiple potential matches
        if len(professor_results) > 1:
            response = {
                'text': f"🤔 I found a few people matching **{user_message}**. Who are you looking for?",
                'buttons': [prof.get('name', 'N/A') for prof in professor_results[:4]]
            }
            return response

        # Handle a single match
        details = professor_results[0]
        prof_display_name = details.get('name', 'N/A')

        if details.get('match_type') == 'fuzzy':
            response = f"🤖 I found someone with a similar name: **{prof_display_name}**.\n\n"
        else:
            response = f"👨‍🏫 Here is the information for **{prof_display_name}**:\n\n"

        response += f"**School:** {details.get('school', 'N/A')}\n"
        response += f"**Department:** {details.get('department', 'N/A')}\n"
        response += f"**Email:** {details.get('email', 'N/A')}\n"
        response += f"**Office:** {details.get('office', 'N/A')}\n\n"

        schedule = format_schedule(details.get('office_hours', {}))
        response += f"**Office Hours:**\n{schedule}"
        
        response += f"\n\n💡 You can now ask me for this professor's **email**, **office**, or **schedule** separately."
        return {'text': response}
    
    elif intent == 'unknown':
        response = {
            'text': "🤔 I'm not sure I understood. Here are some things you can ask me:",
            'buttons': ["Find a Course", "Find a Professor", "View a Study Plan"]
        }
        return response

@app.route('/')
def index():
    # Serve the React frontend
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    current_professor = data.get('current_professor')
    message_lower = user_message.lower().strip()
    response = ""

    # Check for follow-up questions about the current professor
    if current_professor:
        prof_name = current_professor.get('name', 'The professor')
        # Check for specific follow-up intents
        if any(word in message_lower for word in ['school', 'college', 'faculty']):
            school = current_professor.get('school', 'I could not find their school.')
            response = f"🏫 **{prof_name}** is in the: {school}"
            return jsonify({'response': response, 'professor': current_professor})
        if any(word in message_lower for word in ['email', 'contact']):
            email = current_professor.get('email', 'I could not find an email for them.')
            response = f"📧 The email for **{prof_name}** is: {email}"
            return jsonify({'response': response, 'professor': current_professor})
        if any(word in message_lower for word in ['office', 'location', 'room']):
            office = current_professor.get('office', 'I could not find their office number.')
            response = f"📍 The office for **{prof_name}** is: {office}"
            return jsonify({'response': response, 'professor': current_professor})
        if any(word in message_lower for word in ['schedule', 'hours', 'when', 'times']):
            schedule = format_schedule(current_professor.get('office_hours', {}))
            if "No schedule" in schedule or "No specific" in schedule:
                 response = f"🗓️ I couldn't find a specific schedule for **{prof_name}**."
            else:
                 response = f"🗓️ Here is the schedule for **{prof_name}**:\n{schedule}"
            return jsonify({'response': response, 'professor': current_professor})

    # --- Regular Processing ---
    intent = extract_intent(message_lower)
    subject_code_match = re.search(r'([a-zA-Z]{2,4}\s*\d{3})', user_message)
    study_plan_match = re.search(r'(show|tell|give|what is|find)\s+(me\s+)?(the\s+)?(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th)\s+year\s+(plan\s+)?(for\s+)?([a-zA-Z\s]+)', message_lower)

    professor_results = None
    subject_result = None
    
    if study_plan_match:
        level_query = study_plan_match.group(4)
        major_query = study_plan_match.group(7)
        plan_result = find_study_plan(major_query, level_query)
        if plan_result:
            response_text = f"📚 Here is the **{plan_result['level']}** plan for **{plan_result['major']}**:\n\n"
            for code, details in plan_result['plan'].items():
                response_text += f"• **{code}**: {details['name']} ({details['credits']} credits)\n"
            response = response_text
        else:
            response = f"Sorry, I couldn't find a study plan for '{major_query}'."
        return jsonify({'response': response})

    if subject_code_match:
        subject_result = find_subject_info_smart(subject_code_match.group(1))
    else:
        # Assuming the query is for a professor if no subject code is found.
        # This can be improved with more sophisticated intent detection.
        professor_results = find_professor_office_hours_smart(user_message)

    # Update context after a successful search
    if professor_results and len(professor_results) == 1:
        context.last_professor = professor_results[0]
        context.last_subject = None  # Clear subject context
    elif subject_result:
        context.last_subject = subject_result
        context.last_professor = None  # Clear professor context
    else:
        # If no clear result or multiple matches, clear context to avoid incorrect follow-ups
        context.last_professor = None
        context.last_subject = None

    response_data = generate_smart_response(intent, user_message, subject_result, professor_results)
    
    # Return response in the format expected by React frontend
    if professor_results and len(professor_results) == 1:
        return jsonify({
            'response': response_data.get('text', response_data),
            'professor': professor_results[0]
        })
    else:
        return jsonify({
            'response': response_data.get('text', response_data)
        })

if __name__ == '__main__':
    # Add both JSON files to 'extra_files' to trigger auto-reload on change
    json_files = ['office_hours.json', 'full_subjects_study_plan.json']
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, extra_files=json_files)