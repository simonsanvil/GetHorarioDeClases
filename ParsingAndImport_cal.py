##GOOGLE
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import vobject
import csv
import os
import sys
import time


os.chdir(os.path.dirname(os.path.realpath(__file__)))

def parseICS():

    print('Parsing .ics files to csv')
    with open('events.csv', mode='w') as csv_out:
        csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['WHAT', 'WHERE', 'FROM', 'TO', 'DESCRIPTION','CATEGORY'])

        # read the data from the file
        dataQ1 = open("horario_Q1.ics", encoding = 'utf-8').read()
        dataQ2 = open("horario_Q2.ics", encoding = 'utf-8').read()

        # iterate through the contents of the .ics corresponding to the calendar of the first semester
        try:
            for cal in vobject.readComponents(dataQ1):
                for component in cal.components():
                    if component.name == "VEVENT":
                        a = 2
                        # # write to csv
                        csv_writer.writerow([restoreAccents(component.summary.valueRepr()) ,
                                            restoreAccents(component.location.valueRepr()),
                                            component.dtstart.valueRepr(),
                                            component.dtend.valueRepr(),
                                            restoreAccents(component.description.valueRepr()),
                                            component.categories.valueRepr()])
            print('Q1.ics succesfuly parsed')
        except:
            print("There was an error parsing horario_Q1.ics")
            return False
        # iterate through the contents of the .ics corresponding to the calendar of the second semeste
        try:
            for cal in vobject.readComponents(dataQ2):
                for component in cal.components():
                    if component.name == "VEVENT":
                        a = 2
                        # # write to csv
                        csv_writer.writerow([restoreAccents(component.summary.valueRepr()) ,
                                            restoreAccents(component.location.valueRepr()),
                                            component.dtstart.valueRepr(),
                                            component.dtend.valueRepr(),
                                            restoreAccents(component.description.valueRepr()),
                                            component.categories.valueRepr()])
            print('Q2.ics succesfuly parsed')
        except:
            print("There was an error parsing horario_Q2.ics")
            return False

        return True

#Google Calendar API Integration:
SCOPES = ['https://www.googleapis.com/auth/calendar']
def importToGoogleCalendar():
    """
    Creates a new "Horario de clases" calendar and imports all the events from the calendar parsed to a csv file in to it.
    """
    print('Importing parsed events to google calendar. Google authentication may be required')
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    #GET A LIST OF ALL THE CALENDARS
    calendar_list = service.calendarList().list().execute()
    myCalendars = {}
    for i in range(0,len(calendar_list['items'])):
        myCalendars[calendar_list['items'][i]['summary']] = calendar_list['items'][i]['id']

    # CREATE NEW CALENDAR AND IMPORT ALL THE CLASS EVENTS THERE
    newCalendarName = 'Horario de Clases ' + getYearInterval()
    if newCalendarName in myCalendars:
        #DELETE 'HORARIO DE CLASES' CALENDAR IF ANOTHER EXISTS ALREADY
        service.calendars().delete(calendarId= myCalendars[newCalendarName]).execute()
        print('Previous calendar ("'+ newCalendarName + ')" deleted')

    print('Creating new "Horario de Clases" calendar')
    calendar = {
            'summary': newCalendarName,
            'description':'Este calendario fue creado usando HorarioDeClases_app disponible en github.com/simonsanvil',
            'timeZone': 'Europe/Madrid'
    }
    new_calendar = service.calendars().insert(body=calendar).execute()
    print("calendar '" + newCalendarName + "' created")
    #IMPORT ALL THE EVENTS FROM CSV TO GOOGLE CALENDAR...
    print('Importing events to new calendar. This might take a while...')
    eventList = getEventListFromCSV()
    offset = (datetime.datetime.now() - datetime.datetime.utcnow()).seconds/3600
    ftime = '%Y-%m-%dT%H:%M:%S+' + str(int(offset)).zfill(2) + ':00'
    for event in eventList:
        startTime = d = datetime.datetime.strptime(event[2],'%Y-%m-%d %H:%M:%S').strftime(ftime)
        endTime = d = datetime.datetime.strptime(event[3],'%Y-%m-%d %H:%M:%S').strftime(ftime)
        CalendarEvent = {
              'summary': event[0],
              'location': event[1],
              'description': event[4],
              'start': {
                'dateTime': startTime,
                'timeZone': 'Europe/Madrid',
              },
              'end': {
                'dateTime': endTime,
                'timeZone': 'Europe/Madrid',
              },
              'reminders': {
                'useDefault': False,
                'overrides': [
                  {'method': 'popup', 'minutes': 20},
                  ],
              },
              #'colorId':'4',
        }
        newEvent = service.events().insert(calendarId=new_calendar['id'], body=CalendarEvent).execute()
        print('Event created: %s %s' %(newEvent['summary'],newEvent['start']['dateTime']))
        time.sleep(0.15) #To make sure the api's user rate limit is not exceeded
    print('All events have been imported')

def getEventListFromCSV():
    """
    Creates a python list containing each event row from the events csv as it's elements
    """
    with open('events.csv', newline = '') as f:
        csv_reader = csv.reader(f)
        try:
            eventList = []
            for row in csv_reader:
                eventList.append(row)
            eventList = list(filter(lambda a: a != [] ,eventList))
            eventList.pop(0)
            return eventList
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))
            return None

def restoreAccents(s):
    s = s.replace('Ã¡','á')
    s = s.replace('Ã³','ó')
    s = s.replace('Ã©','é')

    s = s.replace('Ã±','ñ')
    s = s.replace('Ã­','í')

    return s

def getYearInterval():
    now = datetime.datetime.now()
    if now.month < 9:
        YearInterval = str(now.year-1) + '/' + str(now.year)
    else:
        YearInterval = str(now.year) + '/' + str(now.year+1)
    return YearInterval

if parseICS():
    importToGoogleCalendar()
