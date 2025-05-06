# 📅 Google Calendar Agent 

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Google Calendar API](https://img.shields.io/badge/Google%20Calendar%20API-v3-yellow.svg)

 AI Calendar Agent that seamlessly integrates with Google Calendar API  to provide intelligent meeting management capabilities!

## 🌟 Key Features

### Meeting Views
- **Today's Meetings** - Instant daily schedule overview
- **Upcoming Meetings** - Future event calendar
- **Past Meetings** - Historical meeting reference

### Meeting Management
- **Create Meetings** - Schedule with attendees, descriptions, and reminders
- **Edit Meetings** - Modify details with automatic attendee notifications
- **Delete Meetings** - Remove events with confirmation

### Advanced Tools
- **Keyword Search** - Find meetings across titles/descriptions
- **Time Zone Support** - Automatic PST  handling
- **Responsive UI** - Mobile-friendly interface

## 🛠️ Technical Stack

| Component           | Technology Used                |
|---------------------|--------------------------------|
| Backend Framework   | Flask                          |
| Authentication      | Google OAuth 2.0               |
| Calendar Integration| Google Calendar API v3         |
| Timezone Handling   | pytz (Pakistan Standard Time)  |
| Frontend            | HTML5, CSS3, Vanilla JavaScript|
| Session Management  | Flask Sessions                 |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Platform project with Calendar API enabled
- OAuth 2.0 credentials (`credentials.json`)

### Installation
```bash
git clone https://github.com/arqam-dev/agentic-AI.git
cd google-calendar-agent
pip install -r requirements.txt