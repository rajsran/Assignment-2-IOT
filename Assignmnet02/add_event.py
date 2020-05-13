# pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client httplib2
# python3 add_event.py --noauth_local_webserver

# Reference: https://developers.google.com/calendar/quickstart/python
# Documentation: https://developers.google.com/calendar/overview

# Be sure to enable the Google Calendar API on your Google account by following the reference link above and
# download the credentials.json file and place it in the same directory as this file.

from datetime import datetime
from datetime import timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from flask import request

# If modifying these scopes, delete the file token.json.
class CalendarEvent:
    start_date = None
    booking_id = None
    start_location = None
    
    def __init__(self, start_date, booking_id, start_location):
        self.start_date = start_date
        self.booking_id = booking_id
        self.start_location = start_location
    


    def addToCalendar(self, carnumber,service):
        SCOPES = "https://www.googleapis.com/auth/calendar"
        s = "token_"+request.args['user']+".json"
        store = file.Storage(s)
        creds = store.get()
        if(not creds or creds.invalid):
            flow = client.flow_from_clientsecrets("client_auth.json", SCOPES)
            creds = tools.run_flow(flow, store)
        service = build("calendar", "v3", credentials=creds)
        date = self.start_date
        tomorrow = date.strftime("%Y-%m-%d")
        time_start = "{}T06:00:00+10:00".format(tomorrow)
        time_end = "{}T07:00:00+10:00".format(tomorrow)
        event = {
            "summary": self.booking_id,
            "location": self.start_location,
            "description": "car share booking pickup" + carnumber,
            "start": {
                "dateTime": time_start,
                "timeZone": "Australia/Melbourne",
            },
            "end": {
                "dateTime": time_end,
                "timeZone": "Australia/Melbourne",
            },
            "attendees": [
               
            ],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    { "method": "email", "minutes": 5 },
                    { "method": "popup", "minutes": 10 },
                ],
            }
        }

        event = service.events().insert(calendarId = "primary", body = event).execute()
        print("Event created: {}".format(event.get("htmlLink")))
        return(event.get("htmlLink"))

    def removeFromCalendar(self, event_id,services):
        SCOPES = "https://www.googleapis.com/auth/calendar"
        s = "token_"+request.args['user']+".json"
        store = file.Storage(s)
        creds = store.get()
        if(not creds or creds.invalid):
            flow = client.flow_from_clientsecrets("client_auth.json", SCOPES)
            creds = tools.run_flow(flow, store)
        service = build("calendar", "v3", credentials=creds)
        page_token = None
        while True:
          events = service.events().list(calendarId='primary', pageToken=page_token).execute()
          for event in events['items']:
            if (event['id'] == event_id):
                break
          page_token = events.get('nextPageToken')
          if not page_token:
            break
        service.events().delete(calendarId='primary', eventId=event['id']).execute()
        
