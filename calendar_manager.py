import pickle
import sys, os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import ssl, certifi
import urllib.request

from definitions import LessonStatus, get_base_path

# If modifying these SCOPES, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarManager():

    def __init__(self):
        self.credentials = None
        self.service = None
        self.time_zone = ZoneInfo("Europe/Berlin")
        self.internet_connection_present = False

    def start(self):
        # Check for internet connection
        if not ConnectionChecker.is_internet_connection_present():
            self.internet_connection_present = False
            print("No internet connection available. Cannot authenticate now.")
            return
        self.internet_connection_present = True

        base_path = get_base_path()
        credentials_path = os.path.join(base_path, "credentials.json")
        token_path = os.path.join(base_path, "token.pickle")

        # Check if credentials.json exists
        if not os.path.exists(credentials_path):
            print("Error: Missing 'credentials.json'.")
            print("Please place your Google API credentials file next to the program.")
            sys.exit(1)

        # Load credentials if already saved
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                self.credentials = pickle.load(token)
        try:
            # If no (valid) credentials available, let the user log in.
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    self.credentials = flow.run_local_server(port=8081,
                                                            access_type="offline",  # important: gives you a refresh token)
                                                            prompt="consent")       # important: forces Google to issue a refresh token even if previously authorized
                # Save credentials
                with open(token_path, "wb") as token:
                    pickle.dump(self.credentials, token)

        except RefreshError:
            # Token has expired or is revoked -> delete and force re-login
            print("Refresh failed, clearing saved token and requesting new login.")
            if os.path.exists(token_path):
                os.remove(token_path)

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            self.credentials = flow.run_local_server(
                port=8081,
                access_type="offline",
                prompt="consent"
            )

            # Save the new credentials token
            with open(token_path, "wb") as token:
                pickle.dump(self.credentials, token)

        if self.credentials and self.credentials.valid:
            self.service = build("calendar", "v3", credentials=self.credentials)

    # def create_event(self, name, date, start, end):
    #     # ISO format example 2025-09-09T13:00:00
    #     local_timezone = ZoneInfo("Europe/Berlin")

    #     event = {
    #         "summary": name,
    #         "start": {"dateTime": f"{date}T{start}:00", 'timeZone': str(local_timezone)},
    #         "end": {"dateTime": f"{date}T{end}:00", 'timeZone': str(local_timezone)},
    #         "colorId": "2", # green
    #     }
    #     event = self.service.events().insert(calendarId='primary', body=event).execute()
    
    def create_event(self, calendar_event):
        start_time = f"{calendar_event.date}T{calendar_event.start_hour}:00"
        duration_in_hours = calendar_event.duration // 60
        end_time = (datetime.fromisoformat(start_time) + timedelta(hours=duration_in_hours)).isoformat()
        event = {
            "summary": calendar_event.name,
            "start": {"dateTime": start_time, 'timeZone': str(self.time_zone)},
            "end": {"dateTime": end_time, 'timeZone': str(self.time_zone)},
            "colorId": calendar_event.status,
        }
        event = self.service.events().insert(calendarId='primary', body=event).execute()

    def edit_event(self, event, **kwargs):
        if "color_id" in kwargs:
            self.service.events().patch(calendarId='primary', eventId=event['id'], body={"colorId": kwargs["color_id"]}).execute()


    def get_events_in_selected_period(self, start_of_period, end_of_period):
        events_result = self.service.events().list(calendarId='primary',
                                            timeMin=start_of_period.isoformat(),
                                            timeMax=end_of_period.isoformat(),
                                            singleEvents=True,
                                            orderBy='startTime').execute()    
        events = events_result.get('items', [])
        return events
    
    def get_student_lessons_in_selected_period(self, student_name, start_of_period, end_of_period):
        events_result = self.service.events().list(calendarId='primary',
                                                q=student_name,
                                                timeMin=start_of_period.isoformat(),
                                                timeMax=end_of_period.isoformat(),
                                                singleEvents=True,
                                                orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def routine(self):
        local_timezone = ZoneInfo("Europe/Berlin")

        # Start of this week (Monday 00:00 local time)
        now = datetime.now(local_timezone)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        # End of this week (Sunday 23:59:59)
        end_of_week = start_of_week + timedelta(days=7, seconds=-1)
        print("Week:", start_of_week, "→", end_of_week)

        now = datetime.now(local_timezone)
        end = now + timedelta(hours=1)
        start_time = datetime(2025, 9, 6, 15, tzinfo=local_timezone)
        end_time = start_time + timedelta(hours=1)

        event = {
            'summary': 'Test Event',
            'start': {'dateTime': start_time.isoformat(), 'timeZone': str(local_timezone)},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': str(local_timezone)},
            'colorId': '2', # green
        }

        event = self.service.events().insert(calendarId='primary', body=event).execute()
        print("Created:", event.get('htmlLink'))

        events_result = self.service.events().list(calendarId='primary',
                                            timeMin=start_of_week.isoformat(),
                                            timeMax=end_of_week.isoformat(),
                                            singleEvents=True,
                                            orderBy='startTime').execute()
        
        events = events_result.get('items', [])

        if not events:
            print("No events this week.")
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(event['id'], event['summary'], "→", start)
                end = event['end'].get('dateTime', event['end'].get('date'))
                if end < now.isoformat():
                    self.service.events().patch(calendarId='primary', eventId=event['id'], body={"colorId": "4"}).execute()


class CalendarEvent:

    def __init__(self,
                name,
                date=datetime.today().strftime("%Y-%m-%d"), 
                start_hour=datetime.now(ZoneInfo("Europe/Berlin")).strftime("%H:%M"),
                duration=45,
                status=str(LessonStatus.PENDING.value)):
        self.name = name
        self.date = date
        self.start_hour = start_hour
        self.duration = duration
        self.status = status

class ConnectionChecker():

    """
    Check internet connection by trying to reach https://www.google.com.
    Returns True if connected, False otherwise.
    """

    @staticmethod
    def is_internet_connection_present() -> bool:
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            urllib.request.urlopen("https://www.google.com", timeout=5, context=ssl_context)
            return True
        except Exception:
            return False