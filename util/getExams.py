from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import PyPDF2
from requests import Session
import urllib
from lxml import html
import subprocess
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def getExams():
    URL = "https://aplicaciones.uc3m.es/horarios-web/alumno/verExamenes.page?exp=933961&anoAcad=2019"
    with open("AulaCredentials.txt") as f:
        lineList = [line.rstrip('\n') for line in open("AulaCredentials.txt")]
        NIA = lineList[0]
        PASS = lineList[1]
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
        print('Scraping ' + URL + ' to get pdf file')
        try:
            pdf_content = s.get(URL).content
            #print(pdf_content)
            exams_path = str(os.path.dirname(os.path.realpath(__file__))) + "/Calendars/exams.pdf"
            exams_file = open(exams_path, 'wb').write(pdf_content)
            print('pdf file obtained')
        except Exception as e:
            print(e)
            print('There was  an issue trying to request the website. The site might be temporarilly inactive or the server doesnt respond')
            return False
        #fileReader = PyPDF2.PdfFileReader(exams_path)
        #pages = [fileReader.getPage(i) for i in range(0,(fileReader.numPages))]
        # extracting text from page
        #print(pages[0].extractText())
        print(convert_pdf_to_txt(exams_path))

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

getExams()
