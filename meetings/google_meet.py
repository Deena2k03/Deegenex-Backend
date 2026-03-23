import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.utils import timezone

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "credentials.json")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
# Ensure the subject matches your workspace admin/user
delegated_credentials = credentials.with_subject("hr@deegenex.com")
service = build("calendar", "v3", credentials=delegated_credentials)

def generate_meet_link(start_time, candidate_email):
    event = {
        "summary": "Deegenex Interview",
        "description": "Interview with Deegenex Team",
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": (start_time + datetime.timedelta(minutes=30)).isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [{"email": candidate_email}],
        "conferenceData": {
            "createRequest": {
                "requestId": f"interview-{datetime.datetime.now().timestamp()}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        }
    }
    event = service.events().insert(
        calendarId='primary', 
        body=event, 
        conferenceDataVersion=1,
        sendUpdates='none' # <--- THIS STOPS THE FIRST MAIL
    ).execute()
    return event.get("hangoutLink")

def get_free_slots(date_str):
    tz = timezone.get_current_timezone()
    start_dt = datetime.datetime.strptime(date_str + " 09:00:00", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.datetime.strptime(date_str + " 18:00:00", "%Y-%m-%d %H:%M:%S")
    
    start = timezone.make_aware(start_dt, tz)
    end = timezone.make_aware(end_dt, tz)

    body = {
        "timeMin": start.isoformat(),
        "timeMax": end.isoformat(),
        "timeZone": "Asia/Kolkata",
        "items": [{"id": "primary"}]
    }

    result = service.freebusy().query(body=body).execute()
    busy_times = result["calendars"]["primary"]["busy"]

    slots = []
    current = start
    while current < end:
        slot_end = current + datetime.timedelta(minutes=30)
        overlap = False
        for busy in busy_times:
            b_start = datetime.datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
            b_end = datetime.datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))
            if current < b_end and slot_end > b_start:
                overlap = True
                break
        if not overlap:
            slots.append(current.isoformat())
        current += datetime.timedelta(minutes=30)
    return slots