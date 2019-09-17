from requests import Session
import urllib
from lxml import html
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

#UC3M url that links to the calendars webpage:
URL = "https://aplicaciones.uc3m.es/horarios-web/alumno/alumno.page"
#Aula Global Credentials:
if not os.path.isfile("AulaCredentials.txt"):
    print('Introduce tus credenciales de Aula Global: [NIA (100XXXXXX) y contraseña]')
    NIA = input('NIA/Numero de Estudiante/Student Number: ') # ## TODO: NUMERO DE ESTUDIANTE / USUARIO DE AULA GLOBAL
    PASS = input('Contraseña/Password: ')# #TODO
    with open("AulaCredentials.txt", mode = 'w') as f:
        f.write(NIA + "\n")
        f.write(PASS + "\n")
else:
    with open("AulaCredentials.txt") as f:
        lineList = [line.rstrip('\n') for line in open("AulaCredentials.txt")]
        NIA = lineList[0]
        PASS = lineList[1]

#Scraping the .ics file to get the calendars:
with Session() as s:

    print('Scraping ' + URL + ' to get .ics file')
    print("Attempting to log into Aula Global")
    ##To login to Aula global using the credentials above
    site = s.get("https://login.uc3m.es/index.php/CAS/login?service=https%3A%2F%2Faulaglobal.uc3m.es%2Flogin%2Findex.php&gateway=true")
    login_data = {"adAS_i18n_theme": "es",
                  "adAS_mode":"authn",
                  "adAS_username":NIA,
                  "adAS_password":PASS}
    s.post("https://login.uc3m.es/index.php/CAS/login?service=https%3A%2F%2Faulaglobal.uc3m.es%2Flogin%2Findex.php&gateway=true",login_data)
    print('Log in was succesful')
    ##To enter the horarios webpage and access all the references with links
    calendar_page = s.get(URL)
    webpage = html.fromstring(calendar_page.content)
    hrefList = webpage.xpath('//a/@href')
    ##To download the ics files and put them into the "horarios" folder:
    ## HORARIO CORRESPONDIENTE AL PRIMER CUATRIMESTRE:
    calendarLink_1 = "https://aplicaciones.uc3m.es" + hrefList[2]
    cal_q1 = s.get(calendarLink_1)
    calFile_1 = str(os.path.dirname(os.path.realpath(__file__))) + "/horarios/horario_Q1.ics"
    horarioCuatri_1 = open(calFile_1, 'wb').write(cal_q1.content)
    print('Horario 1er Cuat. obtained')

    ## HORARIO CORRESPONDIENTE AL SEGUNDO CUATRIMESTRE:
    calendarLink_2 = "https://aplicaciones.uc3m.es" + hrefList[4]
    cal_q2 = s.get(calendarLink_2)
    calFile_2 = str(os.path.dirname(os.path.realpath(__file__))) + "/horarios/horario_Q2.ics"
    horarioCuatri_2 = open(calFile_2, 'wb').write(cal_q2.content)
    print('Horario 2do Cuat. obtained')

import ParsingAndImport_cal
