#IMPORTS
from __future__ import print_function
import httplib2
import os
import datetime
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# SET VARIABLES/SHORTCUTS
now = datetime.datetime.now()

# DEFINE STUFF
def get_credentials(api_dict):
    credential_filename = 'python-roster_tools.json'
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir): os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,credential_filename)
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(api_dict['CLIENT_SECRET_FILE'], api_dict['SCOPES'])
        flow.user_agent = api_dict['APPLICATION_NAME']
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        #print('Storing credentials to ' + credential_path)
    #print('returning credentials...')
    api_dict['credentials'] = credentials

def get_shifts(sheet):
#    for item in ['credentials','service','range']:
#        if sheet[item]:
#            print("have",item)
#        else:
#            print("DON'T HAVE",item)
    #spreadsheetId = '19De960eh1EJC5GPAPMvSvKTHfJ30MYAUCJdGahVhMWM' #change this to change spreadsheets
    #rangeName = 'A2:B' #range of data to pull from
    #print("sheet id:",sheet['id'])
    #print("range:",sheet['range'])
    result = sheet['service'].spreadsheets().values().get(
        spreadsheetId=sheet['id'], range=sheet['range']).execute()
    values = result.get('values', [])

    if not values:
#        print('No data found!') # do this if no data is found
        pass
    else:
#        print('spreadsheet loaded...') # do this if we find data
        shifts = [] # create empty arrays for info
        for row in values: # for each row in each cell
            col = 1 # data from column B
            cell = row[col] #grab cell data
            cell = cell.split("\n") # split the data for every return character

            for shiftLine in cell: # for each return, do this
                shiftLine = shiftLine.split(" ") # turn the line into an array based on spaces
                if ((shiftLine[0] != "") and (shiftLine[0] != "Roster") and (shiftLine[3] == "@")): # run when conditions met
#                        print("         shiftLine[0] (day):",shiftLine[0])
#                        print("        shiftLine[1] (date):",shiftLine[1])
#                        print("        shiftLine[2] (time):",shiftLine[2])
#                        print("         shiftLine[3] ('@'):",shiftLine[3])
#                        print("shiftLine[4] (location 1/2):",shiftLine[4])
#                        print("shiftLine[5] (location 2/2):",shiftLine[5])
                    date = shiftLine[1] # copy the date from text
                    year = now.year # set the year as the current year
                    startTime = shiftLine[2].split("-")[0]
                    endTime = shiftLine[2].split("-")[1]
                    #print("startTime:",startTime);print("endTime:",endTime)
                    shiftStarts = [str(date),str(year),str(startTime)]
                    shiftEnds = [str(date),str(year),str(endTime)]
#                        print("starts at:",shiftStarts)
#                        print("  ends at:",shiftEnds)

                    #join 'em
                    shiftStarts = " ".join(shiftStarts); shiftEnds = " ".join(shiftEnds)
                    #strp 'em
                    shiftStarts = datetime.datetime.strptime(shiftStarts,"%d/%m %Y %H:%M"); shiftEnds = datetime.datetime.strptime(shiftEnds,"%d/%m %Y %H:%M")
                    #format 'em
                    shiftStarts = shiftStarts.isoformat('T');shiftEnds = shiftEnds.isoformat('T')
                    #print 'em
#                    print("formatted start:",shiftStarts); print("  formatted end:",shiftEnds)
                    #add 'em (it)
                    shifts.append({'start': shiftStarts, 'end': shiftEnds})
#                print("---- END OF LINE ANALYSIS ----")
#            print("-------- END OF CELL ANALYSIS --------")
#        print("------------ END OF SHEET ANALYSIS ------------")
        
        events = []
        
        for shift in shifts:
#            print("generating event...")
            event = {
              'summary': '[ job ] Mawson\'s Bakery',
              'location': 'Mawson\'s Bakery Cafe, Euroa',
              'description': 'Shift automatically added by python script',
              'start': {
                'dateTime': shift['start']+"+11:00",
                'timeZone': 'Australia/Melbourne',
              },
              'end': {
                'dateTime': shift['end']+"+11:00",
                'timeZone': 'Australia/Melbourne',
              },
#              'recurrence': ['RRULE:FREQ=DAILY;COUNT=2'],
              'reminders': {
                'useDefault': False,
                'overrides': [
                  {'method': 'popup', 'minutes': 10},
                  {'method': 'popup', 'minutes': 30},
                  {'method': 'popup', 'minutes': 60},
                ],
              },
            }
#            print("appending event...")
            events.append(event) # add this event
#        print(events)
#            for event in events:
#                for data in event: print("[%s]: %s" % (data,event[data])) #print info for each event
#        print("finished appending events!...")
#        print("returning event list!...")
        sheet['shifts'] = events
        #return(events)

#        [YEAR]-[MONTH]-[DAY]T[HOUR]:[MIN]:[SEC].[SECDECIMAL]Z
#        [YEAR]-[MONTH]-[DAY]T[HOUR]:[MIN]:[SEC].[SECDECIMAL]-[TIMEZONE_HOUR]:[TIMEZONE_MIN]    # take away timezone
#        [YEAR]-[MONTH]-[DAY]T[HOUR]:[MIN]:[SEC].[SECDECIMAL]+[TIMEZONE_HOUR]:[TIMEZONE_MIN]    # add in timezone
#1985-04-12T23:20:50.52Z
#This represents 20 minutes and 50.52 seconds after the 23rd hour of April 12th, 1985 in UTC.
def printShifts(my_shifts):
    output = []
    for shift in my_shifts:
        output.append("[doing:] %s [at:] %s [from:] %s [until:] %s" % (shift['summary'],shift['location'],shift['start']['dateTime'],shift['end']['dateTime']))
    return(output)

def get_service(api_dict):
    if (api_dict['API'] == 'Google_Sheets'):
        http = api_dict['credentials'].authorize(httplib2.Http())
        api_dict['service'] = discovery.build('sheets', 'v4', credentials=api_dict['credentials'])
    elif (api_dict['API'] == 'Google_Calendar'):
        http = api_dict['credentials'].authorize(httplib2.Http())
        api_dict['service'] = discovery.build('calendar', 'v3', http=http)
    else:
        raise Exception("api not recognized!")

def get_calendar_id(calendar):
    page_token = None
    calendar_list = calendar['service'].calendarList().list(pageToken=page_token).execute()
#    print("finding calendarId based on summary (in list of all calendars)...")
    for calendar_list_entry in calendar_list['items']:
        if (calendar_list_entry['summary'] == calendar['summary_to_find']):
            return calendar_list_entry['id'] # set the id variable

def printCalendarEvents(service_object,calendar_id):
    my_events = service_object.events().list(calendarId=calendar_id).execute()
    for my_event in my_events['items']:
        #for key in my_event: print(key) # print available keys
        return([my_event['summary'],my_event['start']['dateTime'],my_event['end']['dateTime']])
def check_in_calendar(calendar,event_to_check,**kwargs):
    if 'timeMin' in kwargs: timeMin = kwargs['timeMin']
    if 'debug' in kwargs: debug_active = kwargs['debug']
    page_token = None
    cal_events = calendar['service'].events().list(calendarId=calendar['id'], pageToken=page_token, timeMin=timeMin).execute()
    dups = 0 # set duplicates found to 0
    for cal_event in cal_events['items']:
        if debug_active: print("        [event_to_check:]",str(event_to_check['start']['dateTime']))
        if debug_active: print("        [     cal_event:]",str(cal_event['start']['dateTime']))
        name_match = cal_event['summary'] == event_to_check['summary']
        start_match = str(cal_event['start']['dateTime']) == str(event_to_check['start']['dateTime'])
        end_match = str(cal_event['end']['dateTime']) == str(event_to_check['end']['dateTime'])
        if (name_match and start_match and end_match):
            dups = dups + 1 # add 1 to duplicates found
            if debug_active: print("matching: [%s] == [%s]" % (cal_event['start']['dateTime'],event_to_check['start']['dateTime']))
        else:
            if debug_active: print("NO MATCH!: [%s] != [%s]" % (cal_event['start']['dateTime'],event_to_check['start']['dateTime']))
            pass
    if (dups > 0): # run if any duplicates found
        return(True)
    else: # run if no duplicates found
        return(False)

def addToCalendar(shift,service,calendar_id):
        created_event = service.events().insert(calendarId=calendar_id,body=shift).execute()
        return created_event
#        print(created_event['id'])

#my_shifts = getShifts('19De960eh1EJC5GPAPMvSvKTHfJ30MYAUCJdGahVhMWM','A2:B')
#printShifts(my_shifts)

