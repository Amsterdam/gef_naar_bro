# dit script zet oude gef formaten om in gef 1.1.3
# er wordt informatie waar nodig aangevuld of aangepast
# deze bestanden kunnen vervolgens met het programma GEF-CPT2BRO-XML (van Fugro en Wiertsema & Partners, verkrijgbaar bij BRO) omgezet worden in IMBRO/A 
# de xml kunnen worden geleverd aan de BRO
# ook is er een optie om XMl te valideren via de API van de BRO. Hiervoor zijn een inlognaam en wachtwoord benodigd
# meer over de validatie op: https://basisregistratieondergrond.nl/inhoud-bro/aanleveren-gebruiken/tools-tips/validatieservice/

# er is een apart bestand met de naam organisatieSpecifiek.py nodig
# hierin staan wachtwoorden en kvk-nummer van de organisatie
# ook een link naar de bestandslocatie van de geopkg met sondeerlocaties die al aanwezig zijn in de bro
# alles op te geven als string, met de onderstaande namen
#username = ''
#password = ''
#kvk = ''
#broGpkg = ''

__author__ = "Thomas van der Linden"
__credits__ = ""
__license__ = "EUPL-1.2"
__version__ = ""
__maintainer__ = "Thomas van der Linden"
__email__ = "t.van.der.linden@amsterdam.nl"
__status__ = "Dev"

import tkinter as tk
from tkinter import filedialog
import os
import sys
import math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

import requests
from requests.structures import CaseInsensitiveDict
from requests.auth import HTTPBasicAuth
import json


import organisatieSpecifiek # TODO: from organisatieSpecifiek import ...

sys.path.insert(0, '../gefxml_viewer')
from gefxml_reader import Cpt

main_win = tk.Tk()

logo1 = tk.PhotoImage(file='./img/LogoAmsterdam.png')
tk.Label(main_win, image=logo1).place(x=15, y=95)

logo2 = tk.PhotoImage(file='./img/LogoWapen_van_amsterdam.png')
tk.Label(main_win, image=logo2).place(x=15, y=5)

script_version = ''
script_name = 'Thomas van der Linden'
tk.Label(main_win, text='Zet oude GEF formaten om in gef1.1.3 t.b.v. omzetten naar BRO XML ', fg='black', font='Courier 16 bold').pack()
tk.Label(main_win, text='Lees GEF bestanden in map met Python =) of kies één of meerdere GEF-file(s)', fg='black', font='Courier 12').pack()
tk.Label(main_win, text='Kies een map om xml bestanden te valideren', fg='black', font='Courier 12').pack()
tk.Label(main_win, text = 'Script: ' + script_name, fg='grey', font='Courier 10').place(x=800, y=280)
tk.Label(main_win, text = 'Versie: ' + script_version, fg='grey', font='Courier 10').place(x=1095, y=280)

main_win.geometry("1200x300")
main_win.sourceFolder = ''
main_win.sourceFiles = []
main_win.validateFiles = ''

def chooseDir():
    main_win.sourceFolder = filedialog.askdirectory(parent=main_win, title='Please select a directory')

b_chooseDir = tk.Button(main_win, text="Select Folder", width=20, height= 3, command=chooseDir)
b_chooseDir.place(x=335, y=95)
b_chooseDir.width = 100
b_chooseDir.config(font=('Courier 14'))

def chooseFiles():
    main_win.sourceFiles = filedialog.askopenfilenames(parent=main_win, title='Please select files')

b_chooseFiles = tk.Button(main_win, text="Select File(s)", width=20, height=3, command=chooseFiles)
b_chooseFiles.place(x=635, y=95)
b_chooseFiles.width = 100
b_chooseFiles.config(font=('Courier 14'))

def chooseValidate():
    main_win.validateFiles = filedialog.askdirectory(parent=main_win, title='Please select directory to validate')

b_chooseValidate = tk.Button(main_win, text="Select Validate", width=20, height=3, command=chooseValidate)
b_chooseValidate.place(x=935, y=95)
b_chooseValidate.width = 100
b_chooseValidate.config(font=('Courier 14'))

def ContinueButton():
    main_win.destroy()

b_ContinueButton = tk.Button(text="Continue", width=20, height=3, command=ContinueButton)
b_ContinueButton.place(x=635, y=195)
b_ContinueButton.width = 100
b_ContinueButton.config(font=('Courier 14 bold'))

main_win.mainloop()

def validate(folder):
    # functie om bestanden te valideren via de API van BRO
    # volgens https://www.bronhouderportaal-bro.nl/doc/api.html
    files = [f'{folder}/{f}' for f in os.listdir(folder) if f.lower().endswith('xml')]
    # functie om te bepalen of een xml valide is via de API van BRO

    url = "https://www.bronhouderportaal-bro.nl/api/validatie"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/xml"
    headers["Authorization"] = "basic"

    auth=HTTPBasicAuth(organisatieSpecifiek.username, organisatieSpecifiek.password)

    validateDict = {}

    for path in files:
        print(path)
        with open(path) as data:
            # doe de request
            resp = requests.post(url, headers=headers, data=data, auth=auth)
            broResp = json.loads(resp.content.decode("utf-8"))
            validateDict[path] = broResp
    
    validateDf = pd.DataFrame().from_dict(validateDict, orient='index')
    validateDf.to_csv(f'{folder}/validate.csv', sep=';')
    print(f'validatieresultaat weggeschreven in {folder}/validate.csv')


def aanleveren(folders):
    # functie om bestanden aan te leveren via de API van BRO
    # volgens https://www.bronhouderportaal-bro.nl/doc/api.html
    print('aanleveren loopt')
    
    # geef het projectid op. Dit is het projectnummer dat je vindt onder Projectgegevens in het bronhouderportaal
    projectId = organisatieSpecifiek.projectId
    
    headersAanmaken = CaseInsensitiveDict()
    headersAanmaken["Content-Type"] = "application/xml"
    headersAanmaken["Authorization"] = "basic"

    auth=HTTPBasicAuth(organisatieSpecifiek.username, organisatieSpecifiek.password)

    uploadId = upload_aanmaken(auth, headersAanmaken, projectId)

    for folder in folders: # het zou netter zijn per folder, maar dan is de levering ook per folder en dat is minder goed
        files = [f'{folder}/{f}' for f in os.listdir(folder) if f.lower().endswith('xml')]
        for path in files:
            bestanden_toevoegen_aan_upload(auth, headersAanmaken, path, projectId, uploadId)
    lever_upload(auth, projectId, uploadId)

def upload_aanmaken(auth, headers, projectId):
    # post een request om een upload aan te maken.
    urlAanmaken = f"https://www.bronhouderportaal-bro.nl/api/v2/{projectId}/uploads"

    resp = requests.post(urlAanmaken, headers=headers, auth=auth)
    # controleer of dat gelukt is
    if resp.status_code == 201:
        # er wordt een upload id aangemaakt die later weer nodig is
        print('upload succesvol gemaakt')
        return resp.headers["Location"].split('/')[-1]
    else:
        print(f'{resp.status_code}, er ging iets mis bij het aanmaken van het upload')

def bestanden_toevoegen_aan_upload(auth, headers, path, projectId, uploadId):
    # voeg bestanden toe aan de upload
        
    filename = path.split('/')[-1]

    urlUpload = f'https://www.bronhouderportaal-bro.nl/api/v2/{projectId}/uploads/{uploadId}/brondocumenten?filename={filename}'

    with open(path) as data:
        # post een request om een bestand toe te voegen
        resp = requests.post(urlUpload, headers=headers, data=data, auth=auth)

def lever_upload(auth, projectId, uploadId):
    # lever de upload
    urlLeveren = f'https://www.bronhouderportaal-bro.nl/api/v2/{projectId}/leveringen?labels=archief'

    headersLeveren = CaseInsensitiveDict()
    headersLeveren["Content-Type"] = "application/json"
    headersLeveren["Authorization"] = "basic"

    resp = requests.post(urlLeveren, headers=headersLeveren, data=json.dumps({"upload": int(uploadId)}), auth=auth)


def to_gef113(cpt, filePath):
    # schrijf een bestand weg met daarin de ingelezen gegevens volgens de GEF standaard 113
                
    # verplicht, informatie mag niet ontbreken:
        #GEFID=
        #PROCEDURECODE=
        #MEASUREMENTTEXT= 9, maaiveld of waterbodem (meer mogelijke teksten in GEF dan in XML)
        #MEASUREMENTTEXT= 101, KVK-nummer bronhouder
        #PROJECTID=
        #TESTID=
        #COLUMNINFO= [number], [text], [text], 1
        #COLUMNINFO= [number], [text], [text], 2
        #XYID=
        #ZID=

    # verplicht, informatie mag ontbreken:
        #COMPANYID=
        #FILEDATE=

    # bepaal of er een mapje output is, anders moet deze gemaakt
    if not os.path.isdir(f'./output/'):
        os.mkdir(f'./output/')

    # ontbrekende data aanvullen
    if cpt.date is None:
        date = '-,-,-' # TODO: uitzoeken wat correcte 'informatie ontbreekt' tekst is
    if len(cpt.procedurecode.keys()) == 0:
        cpt.procedurecode = {"type": "GEF-CPT-Report", "major": 1, "minor": 1, "build": 0}
    if len(cpt.reportcode.keys()) == 0:
        cpt.reportcode = {"type": "GEF-CPT-Report", "major": 1, "minor": 1, "build": 0}

    # kvk-nummer aanvullen
    checkKvk = False
    if checkKvk:
        if 'Multiconsult'.lower() in cpt.companyid.lower():
            kvk = '09073590'
        elif 'BAM Infraconsult BV'.lower() in cpt.companyid.lower():
            kvk = '09073590'
        elif 'Ruiter'.lower() in cpt.companyid.lower():
            kvk = '09073590'
        elif 'Lankelma Ingenieursbureau'.lower() in cpt.companyid.lower():
            kvk = '71979972'
        elif 'Lankelma'.lower() in cpt.companyid.lower():
            kvk = '54521610'
        elif 'Fugro'.lower() in cpt.companyid.lower():
            kvk = '27114147'
        elif 'Geonius'.lower() in cpt.companyid.lower():
            kvk = '14048726'
        elif 'Rotterdam'.lower() in cpt.companyid.lower():
            kvk = '24483298'
        elif 'Inpijn'.lower() in cpt.companyid.lower():
            kvk = '17076128'
        elif 'Dijk'.lower() in cpt.companyid.lower():
            kvk = '30128364'
        elif 'Mos'.lower() in cpt.companyid.lower():
            kvk = '24257098'
        elif 'Wiertsema'.lower() in cpt.companyid.lower():
            kvk = '02095434'
        elif 'Tjaden'.lower() in cpt.companyid.lower():
            kvk = '54294959'
        elif 'Geosonda'.lower() in cpt.companyid.lower():
            kvk = '27184822'
        elif 'Geo-Supporting'.lower() in cpt.companyid.lower():
            kvk = '34252996'
        elif 'Aelmans'.lower() in cpt.companyid.lower():
            kvk = '14048216'
        elif 'BoutenGeotron'.lower() in cpt.companyid.lower():
            kvk = '10039086'
        elif 'Hoogveld'.lower() in cpt.companyid.lower():
            kvk = '08145500'
        elif 'Hutton'.lower() in cpt.companyid.lower():
            kvk = '82359598'
        elif 'IJB'.lower() in cpt.companyid.lower():
            kvk = '01059718'
        elif 'Koops'.lower() in cpt.companyid.lower():
            kvk = '61574031'
        elif 'Ortageo'.lower() in cpt.companyid.lower():
            kvk = '66382971'
        elif 'Poelsema'.lower() in cpt.companyid.lower():
            kvk = '05086972'
        elif 'Sialtech'.lower() in cpt.companyid.lower():
            kvk = '30114487'
        elif 'Deltares'.lower() in cpt.companyid.lower():
            kvk = '41146461'
        elif 'Waternet'.lower() in cpt.companyid.lower():
            kvk = '41216593'
        elif 'Tjaden Adviesbureau'.lower() in cpt.companyid.lower():
            kvk = '54294959'
        elif 'Tjaden'.lower() in cpt.companyid.lower():
            kvk = '34057287'
        elif 'Straaten'.lower() in cpt.companyid.lower():
            kvk = '20015504'
        elif 'VWB'.lower() in cpt.companyid.lower():
            kvk = '62092758'
        else:
            kvk = organisatieSpecifiek.kvk


    # maak de data absoluut, negatieve waarden zijn niet toegestaan
    for param in ['frictionRatio', 'localFriction']:
        if param in cpt.data.columns:
            cpt.data[cpt.data[param] < 0][param] = 0
    cpt.data = cpt.data.abs()
    
    with open(filePath, 'w') as f:
        f.write(
            f'#GEFID= {cpt.gefid["major"]},{cpt.gefid["minor"]},{cpt.gefid["build"]}\n' +
            f'#REPORTCODE= {cpt.reportcode["type"]},{cpt.reportcode["major"]},{cpt.reportcode["minor"]},{cpt.reportcode["build"]}\n' + 
            f'#PROCEDURECODE= {cpt.procedurecode["type"]},{cpt.procedurecode["major"]},{cpt.procedurecode["minor"]},{cpt.procedurecode["build"]}\n' + 
#            f'#COMPANYID= {cpt.companyid}, {kvk}, 31\n' 
            f'#COMPANYID= \n' 
        )

        f.write(
            f'#PROJECTID= {cpt.projectid}\n' +
#                f'#PROJECTNAME= {cpt.projectname}\n' +            
            f'#TESTID= {cpt.testid}\n' +
            f'#XYID= 31000, {cpt.easting}, {cpt.northing}\n' +
            f'#ZID= 31000, {cpt.groundlevel}\n'
        )

        # filedate is verplicht
        if len(cpt.filedate.keys()) > 0:
            f.write(f'#FILEDATE= {cpt.filedate["year"]}, {cpt.filedate["month"]}, {cpt.filedate["day"]}\n')
        # als er geen filedate is, maar wel startdate is dat de tweede keus
        elif len(cpt.startdate.keys()) > 0:
            f.write(f'#FILEDATE= {cpt.startdate["year"]}, {cpt.startdate["month"]}, {cpt.startdate["day"]}\n')
        # als er ook geen startdate is, dan een dummy waarde gebruiken
        else:
            f.write(f'#FILEDATE= {date}\n')

        # zonder startdate is bestand niet valide
        if len(cpt.startdate.keys()) > 0:
            f.write(f'#STARTDATE= {cpt.startdate["year"]}, {cpt.startdate["month"]}, {cpt.startdate["day"]}\n')
        # als er geen filedate is, maar wel startdate is dat de tweede keus
        elif len(cpt.filedate.keys()) > 0:
            f.write(f'#STARTDATE= {cpt.filedate["year"]}, {cpt.filedate["month"]}, {cpt.filedate["day"]}\n')
        # als er ook geen startdate is, dan een dummy waarde gebruiken
        else:
            f.write(f'#STARTDATE= {date}\n')

        # voeg de measurementtexts toe
        for number, text in cpt.measurementtexts.items():
            if number != '9': # 9 maaiveld of waterbodem wordt apart behandeld
                f.write(f"#MEASUREMENTTEXT= {number}, {text}\n")

        # lokaal verticaal referentiepunt is verplicht
        # als het ontbreekt, aanvullen met standaard maaiveld
        mt9Options = ['maaiveld', 'mv', 'ground level', 'groundlevel', 'waterbodem', 'wb', 'flow bed']
        if '9' in cpt.measurementtexts.keys():
            # er werden in de praktijk verschillende woorden gebruikt. Moet 'maaiveld' of 'waterbodem' zijn.
            if cpt.measurementtexts['9'].lower() in mt9Options:
                f.write(f"#MEASUREMENTTEXT= 9, {cpt.measurementtexts['9']}\n")
            elif 'w' in cpt.measurementtexts['9'].lower():
                f.write("#MEASUREMENTTEXT= 9, waterbodem\n")
            elif 'v' in cpt.measurementtexts['9'].lower() or 'g' in cpt.measurementtexts['9'].lower():
                f.write("#MEASUREMENTTEXT= 9, maaiveld\n")
        else:
            f.write("#MEASUREMENTTEXT= 9, maaiveld\n")

        # measurementtext 101 met KvK-nummer van bronhouder is verplicht
        if not '101' in cpt.measurementtexts.keys():
            f.write(f"#MEASUREMENTTEXT= 101, Gemeente Amsterdam, {organisatieSpecifiek.kvk}, -\n") 
        
        # opmerking dat deze uit ons archief komt TODO: is eigenlijk organisatiespecifiek
        if not '24' in cpt.measurementtexts.keys():
            f.write("#MEASUREMENTTEXT= 24, cpt uit archief ingenieursbureau Amsterdam, -\n")

        # een te diepe start van de sondering zonder opgave van voorboring resulteert in een foutmelding
        # er zijn twee opties:
        # 1. measurement variable 13 - voorboring
        # 2. opvullen vanaf sondeerlengte 0 met dummy waarden
        voorboringMeasurmentVar13 = False
        voorboringDummyVulling = True
        # deze methode werkt voor 00 (2) en voor W106 (4)
        if voorboringMeasurmentVar13:
            # als er geen measurementvar 13 aanwezig is in het originele bestand
            if cpt.data['penetrationLength'].min() != 0. and not '13' in cpt.measurementvars.keys():    
                f.write(f"#MEASUREMENTVAR= 13, {cpt.data['penetrationLength'].min()}, m, -\n")
            # als er wel measurementvar 13 aanwezig is in het originele bestand    
            elif cpt.data['penetrationLength'].min() != 0. and '13' in cpt.measurementvars.keys():
                f.write(f"#MEASUREMENTVAR= 13, {cpt.measurementvars['13']}\n") 

        # deze methode werkt 1016-0174-009_DKM10
        if voorboringDummyVulling:
            if cpt.data['penetrationLength'].min() != 0.:
                voorboring = pd.DataFrame(columns=cpt.data.columns)
                if 'penetrationLength' in cpt.data.columns:
                    voorboring['penetrationLength'] = np.arange(0, cpt.data['penetrationLength'].min(), 0.02)
                    for column in cpt.data.columns:
                        if column != 'penetrationLength':
                            voorboring[column] = -9999
                cpt.data = pd.concat([cpt.data, voorboring])
                cpt.data.sort_values(by='penetrationLength', inplace=True)

        # TODO: uitzoeken wat hiermee te doen in relatie tot bovenstaande omgang met voorboringen
        # soms is er voor een regel met dummy waarden toegevoegd, in dat geval
        if cpt.data[cpt.data['penetrationLength'] == 0.][cpt.data.columns[1:]].isnull().values.all():
            # het kan ook zijn dat de waarde 0 niet voorkomt, dan is de vorige True
            # daarom check of die lengte voorkomt en of maaiveld / waterbodem is opgegeven
            if len(cpt.data[cpt.data['penetrationLength'] == 0.] > 0) and '9' in cpt.measurementtexts.keys():
                # als de referentie iets van water is
                if 'w' in cpt.measurementtexts['9'].lower():
                    # verwijder de eerste regel
                    cpt.data.drop(labels=cpt.data[cpt.data['penetrationLength'] == 0.].index[0], axis='index')
                    # voeg waterdiepte toe
                    f.write(f"#MEASUREMENTVAR= 15, {cpt.data['penetrationLength'].min()},m,-\n")

        # measurementvars kunnen tot fouten leiden en zijn niet verplicht, daarom zijn ze optioneel gemaakt
        includeMeasVar = False
        if includeMeasVar:
            for number, text in cpt.measurementvars.items():
                f.write(f"#MEASUREMENTVAR= {number}, {text}\n")

        for number, text in cpt.columninfo.items():
            f.write(f"#COLUMNINFO= {number+1},{cpt.columninfoUnit[number]},{text},{cpt.columninfoQuantNr[number]}\n")

        # column void values zijn vervangen door -9999
        for colnr, voidvalue in enumerate(cpt.data.columns): #cpt.columnvoid_values.items():
            f.write(f'#COLUMNVOID= {colnr+1}, -9999.0\n')

        # schrijf de data weg zonder header en index
        # om later weer in te lezen als platte tekst
        # direct omzetten met to_string kan een foutmelding geven bij omzetten naar XML vanwege initiële spatie
        cpt.data.to_csv('./datatemp.txt', index=False, header=False, sep=' ', na_rep='-9999.0')
        with open('./datatemp.txt', 'r') as dataTemp:
            content = dataTemp.read()


        f.write(
                f'#COLUMN= {len(cpt.columninfo)}\n' +
                f'#LASTSCAN= {len(cpt.data)}\n' +
                '#EOH=\n' +
                content
        )

def check_al_in_BRO(easting, northing, buffer):
    # bepaal of op dit coördinaat al een sondering beschikbaar is
    if Point(easting, northing).within(buffer):
        return True
    else:
        return False

def haal_xy_uit_GIS():
    pass

def check_benodigdheden(cpt):
    # controle of alle benodigde elementen aanwezig zijn en een correcte waarde hebben
    checks = []
    if cpt.easting is not None and cpt.northing is not None:
        checks.append(float(cpt.easting) != 0.) 
        checks.append(float(cpt.northing) != 0.)
    else:
        checks.append(False)
    checks.append(cpt.groundlevel is not None)
    checks.append(cpt.testid is not None) 
    checks.append(cpt.projectid is not None) 
    return checks

def convert_batch(files):
    # wat dingen om bij te houden wat er wel en niet is omgezet
    columns=["testid", "x", "y", "lengte"]
    uniekCorrect = pd.DataFrame(columns=columns)
    nietUniekCorrect = pd.DataFrame(columns=columns)
    i, j = 0, 0

    broCptVolledigeSet = gpd.read_file(organisatieSpecifiek.broGpkg)
    broCptVolledigeSet = broCptVolledigeSet.to_crs('epsg:28992')
    buffer = broCptVolledigeSet['geometry'].buffer(1).unary_union

    # maak een bestand met errors
    with open('./output/errors.txt', 'w') as errors:
        for f in files:
            print(f)
            if f.lower().endswith('gef'):
                try:
                    cpt = Cpt()
                    # laad de cpt in
    #                try: 
                    cpt.load_gef(f)

                    # doe checks of xyz-coördinaten, testid en projectid aanwezig zijn en niet 0
                    checkContents = check_benodigdheden(cpt)
                    # check of het bestand een duplicaat is

                    # TODO: coördinaten inlezen uit GIS bestand als ze ontbreken
                    # Dit kan niet voor alles. Kan ook nog later
                    # check of op deze locatie al een sondering in de BRO zit.

                    if all(checkContents) and not (uniekCorrect == [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]).all(1).any():
                        checkInBro = check_al_in_BRO(cpt.easting, cpt.northing, buffer)
                        if not checkInBro:

                            # bestandsnaam t.b.v. wegschrijven:
                            fileName113 = f.split('/')[-1]

                            # voeg data over de sondering toe aan de tabel
                            uniekCorrect.loc[i] = [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]
                            
                            # de omzetter naar xml kan maximaal 100 bestanden per keer aan
                            # daarom per 100 bestanden een nieuwe map aanmaken
                            if not os.path.isdir(f'./output/{math.floor(i/100)}'):
                                os.mkdir(f'./output/{math.floor(i/100)}')
                            # schrijf het bestand weg
                            filePath = f'./output/{math.floor(i/100)}/{fileName113}'

                            to_gef113(cpt, filePath)
                            i += 1
                    else:
                        nietUniekCorrect.loc[j] = [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]
                        j += 1
                except Exception as e:
                    errors.write(f'{f}, {e}\n')

    uniekCorrect.to_csv('./output/uniekCorrect.csv', sep=';', decimal=',')
    nietUniekCorrect.to_csv('./output/nietUniekCorrect.csv', sep=';', decimal=',')

if main_win.sourceFolder != '':
    filelist = os.listdir(main_win.sourceFolder)
    files = [f'{main_win.sourceFolder}/{f}' for f in filelist]
    convert_batch(files)

elif len(main_win.sourceFiles) > 0: 
    files = list(main_win.sourceFiles)
    convert_batch(files)


elif main_win.validateFiles != '':
    validate(main_win.validateFiles)



vanMap = 37
totMap = 43

doOpnieuw = False
if doOpnieuw:
    # onderstaande is om een correctie uit te kunnen voeren
    # in veel bestanden ontbreekt een voorboordiepte vanwege een onhandige check
    # die bestanden kunnen opnieuw omgezet worden in gef113
    for i in range(vanMap, totMap+1):
        validatieResult = pd.read_csv(f'C:/Users/linden082/Documents/{i}/xml/validate.csv', sep=';')
        nietValide = validatieResult[validatieResult['status'] == 'NIET_VALIDE']
        nietValide['filename'] = nietValide['Unnamed: 0'].str.split('/').str.get(-1)
        for filename in nietValide['filename']:
            cpt = Cpt()
            try:
                f = f"C:/Users/linden082/data\cpt/GEF/niet_omegam/{filename.replace('xml', 'gef')}"
                cpt.load_gef(f)
            except:
                f = f"C:/Users/linden082/data\cpt/GEF/niet_omegam/{filename.replace('xml', 'GEF')}"
                cpt.load_gef(f)

            filePath = f"C:/Users/linden082/Documents/{i}/{filename.replace('xml', 'gef')}"
            
            to_gef113(cpt, filePath)

doValidatie = False
if doValidatie:
    for i in range(vanMap, totMap+1):
        folder = f'C:/Users/linden082/Documents/{i}/xml'
        validate(folder)

moveInvalidXML = False
if moveInvalidXML:
    for i in range(vanMap, totMap+1):
        validatieResult = pd.read_csv(f'C:/Users/linden082/Documents/{i}/xml/validate.csv', sep=';')
        nietValide = validatieResult[validatieResult['status'] == 'NIET_VALIDE']
        nietValide['filename'] = nietValide['Unnamed: 0'].str.split('/').str.get(-1)

        if not os.path.isdir(f'C:/Users/linden082/Documents/iets mis/{i}/'):
            os.mkdir(f'C:/Users/linden082/Documents/iets mis/{i}/')

        for filename in nietValide['filename']:
            f = f'C:/Users/linden082/Documents/{i}/xml/{filename}'
            dest = f'C:/Users/linden082/Documents/iets mis/{i}/{filename}'
            os.rename(f, dest)


filterAmsterdam = False
if filterAmsterdam:
    # doorloop de bestanden nog eens of ze in Amsterdam zijn, anders grote kans dat de locaties fout zijn
    # TODO: moet ook in de batch verwerking
    # TODO: let dan op,of je all of any gebruikt!
    for i in range(vanMap, totMap+1):
        if not os.path.isdir(f'C:/Users/linden082/Documents/iets mis/buitenAdam/{i}/'):
            os.mkdir(f'C:/Users/linden082/Documents/iets mis/buitenAdam/{i}/')
        folder = f'C:/Users/linden082/Documents/{i}/xml'
        files = [f'{folder}/{f}' for f in os.listdir(folder) if f.lower().endswith('xml')]
        for f in files:
            cpt = Cpt()
            cpt.load_xml(f)
            westVanA = cpt.easting < organisatieSpecifiek.west
            oostVanA = cpt.easting > organisatieSpecifiek.oost
            noordVanA = cpt.northing > organisatieSpecifiek.noord
            zuidVanA = cpt.northing < organisatieSpecifiek.zuid
            # als een van deze True is dan moet het bestand verplaatst worden
            if any([oostVanA, westVanA, noordVanA, zuidVanA]):
                filename = f.split('/')[-1]

                dest = f'C:/Users/linden082/Documents/iets mis/buitenAdam/{i}/{filename}'
                os.rename(f, dest)


doLeveren = True
if doLeveren:
    folders = [f'C:/Users/linden082/Documents/{i}/xml' for i in range(vanMap, totMap+1)]
    aanleveren(folders)

losGefOmzetten = False
if losGefOmzetten:
    gef = '1016-0174-009_DKM10' #'00 (2)' # W106 (4)
    f = f'./gef113/in_test/{gef}.gef'
    filePath = f'./gef113/out_test/{gef}.gef'
    cpt = Cpt()
    cpt.load_gef(f)
    to_gef113(cpt, filePath)

losXmlValideren = False
if losXmlValideren:
    validate('./gef113/out_test/xml')