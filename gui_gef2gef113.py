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
#validatieUsername = ''
#validatiePassword = ''
#kvk = ''
#broGpkg = ''

import tkinter as tk
from tkinter import filedialog
import os
from gefxml_reader import Cpt
import math
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

import organisatieSpecifiek

main_win = tk.Tk()

logo1 = tk.PhotoImage(file='./img/LogoAmsterdam.png')
tk.Label(main_win, image=logo1).place(x=15, y=95)

logo2 = tk.PhotoImage(file='./img/LogoWapen_van_amsterdam.png')
tk.Label(main_win, image=logo2).place(x=15, y=5)

script_version = ''
script_name = 'Thomas van der Linden'
tk.Label(main_win, text='Zet oude GEF formaten om in nieuwe t.b.v. omzetten naar BRO XML ', fg='black', font='Courier 16 bold').pack()
tk.Label(main_win, text='Lees GEF bestanden in map met Python =) of kies één of meerdere GEF-file(s)', fg='black', font='Courier 12').pack()
tk.Label(main_win, text = 'Script: ' + script_name, fg='grey', font='Courier 10').place(x=800, y=280)
tk.Label(main_win, text = 'Versie: ' + script_version, fg='grey', font='Courier 10').place(x=1095, y=280)

main_win.geometry("1200x300")
main_win.sourceFolder = ''
main_win.sourceFiles = []
main_win.validateFiles = []

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
    main_win.validateFiles = filedialog.askopenfilenames(parent=main_win, title='Please select validate')

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

def validate(files):
    # functie om te bepalen of een xml valide is via de API van BRO
    import requests
    from requests.structures import CaseInsensitiveDict
    from requests.auth import HTTPBasicAuth

    url = "https://www.bronhouderportaal-bro.nl/api/validatie"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/xml"
    headers["Authorization"] = "basic"

    auth=HTTPBasicAuth(organisatieSpecifiek.validatieUsername, organisatieSpecifiek.validatiePassword)

    for path in files:
        print(path)
        with open(path) as f:
            data = f.read()
        # doe de request
        resp = requests.post(url, headers=headers, data=data, auth=auth)
        broResp = resp.content.decode("utf-8")
        print(path, broResp, '\n')

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
        date = '2017, , \n#COMMENT= datum informatie ontbreekt in oorspronkelijke bestand' # TODO: uitzoeken wat correcte 'informatie ontbreekt' tekst is
    if len(cpt.procedurecode.keys()) == 0:
        cpt.procedurecode = {"type": "GEF-CPT-Report", "major": 1, "minor": 1, "build": 0}
    if len(cpt.reportcode.keys()) == 0:
        cpt.reportcode = {"type": "GEF-CPT-Report", "major": 1, "minor": 1, "build": 0}

    # kvk-nummer aanvullen
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
    
    # schrijf de data weg zonder header en index
    # om later weer in te lezen als platte tekst
    # direct omzetten met to_string kan een foutmelding geven bij omzetten naar XML vanwege initiële spatie
    cpt.data.to_csv('./datatemp.txt', index=False, header=False, sep=' ', na_rep='-9999')
    with open('./datatemp.txt', 'r') as f:
        content = f.read()

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
        if cpt.data['penetrationLength'].min() != 0. and not '13' in cpt.measurementvars.keys():
            # voeg voorboordiepte toe
            f.write(f"#MEASUREMENTVAR= 13, {cpt.data['penetrationLength'].min()},m,-\n")

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
        for colnr, voidvalue in cpt.columnvoid_values.items():
            f.write(f'#COLUMNVOID= {colnr+1}, -9999\n')

        f.write(
                f'#COLUMN= {len(cpt.columninfo)}\n' +
                f'#LASTSCAN= {len(cpt.data)}\n' +
                '#EOH=\n' +
                content
        )

def check_al_in_BRO(easting, northing, broCptVolledigeSet):
    # bepaal of op dit coördinaat al een sondering beschikbaar is
    if Point(easting, northing) in broCptVolledigeSet.geometry:
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

    with open('./output/errors.txt', 'w') as errors:
        for f in files:
            print(f)
            # maak een bestand met errors
            if f.lower().endswith('gef'):
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
                    checkInBro = check_al_in_BRO(cpt.easting, cpt.northing, broCptVolledigeSet)
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
#                except Exception as e: 
#                    errors.write(f'{f}, {e}\n') 

    uniekCorrect.to_csv('./output/uniekCorrect.csv', sep=';', decimal=',')
    nietUniekCorrect.to_csv('./output/nietUniekCorrect.csv', sep=';', decimal=',')

if main_win.sourceFolder != '':
    filelist = os.listdir(main_win.sourceFolder)
    files = [f'{main_win.sourceFolder}/{f}' for f in filelist]
    convert_batch(files)

elif len(main_win.sourceFiles) > 0: 
    files = list(main_win.sourceFiles)
    convert_batch(files)


elif len(main_win.validateFiles) > 0:
    files = list(main_win.validateFiles)
    validate(files)


