import os
import datetime as dt
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- Configuration ---
# 1) Put your service account JSON on Render (or local) and set this env var to its path.
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "services/service_account.json")

# 2) Share a Google Calendar with the service account email (Make changes to events),
#    then put that Calendar ID here (or set GOOGLE_SHARED_CALENDAR_ID env var).
CALENDAR_ID = os.getenv("GOOGLE_SHARED_CALENDAR_ID", "beingthebridges@gmail.com")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def _get_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"SERVICE_ACCOUNT_FILE not found at '{SERVICE_ACCOUNT_FILE}'. "
            "Make sure the JSON key is present and the env var is set."
        )
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)

def create_calendar_event(title: str, description: str, due_date_str: str) -> dict:
    """
    Create an ALL-DAY event on 'due_date_str' (YYYY-MM-DD).
    Using all-day avoids time zone edge cases with service accounts.
    Returns the created event JSON (with 'id', 'htmlLink', etc.).

    IMPORTANT: The calendar identified by CALENDAR_ID must be shared
    with the service account email with 'Make changes to events'.
    """
    if not CALENDAR_ID:
        raise RuntimeError(
            "No CALENDAR_ID configured. Set GOOGLE_SHARED_CALENDAR_ID env var "
            "to the ID of a calendar shared with the service account."
        )

    try:
        date_obj = dt.date.fromisoformat(due_date_str)
    except Exception:
        raise ValueError("Invalid date format. Expected 'YYYY-MM-DD'.")

    # All-day events use 'date' (not 'dateTime'). End date is exclusive -> +1 day.
    start_date = date_obj.isoformat()
    end_date = (date_obj + dt.timedelta(days=1)).isoformat()

    event = {
        "summary": title or "Grant Deadline",
        "description": description or "",
        "start": {"date": start_date, "timeZone": "Asia/Singapore"},
        "end":   {"date": end_date,   "timeZone": "Asia/Singapore"},
    }

    service = _get_service()
    created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"✅ Event created: {created.get('htmlLink')}")
    return created
