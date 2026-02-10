#!/usr/bin/env python3
"""
Google Calendar Tool for OpenClaw
Provides CLI commands to interact with Google Calendar via Service Account.
Usage: python calendar_tool.py <command> [args]
"""
import sys
import os
import datetime
import json

# Set default timezone to Madrid for convenience
TIMEZONE = 'Europe/Madrid'

def get_service():
    """Authenticate and return Calendar service."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Missing dependencies. Run: pip install google-auth google-api-python-client")
        sys.exit(1)

    # Re-use credential logic from drive_tool
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Method 2: JSON content in env var (Codespaces)
    if not creds_path or not os.path.exists(creds_path or ''):
        json_content = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if json_content:
            creds_path = '/tmp/gsa_credentials.json'
            # Only write if it doesn't exist or is empty
            if not os.path.exists(creds_path) or os.path.getsize(creds_path) == 0:
                with open(creds_path, 'w') as f:
                    f.write(json_content)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        else:
            print("ERROR: No credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON.")
            sys.exit(1)

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def get_target_calendar_id(service):
    """Find a calendar shared with the service account (user email)."""
    calendar_list = service.calendarList().list().execute()
    calendars = calendar_list.get('items', [])
    
    for cal in calendars:
        # Prefer a gmail address that isn't the service account itself
        if 'gserviceaccount.com' not in cal['id'] and '@' in cal['id']:
            return cal['id']
            
    return None

def cmd_list(service, args):
    """List 10 upcoming events."""
    target_id = get_target_calendar_id(service)
    if not target_id:
        print("ERROR: No shared user calendar found. Did you share your calendar with the Service Account?")
        return

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    
    print(f"📅 Reading calendar: {target_id}\n")
    
    events_result = service.events().list(calendarId=target_id, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print("No upcoming events found.")
        return

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"  🕒 {start} - {event['summary']}")

def cmd_create(service, args):
    """Create a new event."""
    if len(args) < 4:
        print('Usage: create "YYYY-MM-DD" "HH:MM" "Duration(mins)" "Title"')
        return

    date_str, time_str, duration_str, title = args[0], args[1], args[2], args[3]
    
    target_id = get_target_calendar_id(service)
    if not target_id:
        print("ERROR: No shared user calendar found.")
        return

    start_datetime_str = f"{date_str}T{time_str}:00"
    
    try:
        start_dt = datetime.datetime.fromisoformat(start_datetime_str)
        end_dt = start_dt + datetime.timedelta(minutes=int(duration_str))
        
        event = {
            'summary': title,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': TIMEZONE,
            },
        }

        created_event = service.events().insert(calendarId=target_id, body=event).execute()
        print(f"✅ Event created: {created_event.get('htmlLink')}")
            
    except Exception as e:
        print(f"Error creating event: {e}")

def main():
    if len(sys.argv) < 2:
        print("Google Calendar Tool for OpenClaw")
        print("Commands: list, create")
        print("Usage: python calendar_tool.py <command> [args]")
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    service = get_service()
    
    if command == 'list':
        cmd_list(service, args)
    elif command == 'create':
        cmd_create(service, args)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
