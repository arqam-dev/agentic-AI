from flask import Flask, redirect
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

# Configuration
CLIENT_SECRETS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = 'token.json'
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]
PAKISTAN_TZ = pytz.timezone('Asia/Karachi')

# HTML/CSS Template
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
        display: block;
        padding: 12px 20px;
        background-color: var(--primary-color);
        color: white;
        text-decoration: none;
        border-radius: var(--border-radius);
        text-align: center;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: var(--box-shadow);
        border: none;
        cursor: pointer;
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
        margin-bottom: 10px;
        background: var(--light-color);
        border-radius: var(--border-radius);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .meeting-time {
        color: #666;
        font-size: 0.9em;
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
    
    @media (max-width: 600px) {
        .container {
            padding: 20px;
            margin: 20px;
        }
    }
</style>
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

# Calendar Service Functions
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

# Routes
@app.route('/')
def index():
    content = """
    <div class="menu">
        <a href="/meetings" class="btn btn-primary">View All My Meetings</a>
        <a href="/create_meeting" class="btn btn-secondary">Create Test Meeting</a>
        <a href="/clear_token" class="btn btn-warning">Clear Authentication</a>
    </div>
    """
    return render_page("AI Calendar Agent", content)

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
            
            meetings_html += f"""
            <div class="meeting-item">
                <span><strong>{event.get('summary', 'No Title')}</strong></span>
                <span class="meeting-time">{time_str}</span>
            </div>
            """

        content = f"""
        <h2>Welcome, {user_name}!</h2>
        <p>Email: {user_email}</p>
        <h3>Your Meetings</h3>
        <div class="meeting-list">
            {meetings_html if events else "<p>No meetings found.</p>"}
        </div>
        <div class="menu">
            <a href="/" class="btn btn-primary">Back to Home</a>
            <a href="/create_meeting" class="btn btn-secondary">Create New Meeting</a>
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

@app.route('/create_meeting')
def create_meeting():
    try:
        creds, service = get_calendar_service()
        if not creds or not creds.valid:
            return redirect('/')

        # Create meeting 1 hour from now
        start_dt = datetime.datetime.now(PAKISTAN_TZ) + datetime.timedelta(hours=1)
        end_dt = start_dt + datetime.timedelta(hours=1)

        event = {
            'summary': 'Test Meeting from Flask App',
            'description': 'Automatically created by the Flask Calendar Integration',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Karachi',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Karachi',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        content = f"""
        <div class="success-message">
            <h3>Meeting Created Successfully!</h3>
            <p><strong>Title:</strong> {created_event.get('summary')}</p>
            <p><strong>Time:</strong> {start_dt.strftime('%d %b %Y, %I:%M %p')}</p>
            <p><strong>Duration:</strong> 1 hour</p>
            <a href="{created_event.get('htmlLink')}" target="_blank" class="btn btn-secondary">View in Calendar</a>
        </div>
        <div class="menu">
            <a href="/meetings" class="btn btn-primary">View All Meetings</a>
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
        """
        return render_page("Meeting Created", content)

    except Exception as e:
        error_content = f"""
        <div class="error-message">
            <h3>Error Creating Meeting</h3>
            <p>{str(e)}</p>
        </div>
        <div class="menu">
            <a href="/" class="btn btn-primary">Back to Home</a>
            <a href="/meetings" class="btn btn-secondary">View Meetings</a>
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