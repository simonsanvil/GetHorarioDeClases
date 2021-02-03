from lxml import html
import subprocess
import os
from datetime import datetime
import sys
from util.LoginSession import MyLoginSession
from tkinter import *

os.chdir(os.path.dirname(os.path.realpath(__file__)))

import argparse
def extract_arguments():

    parser = argparse.ArgumentParser(description='Process values for implementation of system.',argument_default = 3)
    parser.add_argument('-without', metavar='--not_include', type=str, default = None,
                       help='Names of classes that wont be included in the calendar, separated by commas')
    parser.add_argument('-Q', metavar='--cuatrimestre', type=int, default = None,
                       help='Specific semester to retrieve. Values are 1/2 or NULL to retrieve the most recent one.')
    parser.add_argument('-calname', metavar='--nombre', type=str, default = None,
                       help='Name of the calendar to create. Default is "Horario de Clases 20[XX]-20[XX+1]"')
    args = parser.parse_args()

    attributes = {
        "calname" : args.calname,
        "to_ignore" : [args.without] if args.without is None else args.without.replace(" ","").lower().split(","),
        "cuatrimestre" : args.Q
    }


    return attributes

def getHorarios(cuatrimestre):
    #UC3M url that links to the calendars webpage:
    print('To obtain class calendars UC3M Aula global credentials are required')
    URL = "https://aplicaciones.uc3m.es/horarios-web/alumno/alumno.page"
    #Aula Global Credentials:
    if not os.path.isfile("util/AulaCredentials.txt"): #If we we dont have the credentials in a file already
        credentials = getCredentials() # TODO: NUMERO DE ESTUDIANTE y contrasena de aula global
        NIA = credentials[0]
        PASS = credentials[1]
    else: #Reading credentials from file in directory if it exists
        with open("util/AulaCredentials.txt") as f:
            lineList = [line.rstrip('\n') for line in f]
            NIA = lineList[0]
            PASS = lineList[1]

    login_site = "https://login.uc3m.es/index.php/CAS/login?service=https%3A%2F%2Faulaglobal.uc3m.es%2Flogin%2Findex.php&gateway=true"
    login_data = {"adAS_i18n_theme": "es",
                  "adAS_mode":"authn",
                  "adAS_username":NIA,
                  "adAS_password":PASS}
    mySession = MyLoginSession(login_site,login_data, maxSessionTimeSeconds = 0*60) #30 minutes of timeout session

    print("Attempting to log into Aula Global")
    mySession.login() ##To login to Aula global using the credentials above

    #Scraping the .ics file to get the calendars:
    with mySession as s:
        ##To enter the horarios webpage and access all the references with links
        print('Scraping ' + URL + ' to get .ics file')
        try:
            calendar_page = s.retrieveContent(URL)
        except:
            print('There was an issue trying to request the website. The site might be temporarilly inactive or the server doesnt respond')
            return False

        webpage = html.fromstring(calendar_page.content)
        hrefList = webpage.xpath('//a/@href')
        ##To download the ics files and put them into the "horarios" folder:
        try:
            ics_refs = [href for href in hrefList if 'ics' in href]

            if  len(ics_refs) == 0:
                print('No horario found in the website')
                return False

            which_cal = 1 if datetime.today().month > 6 else 2 #En cual cuatrimestre estamos?
            which_ref = ics_refs[which_cal - 1] if len(ics_refs) > 1 else ics_refs[0]
            #for href in ics_refs:
            name = 'horario_Q1.ics' if (which_cal == 1) else 'horario_Q2.ics'
            calendarLink = "https://aplicaciones.uc3m.es" + which_ref
            print("Scraping",calendarLink,"to obtain calendar")
            cal = s.retrieveContent(calendarLink)
            calFile = str(os.path.dirname(os.path.realpath(__file__))) + "/Calendars/" + name
            horarioCuatri = open(calFile, 'wb').write(cal.content)
            print('Horario of this semester obtained')
        except Exception as e:
            print(e)
            print("Failed to obtain the calendars from Aula Global. Try again and make sure your aula global credentials are correct.")
            return False

        return True

def getCredentials():

    root = Tk()
    root.iconbitmap('util/Logo_UC3M.ico')
    root.title('Login')

    L1 = Label(root, text = 'Log with your Aula Global account: ')
    L1.grid(row = 0, column = 0)

    USER_label = Label(root, text = "NIA/student ID:")
    USER_label.grid(row = 1, column = 0)
    USER_entry = Entry(root, bd = 5)
    USER_entry.grid(row = 1, column = 1)

    PASS_label = Label(root, text= 'Password/Contraseña:')
    PASS_label.grid(row = 2,column = 0)
    PASS_entry = Entry(root, bd = 5, show = '*')
    PASS_entry.grid(row = 0, column = 1)
    PASS_entry.grid(row = 2, column = 1)

    credentialsList = []
    def callback():
        username = USER_entry.get()
        PASS = PASS_entry.get()
        credentialsList.append(username)
        credentialsList.append(PASS)
        root.destroy()

    SUBMIT_button = Button(root, text="Submit", width=10, command=callback) # button named submit
    SUBMIT_button.grid(row=3, column=1) # position for button
    root.mainloop()
    return credentialsList

def installRequirementsWithPip():
        subprocess.call([sys.executable, "-m", "pip", "install","-r","requirements.txt"])

if __name__ == "__main__":
    print(os.getcwd())
    installRequirementsWithPip()
    args = extract_arguments()
    if getHorarios(args['cuatrimestre']):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        import ParsingAndImport
        if ParsingAndImport.parseICS(args['to_ignore']):
            ParsingAndImport.importToGoogleCalendar(args['calname'])
