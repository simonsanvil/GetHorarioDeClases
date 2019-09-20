from requests import Session
import urllib
from lxml import html
import subprocess
import os
import tkinter
from tkinter import *

os.chdir(os.path.dirname(os.path.realpath(__file__)))


def getHorarios():
    #UC3M url that links to the calendars webpage:
    print('To obtain class calendars, UC3M Aula global credentials are required')
    URL = "https://aplicaciones.uc3m.es/horarios-web/alumno/alumno.page"
    #Aula Global Credentials:
    if not os.path.isfile("AulaCredentials.txt"): #If we we dont have the credentials in a file already
        credentials = getCredentials() # TODO: NUMERO DE ESTUDIANTE y contrasena de aula global
        NIA = credentials[0]
        PASS = credentials[1]

    else: #Reading credentials from file in directory if it exists
        with open("AulaCredentials.txt") as f:
            lineList = [line.rstrip('\n') for line in open("AulaCredentials.txt")]
            NIA = lineList[0]
            PASS = lineList[1]

    #Scraping the .ics file to get the calendars:
    with Session() as s:
        print("Attempting to log into Aula Global")
        ##To login to Aula global using the credentials above
        site = s.get("https://login.uc3m.es/index.php/CAS/login?service=https%3A%2F%2Faulaglobal.uc3m.es%2Flogin%2Findex.php&gateway=true")
        login_data = {"adAS_i18n_theme": "es",
                      "adAS_mode":"authn",
                      "adAS_username":NIA,
                      "adAS_password":PASS}
        r = s.post("https://login.uc3m.es/index.php/CAS/login?service=https%3A%2F%2Faulaglobal.uc3m.es%2Flogin%2Findex.php&gateway=true",login_data)
        ##To enter the horarios webpage and access all the references with links
        print('Scraping ' + URL + ' to get .ics file')
        try:
            calendar_page = s.get(URL)
        except:
            print('There was  an issue trying to request the website. The site might be temporarilly inactive or the server doesnt respond')

        webpage = html.fromstring(calendar_page.content)
        hrefList = webpage.xpath('//a/@href')
        ##To download the ics files and put them into the "horarios" folder:
        try:
            ## HORARIO CORRESPONDIENTE AL PRIMER CUATRIMESTRE:
            calendarLink_1 = "https://aplicaciones.uc3m.es" + hrefList[2]
            cal_q1 = s.get(calendarLink_1)
            calFile_1 = str(os.path.dirname(os.path.realpath(__file__))) + "/horario_Q1.ics"
            horarioCuatri_1 = open(calFile_1, 'wb').write(cal_q1.content)

            ## HORARIO CORRESPONDIENTE AL SEGUNDO CUATRIMESTRE:
            calendarLink_2 = "https://aplicaciones.uc3m.es" + hrefList[4]
            cal_q2 = s.get(calendarLink_2)
            calFile_2 = str(os.path.dirname(os.path.realpath(__file__))) + "/horario_Q2.ics"
            horarioCuatri_2 = open(calFile_2, 'wb').write(cal_q2.content)

            print('Horario 1er Cuat. obtained')
            print('Horario 2do Cuat. obtained')
        except:
            print("Failed to obtain the calendars from Aula Global. Try again and make sure your aula global username and password are correct.")


def getCredentials():
    root = Tk()
    root.iconbitmap('Logo_UC3M.ico')
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
        subprocess.call([sys.executable, "-m", "pip", "install", "requirements.txt"])

#installRequirementsWithPip()
getHorarios()
#import ParsingAndImport_cal
