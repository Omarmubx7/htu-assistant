from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import json
import re
from difflib import SequenceMatcher
from datetime import datetime
import random
from typing import Optional
import unicodedata
import os
import copy

app = Flask(__name__, static_folder='static', template_folder='templates')

# Comprehensive CORS configuration for all deployment scenarios
CORS(app, origins=[
    'http://localhost:5173', 
    'http://127.0.0.1:5173', 
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'https://omarmubaidin.pythonanywhere.com',
    'https://omarmubx7.github.io',
    'https://htu-assistant.com',
    'https://*.github.io',
    'https://*.pythonanywhere.com',
    'https://*.vercel.app',
    'https://*.railway.app',
    'https://*.herokuapp.com'
], methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

app.secret_key = 'htu_info_bot_secret_key_2024'

def load_data():
    """Loads data from JSON files with comprehensive error handling."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    subjects_path = os.path.join(project_root, 'full_subjects_study_plan.json')
    office_hours_path = os.path.join(project_root, 'office_hours.json')
    
    try:
        with open(subjects_path, 'r', encoding='utf-8') as f:
            subjects_data = json.load(f)
        print(f"✅ Successfully loaded subjects data from {subjects_path}")
    except FileNotFoundError:
        print(f"❌ Subjects file not found: {subjects_path}")
        subjects_data = {}
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in subjects file: {e}")
        subjects_data = {}
    except PermissionError as e:
        print(f"❌ Permission error accessing subjects file: {e}")
        subjects_data = {}
    
    try:
        with open(office_hours_path, 'r', encoding='utf-8') as f:
            office_hours_data = json.load(f)
        print(f"✅ Successfully loaded office hours data from {office_hours_path}")
    except FileNotFoundError:
        print(f"❌ Office hours file not found: {office_hours_path}")
        office_hours_data = []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in office hours file: {e}")
        office_hours_data = []
    except PermissionError as e:
        print(f"❌ Permission error accessing office hours file: {e}")
        office_hours_data = []
    
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
    """Normalizes names for consistent matching."""
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
    if not subjects_data:
        return None
        
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
    if not office_hours_data:
        return []
        
    clean_input = normalize_name(professor_name)
    potential_matches = []
    
    for prof in office_hours_data:
        prof_name_from_data = normalize_name(prof.get('name', ''))
        if not prof_name_from_data:
            continue
        
        # Create a deep copy to prevent any chance of data corruption
        prof_copy = copy.deepcopy(prof)
        
        similarity = calculate_similarity(clean_input, prof_name_from_data)
        
        if clean_input == prof_name_from_data:
            prof_copy['match_type'] = 'exact'
            prof_copy['similarity'] = 1.0
            return [prof_copy]

        if clean_input in prof_name_from_data or similarity > 0.6:
            prof_copy['match_type'] = 'contains' if clean_input in prof_name_from_data else 'fuzzy'
            prof_copy['similarity'] = similarity
            potential_matches.append(prof_copy)
            
    potential_matches.sort(key=lambda x: x.get('similarity', 0), reverse=True)
    return potential_matches

def find_professors_in_department(department_name, exclude_professor_name):
    """Finds all professors in a given department, excluding one professor."""
    if not department_name or not office_hours_data:
        return []
    
    colleagues = []
    normalized_exclude_name = normalize_name(exclude_professor_name)
    
    for prof in office_hours_data:
        prof_department = prof.get('department', '')
        prof_name = prof.get('name', '')
        
        # Check for department match (case-insensitive) and ensure it's not the excluded professor
        if (prof_department.lower() == department_name.lower() and 
            normalize_name(prof_name) != normalized_exclude_name):
            colleagues.append(prof_name)
    
    return colleagues

def find_study_plan(major_query, level_query):
    """Finds study plan for a specific major and level."""
    if not subjects_data:
        return None
        
    # Normalize the major query
    major_query = major_query.strip().lower()
    level_query = level_query.strip().lower()
    
    # Map level queries to actual level names
    level_mapping = {
        'first': 'First Year',
        '1st': 'First Year',
        'second': 'Second Year', 
        '2nd': 'Second Year',
        'third': 'Third Year',
        '3rd': 'Third Year',
        'fourth': 'Fourth Year',
        '4th': 'Fourth Year',
        'fifth': 'Fifth Year',
        '5th': 'Fifth Year'
    }
    
    target_level = level_mapping.get(level_query, level_query.title())
    
    # Find the major
    for major, levels in subjects_data.items():
        if major_query in major.lower():
            if target_level in levels:
                return {
                    'major': major,
                    'level': target_level,
                    'plan': levels[target_level]
                }
    
    return None

def format_schedule(schedule_dict):
    """Formats office hours schedule for display."""
    if not schedule_dict:
        return "No schedule available."
    
    formatted_schedule = ""
    days_order = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for day in days_order:
        if day in schedule_dict and schedule_dict[day]:
            formatted_schedule += f"**{day}:** {schedule_dict[day]}\n"
    
    if not formatted_schedule:
        return "No specific schedule available."
    
    return formatted_schedule.strip()

def extract_intent(user_message):
    """Extracts user intent from the message."""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['help', 'what can you do', 'assist']):
        return 'help'
    elif any(word in message_lower for word in ['course', 'subject', 'cs', 'it', 'se']):
        return 'course_search'
    elif any(word in message_lower for word in ['professor', 'teacher', 'instructor', 'dr', 'dr.']):
        return 'professor_search'
    elif any(word in message_lower for word in ['plan', 'curriculum', 'year']):
        return 'study_plan'
    else:
        return 'unknown'

def generate_smart_response(intent, user_message, subject_result=None, professor_results=None):
    """Generates intelligent responses based on intent and results."""
    
    if intent == 'help':
        return {
            'text': """
🤖 **HTU Assistant - Smart University Bot**

I can help you with:

📚 **Course Information:**
• Search by subject code (e.g., CS201, CS101)
• Get course details, credits, and descriptions
• Find prerequisites and program information

👨‍🏫 **Professor Office Hours:**
• Search by professor name (e.g., Ahmed Bataineh)
• Get office hours, locations, and contact info
• Find department and email information

📋 **Study Plans:**
• View curriculum for different years
• Find course sequences and requirements

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
        response += f"**Office Hours Schedule:**\n{schedule}"
        
        # Dynamic suggestions based on context
        response += "\n\n💡 **You can also ask:**"
        response += "\n• What courses does this professor teach?"
        response += "\n• Who else is in this department?"

        return {'text': response}
    
    elif intent == 'unknown':
        response = {
            'text': "🤔 I'm not sure I understood. Here are some things you can ask me:",
            'buttons': ["Find a Course", "Find a Professor", "View a Study Plan", "Help"]
        }
        return response

# Route handlers
@app.route('/')
def index():
    """Serve the main chat interface."""
    return send_from_directory('static', 'index.html')

@app.route('/chat')
def chat_page():
    """Alternative chat page route."""
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint to verify the API is accessible."""
    try:
        # Check if data files are accessible
        subjects_count = len(subjects_data) if subjects_data else 0
        office_hours_count = len(office_hours_data) if office_hours_data else 0
        
        return jsonify({
            'status': 'healthy',
            'message': 'HTU Assistant API is running',
            'data_loaded': {
                'subjects': subjects_count,
                'professors': office_hours_count
            },
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat API endpoint."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = data.get('message', '')
        current_professor = data.get('current_professor')
        
        if not user_message.strip():
            return jsonify({'error': 'Empty message provided'}), 400
            
        message_lower = user_message.lower().strip()
        response = ""

        # Check for follow-up questions about the current professor
        if current_professor:
            prof_name = current_professor.get('name', 'The professor')
            # Check for specific follow-up intents
            if 'who else' in message_lower and 'department' in message_lower:
                department = current_professor.get('department')
                if department:
                    colleagues = find_professors_in_department(department, prof_name)
                    if colleagues:
                        response = f"👥 Here are other professors in the **{department}** department:\n\n"
                        for colleague in colleagues[:10]: # Limit to 10 to avoid huge lists
                            response += f"• {colleague}\n"
                    else:
                        response = f"I couldn't find any other professors in the **{department}** department."
                else:
                    response = f"I'm not sure which department **{prof_name}** is in."
                return jsonify({'response': response, 'professor': current_professor})

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
        
        # Construct the JSON response for the frontend
        json_response = {
            'response': response_data.get('text', "Sorry, something went wrong.")
        }

        if 'buttons' in response_data:
            json_response['buttons'] = response_data['buttons']

        # If a single professor was found, add it to the response for context
        if professor_results and len(professor_results) == 1:
            json_response['professor'] = professor_results[0]
        
        return jsonify(json_response)
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({
            'response': "I'm sorry, I encountered an error processing your request. Please try again.",
            'error': str(e)
        }), 500

@app.route('/api/professors')
def get_professors():
    """Get all professors for autocomplete or listing."""
    try:
        if not office_hours_data:
            return jsonify({'professors': []})
        
        professors = []
        for prof in office_hours_data:
            professors.append({
                'name': prof.get('name', ''),
                'department': prof.get('department', ''),
                'school': prof.get('school', '')
            })
        
        return jsonify({'professors': professors})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses')
def get_courses():
    """Get all courses for autocomplete or listing."""
    try:
        if not subjects_data:
            return jsonify({'courses': []})
        
        courses = []
        for major, levels in subjects_data.items():
            for level, subjects in levels.items():
                for code, details in subjects.items():
                    courses.append({
                        'code': code,
                        'name': details.get('name', ''),
                        'major': major,
                        'level': level,
                        'credits': details.get('credits', '')
                    })
        
        return jsonify({'courses': courses})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Add both JSON files to 'extra_files' to trigger auto-reload on change
    json_files = ['office_hours.json', 'full_subjects_study_plan.json']
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, extra_files=json_files)