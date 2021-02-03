##GOOGLE
from __future__ import print_function
import datetime
import pytz
import pickle
import vobject
import csv

import os
import sys
import time
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def parseICS(classes_to_ignore):

    mypath = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir('temp'):
        os.mkdir('temp')

    print('Parsing .ics files to csv')
    with open(os.path.join(mypath,"temp",'events.csv'), mode='w',encoding='latin1') as csv_out:
        csv_writer = csv.writer(csv_out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['WHAT', 'WHERE', 'FROM', 'TO', 'DESCRIPTION','CATEGORY'])

        # read the data from the file
        Cals = {}
        for f in os.listdir(mypath + '/Calendars') :
            if 'pdf' not in f:
                #print(mypath + '\Calendars\\' + f)
                print(f)
                Cals[f[:-4]] = open((mypath + '/Calendars/' + f),encoding= 'latin-1').read()

        # iterate through the contents of the .ics corresponding to the calendar of the first semester
        ignored_count = 0
        try:
            for key in Cals:
                for cal in vobject.readComponents(Cals[key]):
                    for component in cal.components():
                        if component.name == "VEVENT":
                            event_name = restoreAccents(component.summary.valueRepr())
                            if event_name.replace(" ","").lower().split(",")[0] in classes_to_ignore:
                                #print(event_name, "event ignored")
                                ignored_count += 1
                                continue
                            # # write to csv
                            csv_writer.writerow([event_name,
                                                restoreAccents(component.location.valueRepr()),
                                                component.dtstart.valueRepr(),
                                                component.dtend.valueRepr(),
                                                restoreAccents(component.description.valueRepr()),
                                                component.categories.valueRepr()])
                print(ignored_count,"events ignored")
                print(str(key),'succesfuly parsed')
        except Exception as e:
            print(e)
            print("There was an error parsing the calendar(s)")
            return False
        return True


def get_utc_offset_from_raw_datetime(raw_datetime):

    dt_dt = datetime.datetime.strptime(raw_datetime, '%Y-%m-%d %H:%M:%S')
    dt_dt_utc = pytz.utc.localize(dt_dt)
    dt_dt_local = pytz.timezone('Europe/Madrid').localize(dt_dt)
    offset = (max(dt_dt_utc,dt_dt_local) - min(dt_dt_utc,dt_dt_local)).seconds//3600

    return offset

#Google Calendar API Integration:
SCOPES = ['https://www.googleapis.com/auth/calendar']
def importToGoogleCalendar(calname):
    """
    Creates a new "Horario de clases" calendar and imports all the events from the calendar parsed to a csv file into it.
    """
    print('Importing parsed events to google calendar. Google authentication may be required')
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('temp/token.pickle'):
        with open('temp/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'util/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('temp/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Call the Calendar API
    service = build('calendar', 'v3', credentials=creds)
    print("Succesfuly called the google calendar API application")

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    #GET A LIST OF ALL THE CALENDARS
    calendar_list = service.calendarList().list().execute()
    myCalendars = {}
    for i in range(0,len(calendar_list['items'])):
        myCalendars[calendar_list['items'][i]['summary']] = calendar_list['items'][i]['id']

    # CREATE NEW CALENDAR AND IMPORT ALL THE CLASS EVENTS THERE
    newCalendarName = 'Horario de Clases ' + getYearInterval() if (calname == "None" or calname is None) else calname
    calId=None
    if newCalendarName in myCalendars:
        print(f"{newCalendarName} calendar already exists. Clearing all events from this calendar before adding the new ones.")
        print("(This might take a while...)")
        #CLEAR CALENDAR SINCE ANOTHER WITH THE SAME NAME EXISTS ALREADY
        calId = myCalendars[newCalendarName]
        count = 0
        # print(service.events().list(calendarId=calId).execute())
        for event_item in service.events().list(calendarId = calId).execute()['items']:
            event_id = event_item['id']
            service.events().delete(calendarId=calId, eventId=event_id).execute()
            count += 1
            time.sleep(0.1) #To make sure that the api's user rate limit is not exceeded
        print(count,"events removed")
        print('Previous calendar ("'+ newCalendarName + ')" cleared. Class events will be imported here')
        # return

    if calId is None:
        calendar = {
                'summary': newCalendarName,
                'description':'Este calendario fue creado usando HorarioDeClases_app disponible en github.com/simonsanvil',
                'timeZone': 'Europe/Madrid'
        }
        new_calendar = service.calendars().insert(body=calendar).execute()
        print("calendar '" + newCalendarName + "' created")
    else:
        new_calendar = service.calendars().get(calendarId= myCalendars[newCalendarName]).execute()

    #IMPORT ALL THE EVENTS FROM CSV TO GOOGLE CALENDAR...
    print('Importing events to "%s" calendar. This might take a while...'%newCalendarName)
    eventList = getEventListFromCSV()

    for event in eventList:

        offset = get_utc_offset_from_raw_datetime(event[2])
        ftime = '%Y-%m-%dT%H:%M:%S+' + str(int(offset)).zfill(2) + ':00'

        startTime = datetime.datetime.strptime(event[2],'%Y-%m-%d %H:%M:%S').strftime(ftime)

        offset = get_utc_offset_from_raw_datetime(event[3])
        ftime = '%Y-%m-%dT%H:%M:%S+' + str(int(offset)).zfill(2) + ':00'

        endTime = datetime.datetime.strptime(event[3],'%Y-%m-%d %H:%M:%S').strftime(ftime)
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
        time.sleep(0.1) #To make sure that the api's user rate limit is not exceeded
    print('All events have been imported')

def getEventListFromCSV():
    """
    Creates a python list containing each event row from the events csv as it's elements
    """
    if not os.path.isdir('temp'):
        os.mkdir('temp')
    
    fname = os.path.join("temp","events.csv")
    with open(fname, newline = '') as f:
        csv_reader = csv.reader(f)
        try:
            eventList = []
            for row in csv_reader:
                eventList.append(row)
            eventList = list(filter(lambda a: a != [] ,eventList))
            eventList.pop(0)
            return eventList
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(fname, csv_reader.line_num, e))
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

# if parseICS():
#     importToGoogleCalendar()
