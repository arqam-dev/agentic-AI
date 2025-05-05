from flask import Flask, redirect, request
import datetime
import os
import requests
import json
import pytz

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-me')


CLIENT_SECRETS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = 'token.json'
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]
PAKISTAN_TZ = pytz.timezone('Asia/Karachi')


BASE_STYLE = """
<style>
    :root {
        --primary-color: #4285F4;
        --secondary-color: #34A853;
        --accent-color: #EA4335;
        --light-color: #f8f9fa;
        --dark-color: #202124;
        --border-radius: 8px;
        --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    body {
        background-color: #f5f5f5;
        color: var(--dark-color);
        line-height: 1.6;
        padding: 20px;
    }
    
    .container {
        max-width: 800px;
        margin: 40px auto;
        padding: 30px;
        background: white;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
    }
    
    h1, h2, h3 {
        color: var(--primary-color);
        margin-bottom: 20px;
    }
    
    .logo {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .logo svg {
        width: 48px;
        height: 48px;
        color: var(--primary-color);
    }
    
    .menu {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin: 25px 0;
    }
    
    .btn {
        display: inline-block;
        padding: 10px 15px;
        color: white;
        text-decoration: none;
        border-radius: var(--border-radius);
        text-align: center;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: var(--box-shadow);
        border: none;
        cursor: pointer;
        margin: 2px;
    }
    
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    .btn-primary {
        background-color: var(--primary-color);
    }
    
    .btn-primary:hover {
        background-color: #3367d6;
    }
    
    .btn-secondary {
        background-color: var(--secondary-color);
    }
    
    .btn-secondary:hover {
        background-color: #2d9249;
    }
    
    .btn-warning {
        background-color: var(--accent-color);
    }
    
    .btn-warning:hover {
        background-color: #d33426;
    }
    
    .meeting-list {
        list-style: none;
        margin: 20px 0;
    }
    
    .meeting-item {
        padding: 15px;
        margin-bottom: 15px;
        background: var(--light-color);
        border-radius: var(--border-radius);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .meeting-details {
        flex: 1;
        min-width: 200px;
    }
    
    .meeting-time {
        color: #666;
        font-size: 0.9em;
    }
    
    .meeting-actions {
        display: flex;
        gap: 5px;
        margin-top: 10px;
    }
    
    .attendee-list {
        margin-top: 10px;
        font-size: 0.9em;
        color: #555;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #666;
        font-size: 0.9rem;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: var(--border-radius);
        margin: 20px 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: var(--border-radius);
        margin: 20px 0;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    label {
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    input[type="text"],
    input[type="datetime-local"],
    input[type="email"],
    textarea,
    select {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: var(--border-radius);
        font-size: 16px;
    }
    
    textarea {
        min-height: 100px;
        resize: vertical;
    }
    
    .attendee-inputs {
        margin-bottom: 10px;
    }
    
    .add-attendee-btn {
        margin-bottom: 20px;
        background-color: #f8f9fa;
        color: var(--primary-color);
        border: 1px solid var(--primary-color);
    }
    
    .add-attendee-btn:hover {
        background-color: #e8f0fe;
    }
    
    @media (max-width: 600px) {
        .container {
            padding: 20px;
            margin: 20px;
        }
        
        .meeting-item {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .meeting-actions {
            align-self: flex-end;
        }
    }
</style>
<script>
    function addAttendeeField() {
        const container = document.getElementById('attendee-fields');
        const newField = document.createElement('div');
        newField.className = 'form-group attendee-inputs';
        newField.innerHTML = `
            <label>Attendee Email</label>
            <input type="email" name="attendees" placeholder="participant@example.com">
        `;
        container.appendChild(newField);
    }
    
    function confirmDelete(eventId) {
        return confirm('Are you sure! you want to delete this meeting?');
    }
</script>
"""

BASE_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Calendar Agent</title>
    {style}
</head>
<body>
    <div class="container">
        <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
        </div>
"""

BASE_FOOTER = """
        <div class="footer">
            <p>Powered by Google Calendar API</p>
        </div>
    </div>
</body>
</html>
"""

def render_page(title, content):
    return f"""
    {BASE_HEADER.format(style=BASE_STYLE)}
        <h1>{title}</h1>
        {content}
    {BASE_FOOTER}
    """

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except json.JSONDecodeError:
            os.remove(TOKEN_FILE)
            return get_calendar_service()
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                os.remove(TOKEN_FILE)
                return get_calendar_service()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds, build('calendar', 'v3', credentials=creds)

def get_user_info(creds):
    try:
        user_info_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {creds.token}'}
        response = requests.get(user_info_endpoint, headers=headers)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"Error getting user info: {e}")
        return {}

@app.route('/')
def index():
    content = """
    <div class="menu">
        <a href="/meetings" class="btn btn-primary">View All My Meetings</a>
        <a href="/create_meeting_form" class="btn btn-secondary">Create New Meeting</a>
        <a href="/clear_token" class="btn btn-warning">Clear Authentication</a>
    </div>
    """
    return render_page("AI Calendar Agent", content)

@app.route('/create_meeting_form')
def create_meeting_form():
    default_start = (datetime.datetime.now(PAKISTAN_TZ) + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
    default_end = (datetime.datetime.now(PAKISTAN_TZ) + datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
    
    content = f"""
    <form method="POST" action="/create_meeting">
        <div class="form-group">
            <label for="title">Meeting Title</label>
            <input type="text" id="title" name="title" required placeholder="Team Standup">
        </div>
        
        <div class="form-group">
            <label for="description">Description</label>
            <textarea id="description" name="description" placeholder="Meeting agenda..."></textarea>
        </div>
        
        <div class="form-group">
            <label for="start_time">Start Time</label>
            <input type="datetime-local" id="start_time" name="start_time" value="{default_start}" required>
        </div>
        
        <div class="form-group">
            <label for="end_time">End Time</label>
            <input type="datetime-local" id="end_time" name="end_time" value="{default_end}" required>
        </div>
        
        <div class="form-group">
            <label>Attendees</label>
            <div id="attendee-fields">
                <div class="form-group attendee-inputs">
                    <input type="email" name="attendees" placeholder="participant@example.com">
                </div>
            </div>
            <button type="button" class="btn add-attendee-btn" onclick="addAttendeeField()">+ Add Another Attendee</button>
        </div>
        
        <div class="form-group">
            <button type="submit" class="btn btn-primary">Create Meeting</button>
            <a href="/" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
    """
    return render_page("Create New Meeting", content)

@app.route('/create_meeting', methods=['POST'])
def create_meeting():
    try:
        title = request.form.get('title', 'New Meeting')
        description = request.form.get('description', '')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        attendees = request.form.getlist('attendees')
        
        if not start_time_str or not end_time_str:
            raise ValueError("Start and end times are required")
            
        start_dt_naive = datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        end_dt_naive = datetime.datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        
        start_dt = PAKISTAN_TZ.localize(start_dt_naive)
        end_dt = PAKISTAN_TZ.localize(end_dt_naive)
        
        if start_dt >= end_dt:
            raise ValueError("End time must be after start time")

        creds, service = get_calendar_service()
        if not creds or not creds.valid:
            return redirect('/')

        attendee_list = []
        for email in attendees:
            if email.strip():
                attendee_list.append({'email': email.strip()})

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Karachi',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Karachi',
            },
            'attendees': attendee_list,
            'reminders': {
                'useDefault': True,
            },
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'
        ).execute()

        duration = end_dt - start_dt
        duration_str = str(duration).split('.')[0]
        
        attendees_html = ""
        if created_event.get('attendees'):
            attendees_html = "<div class='attendee-list'><strong>Attendees:</strong><ul>"
            for attendee in created_event['attendees']:
                attendees_html += f"<li>{attendee['email']} ({attendee.get('responseStatus', 'no response')})</li>"
            attendees_html += "</ul></div>"
        
        content = f"""
        <div class="success-message">
            <h3>Meeting Created Successfully!</h3>
            <p><strong>Title:</strong> {created_event.get('summary')}</p>
            <p><strong>Time:</strong> {start_dt.strftime('%d %b %Y, %I:%M %p')} to {end_dt.strftime('%I:%M %p')}</p>
            <p><strong>Duration:</strong> {duration_str}</p>
            {attendees_html}
            <a href="{created_event.get('htmlLink')}" target="_blank" class="btn btn-secondary">View in Calendar</a>
        </div>
        <div class="menu">
            <a href="/meetings" class="btn btn-primary">View All Meetings</a>
            <a href="/create_meeting_form" class="btn btn-secondary">Create Another Meeting</a>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
        """
        return render_page("Meeting Created", content)

    except ValueError as e:
        error_content = f"""
        <div class="error-message">
            <h3>Invalid Input</h3>
            <p>{str(e)}</p>
        </div>
        <div class="menu">
            <a href="/create_meeting_form" class="btn btn-primary">Try Again</a>
            <a href="/" class="btn btn-secondary">Back to Home</a>
        </div>
        """
        return render_page("Error", error_content)
        
    except Exception as e:
        error_content = f"""
        <div class="error-message">
            <h3>Error Creating Meeting</h3>
            <p>{str(e)}</p>
        </div>
        <div class="menu">
            <a href="/create_meeting_form" class="btn btn-primary">Try Again</a>
            <a href="/" class="btn btn-secondary">Back to Home</a>
        </div>
        """
        return render_page("Error", error_content)

@app.route('/meetings')
def meetings():
    try:
        creds, service = get_calendar_service()
        if not creds or not creds.valid:
            return redirect('/')
        
        user_info = get_user_info(creds)
        user_name = user_info.get('name', 'Unknown')
        user_email = user_info.get('email', 'Unknown')

        now = datetime.datetime.now(PAKISTAN_TZ)
        time_min = (now - datetime.timedelta(days=365)).isoformat()
        time_max = (now + datetime.timedelta(days=365)).isoformat()

        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=2500,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
        except HttpError as error:
            error_content = f"""
            <div class="error-message">
                <p>Calendar API Error: {error}</p>
            </div>
            <a href="/" class="btn btn-primary">Back to Home</a>
            """
            return render_page("Error", error_content)

        meetings_html = ""
        for event in events:
            start = event.get('start', {})
            if 'dateTime' in start:
                dt = datetime.datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                dt = dt.astimezone(PAKISTAN_TZ)
                time_str = dt.strftime('%d %b %Y, %I:%M %p')
            elif 'date' in start:
                dt = datetime.datetime.fromisoformat(start['date'])
                time_str = dt.strftime('%d %b %Y')
            else:
                time_str = "No time specified"
            
            attendees_html = ""
            if event.get('attendees'):
                attendee_count = len(event['attendees'])
                attendees_html = f"<div class='attendee-list'>{attendee_count} attendee(s)</div>"
            
            meetings_html += f"""
            <div class="meeting-item">
                <div class="meeting-details">
                    <span><strong>{event.get('summary', 'No Title')}</strong></span>
                    <span class="meeting-time">{time_str}</span>
                    {attendees_html}
                </div>
                <div class="meeting-actions">
                    <a href="{event.get('htmlLink', '#')}" target="_blank" class="btn btn-secondary">View</a>
                    <form method="POST" action="/delete_meeting/{event['id']}" onsubmit="return confirmDelete('{event['id']}')">
                        <button type="submit" class="btn btn-warning">Delete</button>
                    </form>
                </div>
            </div>
            """

        content = f"""
        <h2>Welcome, {user_name}!</h2>
        <p>Email: {user_email}</p>
        <div class="success-message">
            <h3>Total Meetings Found: {len(events)}</h3>
        </div>
        <h3>Your Meetings</h3>
        <div class="meeting-list">
            {meetings_html if events else "<p>No meetings found.</p>"}
        </div>
        <div class="menu">
            <a href="/" class="btn btn-primary">Back to Home</a>
            <a href="/create_meeting_form" class="btn btn-secondary">Create New Meeting</a>
        </div>
        """
        return render_page("Your Meetings", content)

    except Exception as e:
        error_content = f"""
        <div class="error-message">
            <p>Error: {str(e)}</p>
        </div>
        <a href="/" class="btn btn-primary">Back to Home</a>
        """
        return render_page("Error", error_content)

@app.route('/delete_meeting/<event_id>', methods=['POST'])
def delete_meeting(event_id):
    try:
        creds, service = get_calendar_service()
        if not creds or not creds.valid:
            return redirect('/')

        service.events().delete(
            calendarId='primary',
            eventId=event_id,
            sendUpdates='all'
        ).execute()

        content = f"""
        <div class="success-message">
            <h3>Meeting Deleted Successfully!</h3>
            <p>The meeting has been removed from your calendar and attendees have been notified.</p>
        </div>
        <div class="menu">
            <a href="/meetings" class="btn btn-primary">Back to Meetings</a>
            <a href="/" class="btn btn-secondary">Back to Home</a>
        </div>
        """
        return render_page("Meeting Deleted", content)

    except HttpError as error:
        if error.resp.status == 404:
            error_content = f"""
            <div class="error-message">
                <h3>Meeting Not Found</h3>
                <p>The meeting you tried to delete doesn't exist or was already deleted.</p>
            </div>
            """
        else:
            error_content = f"""
            <div class="error-message">
                <h3>Error Deleting Meeting</h3>
                <p>{str(error)}</p>
            </div>
            """
        
        error_content += """
        <div class="menu">
            <a href="/meetings" class="btn btn-primary">Back to Meetings</a>
            <a href="/" class="btn btn-secondary">Back to Home</a>
        </div>
        """
        return render_page("Error", error_content)
        
    except Exception as e:
        error_content = f"""
        <div class="error-message">
            <h3>Error Deleting Meeting</h3>
            <p>{str(e)}</p>
        </div>
        <div class="menu">
            <a href="/meetings" class="btn btn-primary">Back to Meetings</a>
            <a href="/" class="btn btn-secondary">Back to Home</a>
        </div>
        """
        return render_page("Error", error_content)

@app.route('/clear_token')
def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)