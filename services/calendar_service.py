from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

# Path to your downloaded service account key
SERVICE_ACCOUNT_FILE = 'services/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Your Google Calendar ID (get from calendar settings page)
CALENDAR_ID = 'beingthebridges@gmail.com'  # Replace with your actual calendar ID

def create_calendar_event(title, description, due_date_str):
    # Format: due_date_str = '2025-06-26'
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build('calendar', 'v3', credentials=creds)

    due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d")
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': due_date.isoformat(),
            'timeZone': 'Asia/Singapore',
        },
        'end': {
            'dateTime': (due_date + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'Asia/Singapore',
        },
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"✅ Event created: {created_event.get('htmlLink')}")
