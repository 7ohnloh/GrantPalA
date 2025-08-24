import os
import json
import datetime as dt
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- Configuration ---
# Option A: Path to JSON file (local dev)
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "services/service_account.json")

# Option B: JSON string stored directly in env var (cloud deploy)
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# Calendar to use (must be shared with the service account!)
CALENDAR_ID = os.getenv("GOOGLE_SHARED_CALENDAR_ID", "beingthebridges@gmail.com")

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _get_service():
    creds = None

    if SERVICE_ACCOUNT_JSON:  # Prefer env var if present
        try:
            creds = service_account.Credentials.from_service_account_info(
                json.loads(SERVICE_ACCOUNT_JSON), scopes=SCOPES
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load credentials from env var: {e}")

    elif os.path.exists(SERVICE_ACCOUNT_FILE):
        try:
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load credentials from file: {e}")

    else:
        raise FileNotFoundError(
            "No Google service account credentials found. "
            "Set SERVICE_ACCOUNT_FILE path or GOOGLE_SERVICE_ACCOUNT_JSON env var."
        )

    return build("calendar", "v3", credentials=creds)


def create_calendar_event(title: str, description: str, due_date_str: str) -> dict:
    """
    Create an ALL-DAY event on 'due_date_str' (YYYY-MM-DD).
    Using all-day avoids time zone edge cases with service accounts.
    Returns the created event JSON (with 'id', 'htmlLink', etc.).
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
        "end": {"date": end_date, "timeZone": "Asia/Singapore"},
    }

    service = _get_service()
    created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"✅ Event created: {created.get('htmlLink')}")
    return created
