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

from organisatieSpecifiek import organisatieSpecifiek

from geotexxx.gefxml_reader import Cpt

def validate(folder):
    # functie om bestanden te valideren via de API van BRO
    # volgens https://www.bronhouderportaal-bro.nl/doc/api.html
    files = [f'{folder}/{f}' for f in os.listdir(folder) if f.lower().endswith('xml')]
    # functie om te bepalen of een xml valide is via de API van BRO

    url = "https://www.bronhouderportaal-bro.nl/api/validatie"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/xml"
    headers["Authorization"] = "basic"

    auth=HTTPBasicAuth(organisatieSpecifiek.get('username'), organisatieSpecifiek.get('password'))

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
    projectId = organisatieSpecifiek.get('projectId')
    
    headersAanmaken = CaseInsensitiveDict()
    headersAanmaken["Content-Type"] = "application/xml"
    headersAanmaken["Authorization"] = "basic"

    auth=HTTPBasicAuth(organisatieSpecifiek.get('username'), organisatieSpecifiek.get('password'))

    uploadId = upload_aanmaken(auth, headersAanmaken, projectId)

    for folder in folders: # het zou netter zijn per folder, maar dan is de levering ook per folder en dat is minder goed
        print(f'start map {folder}')
        files = [f'{folder}/{f}' for f in os.listdir(folder) if f.lower().endswith('xml')]
        for path in files:
            bestanden_toevoegen_aan_upload(auth, headersAanmaken, path, projectId, uploadId)
    lever_upload(auth, projectId, uploadId)

def upload_aanmaken(auth, headers, projectId):
    # stap 1 van het aanleveren via de BRO API
    # post een request om een upload aan te maken
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
    # stap 2 van het aanleveren via de BRO API
    # voeg bestanden toe aan de upload
        
    filename = path.split('/')[-1]

    urlUpload = f'https://www.bronhouderportaal-bro.nl/api/v2/{projectId}/uploads/{uploadId}/brondocumenten?filename={filename}'

    with open(path) as data:
        # post een request om een bestand toe te voegen
        resp = requests.post(urlUpload, headers=headers, data=data, auth=auth)

def lever_upload(auth, projectId, uploadId):
    # stap 3 (laatste stap) van aanleveren via BRO API
    # lever de upload
    print('start leveren')
    urlLeveren = f'https://www.bronhouderportaal-bro.nl/api/v2/{projectId}/leveringen?labels=archief'

    headersLeveren = CaseInsensitiveDict()
    headersLeveren["Content-Type"] = "application/json"
    headersLeveren["Authorization"] = "basic"

    resp = requests.post(urlLeveren, headers=headersLeveren, data=json.dumps({"upload": int(uploadId)}), auth=auth)

def check_datum(cpt):
    from datetime import datetime
    # er zijn bestanden met filedate voor startdate, dat is niet valide
    # als dat zo is, dan worden de datums gelijk gesteld
    if len(cpt.startdate.keys()) == 3 and len(cpt.filedate.keys()) == 3:
        filedate = datetime(cpt.filedate["year"], cpt.filedate["month"], cpt.filedate["day"])
        testdate = datetime(cpt.startdate["year"], cpt.startdate["month"], cpt.startdate["day"])
        if filedate < testdate:
            cpt.filedate["year"], cpt.filedate["month"], cpt.filedate["day"] = cpt.startdate["year"], cpt.startdate["month"], cpt.startdate["day"]

    # filedate is verplicht
    # als er geen filedate is, maar wel startdate is dat de tweede keus
    if len(cpt.filedate.keys()) == 0 and len(cpt.startdate.keys()) > 0:
        cpt.filedate["year"], cpt.filedate["month"], cpt.filedate["day"] = cpt.startdate["year"], cpt.startdate["month"], cpt.startdate["day"]
    # zonder startdate is bestand niet valide
    elif len(cpt.startdate.keys()) == 0 and len(cpt.filedate.keys()) > 0:
    # als er wel een filedate is, maar geen startdate is dat de tweede keus
        cpt.startdate["year"], cpt.startdate["month"], cpt.startdate["day"] = cpt.filedate["year"], cpt.filedate["month"], cpt.filedate["day"]
    # anders stel beide in op dummy waarden
    elif len(cpt.startdate.keys()) == 0 and len(cpt.filedate.keys()) == 0:
        cpt.filedate["year"], cpt.filedate["month"], cpt.filedate["day"] = '-', '-', '-'
        cpt.startdate["year"], cpt.startdate["month"], cpt.startdate["day"] = '-', '-', '-'

    # TODO: -, -, - lijkt niet te werken voor FILEDATE of STARTDATE
    # Check: https://github.com/BROprogramma/CPT_GEF_CONVERTER/blob/master/gef_impl/src/test/resources/test-artf52193cpt.gef hierin is STARTTIME met -, -, - gedaan
    # ook in https://github.com/BROprogramma/CPT_GEF_CONVERTER/blob/master/gef_impl/src/test/resources/test-artf52193dis.gef
    return cpt

def check_voorboring_meas_var(cpt):
    # als er geen measurementvar 13 aanwezig is in het originele bestand
    # deze methode werkt voor 00 (2) en voor W106 (4)
    if cpt.data['penetrationLength'].min() != 0. and not '13' in cpt.measurementvars.keys():    
        cpt.voorboring = cpt.data['penetrationLength'].min()
    # als er wel measurementvar 13 aanwezig is in het originele bestand    
    elif cpt.data['penetrationLength'].min() != 0. and '13' in cpt.measurementvars.keys():
        cpt.voorboring = cpt.measurementvars['13']
    else:
        cpt.voorboring = None

def check_voorboring_dummy(cpt):
    # deze methode werkt voor bijv 1016-0174-009_DKM10
    if cpt.data['penetrationLength'].min() != 0.:
        voorboring = pd.DataFrame(columns=cpt.data.columns)
        if 'penetrationLength' in cpt.data.columns:
            voorboring['penetrationLength'] = np.arange(0, cpt.data['penetrationLength'].min(), 0.02)
            for column in cpt.data.columns:
                if column != 'penetrationLength':
                    voorboring[column] = -9999
        cpt.data = pd.concat([cpt.data, voorboring])
        cpt.data.sort_values(by='penetrationLength', inplace=True)

def check_waterdiepte(cpt):
    # soms is er één regel met dummy waarden toegevoegd om een waterspiegel op te geven, dat werkt niet correct
    gebruikWaterdiepte = False
    if cpt.data[cpt.data['penetrationLength'] == 0.][cpt.data.columns[1:]].isnull().values.all():
        # het kan ook zijn dat de waarde 0 niet voorkomt, dan is de vorige True
        # daarom check of die lengte voorkomt en of maaiveld / waterbodem is opgegeven
        if len(cpt.data[cpt.data['penetrationLength'] == 0.] > 0) and '9' in cpt.measurementtexts.keys():
            # als de referentie iets van water is
            if 'w' in cpt.measurementtexts['9'].lower():
                # verwijder de eerste regel
                cpt.data.drop(labels=cpt.data[cpt.data['penetrationLength'] == 0.].index[0], axis='index')
                # voeg waterdiepte toe
                # TODO: zou eventueel ook via measurementvar 15 kunnen
                cpt.waterdepth = cpt.data['penetrationLength'].min()
                gebruikWaterdiepte = True
                return gebruikWaterdiepte, cpt.waterdepth
    return gebruikWaterdiepte, None

def check_verticaal_referentie(cpt):
    # lokaal verticaal referentiepunt is verplicht
    # als het ontbreekt, aanvullen met standaard maaiveld
    mt9Options = ['maaiveld', 'mv', 'ground level', 'groundlevel', 'waterbodem', 'wb', 'flow bed']
    if '9' in cpt.measurementtexts.keys():
        # er werden in de praktijk verschillende woorden gebruikt. Moet 'maaiveld' of 'waterbodem' zijn.
        if cpt.measurementtexts['9'].lower() in mt9Options:
            cpt.verticalReference = {cpt.measurementtexts['9']}
        elif 'w' in cpt.measurementtexts['9'].lower():
            cpt.verticalReference = 'waterbodem'
        elif 'v' in cpt.measurementtexts['9'].lower() or 'g' in cpt.measurementtexts['9'].lower():
            cpt.verticalReference = 'maaiveld'
        # TODO: dit afmaken
        # elif cpt.groundlevel >= 0: # TODO: variabele maken voor minimaal niveau maaiveld
        #   cpt.verticalReference = 'maaiveld'
        # elif cpt.groundlevel < 1: #  TODO: variabele maken voor maximaal niveau waterbodem, maar dan diepere polders?
        #   cpt.verticalReference = 'waterbodem'
        # else TODO: what else? check via open street map of dit coördinaat in het water is of zoiets?
    else:
        cpt.verticalReference = 'maaiveld'
    return cpt

def check_cpt_record_code(cpt):
    if len(cpt.procedurecode.keys()) == 0:
        cpt.procedurecode = {"type": "GEF-CPT-Report", "major": 1, "minor": 1, "build": 0}
    if len(cpt.reportcode.keys()) == 0:
        cpt.reportcode = {"type": "GEF-CPT-Report", "major": 1, "minor": 1, "build": 0}
    return cpt

def check_data_negative(cpt):
    # wrijving mag niet negatief zijn, zet negatieve waarden op dummy
    for param in ['frictionRatio', 'localFriction']:
        if param in cpt.data.columns:
            cpt.data[cpt.data[param] < 0][param] = np.nan
            # wrijvingsgetal mag niet groter zijn dan 100.1, dan ook op dummy zetten
            if param == 'frictionRatio':
                cpt.data[cpt.data[param] > 100.1][param] = np.nan
    # negatieve waarden zijn soms aanwezig, maar niet toegestaan
    # maak de rest van de data absoluut
    cpt.data = cpt.data.abs()
    return cpt

def kvk_aanvullen(cpt):
    # voor IMBRO is een kvk nummer nodig
    # deze functie kan op basis van een bedrijfsnaam een kvk nummer invullen
    # is niet nodig voor IMBRO/A
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
        kvk = organisatieSpecifiek.get('kvk')
    return kvk

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
    cpt = check_cpt_record_code(cpt)
    cpt = check_data_negative(cpt)
    cpt = check_datum(cpt)
    cpt = check_verticaal_referentie(cpt)

    # een te diepe start van de sondering zonder opgave van voorboring resulteert in een foutmelding
    # er zijn twee opties:
    # 1. measurement variable 13 - voorboring
    # 2. opvullen vanaf sondeerlengte 0 met dummy waarden
    # voor sommige bestanden werkt alleen optie 1, voor andere werkt alleen optie 2
    voorboringMeasurmentVar13 = False
    voorboringDummyVulling = True
    if voorboringMeasurmentVar13:
        check_voorboring_meas_var(cpt)
    elif voorboringDummyVulling:
        check_voorboring_dummy(cpt) # TODO: waarschijnlijk deze versie gaf bestanden met voorboring = 0, terwijl er wel voorgeboord was. Zie mail van bro 2 februari 2023

    # check of er een waterdipte is opgegeven via één regel met columnvoid waardes
    gebruikWaterdiepte, cpt.waterdepth = check_waterdiepte(cpt)

    # schrijf de data weg zonder header en index
    # om later weer in te lezen als platte tekst
    # direct omzetten met to_string kan een foutmelding geven bij omzetten naar XML vanwege initiële spatie
    cpt.data.to_csv('./datatemp.txt', index=False, header=False, sep=' ', na_rep='-9999.0')
    with open('./datatemp.txt', 'r') as dataTemp:
        content = dataTemp.read()

    # begin met wegschrijven
    with open(filePath, 'w') as f:
        f.write(
            f'#GEFID= {cpt.gefid["major"]},{cpt.gefid["minor"]},{cpt.gefid["build"]}\n' +
            f'#REPORTCODE= {cpt.reportcode["type"]},{cpt.reportcode["major"]},{cpt.reportcode["minor"]},{cpt.reportcode["build"]}\n' + 
            f'#PROCEDURECODE= {cpt.procedurecode["type"]},{cpt.procedurecode["major"]},{cpt.procedurecode["minor"]},{cpt.procedurecode["build"]}\n' + 
            f'#COMPANYID= \n' 
            f'#PROJECTID= {cpt.projectid}\n' +
            f'#TESTID= {cpt.testid}\n' +
            f'#XYID= 31000, {cpt.easting}, {cpt.northing}\n' +
            f'#ZID= 31000, {cpt.groundlevel}\n' +
            f'#FILEDATE= {cpt.filedate["year"]}, {cpt.filedate["month"]}, {cpt.filedate["day"]}\n' +
            f'#STARTDATE= {cpt.startdate["year"]}, {cpt.startdate["month"]}, {cpt.startdate["day"]}\n'
        )

        # voeg de measurementtexts toe
        for number, text in cpt.measurementtexts.items():
            f.write(f"#MEASUREMENTTEXT= {number}, {text}\n")
        if '9' not in cpt.measurementtexts.keys():
            f.write(f"#MEASUREMENTTEXT= 9, {cpt.verticalReference}\n")

        if voorboringMeasurmentVar13 and cpt.voorboring is not None:
            f.write(f"#MEASUREMENTVAR= 13, {cpt.voorboring}, m, -\n") 

        if gebruikWaterdiepte:
            f.write(f"#MEASUREMENTVAR= 15, {cpt.waterdepth},m,-\n")

        # measurementtext 101 met KvK-nummer van bronhouder is verplicht
        if not '101' in cpt.measurementtexts.keys():
            f.write(f"#MEASUREMENTTEXT= 101, {organisatieSpecifiek.get('naam')}, {organisatieSpecifiek.get('kvk')}, -\n") 
        
        # informatie wat er in welke kolom staat
        for number, text in cpt.columninfo.items():
            f.write(f"#COLUMNINFO= {number+1},{cpt.columninfoUnit[number]},{text},{cpt.columninfoQuantNr[number]}\n")

        # column void values zijn vervangen door -9999
        for colnr, voidvalue in enumerate(cpt.data.columns): #cpt.columnvoid_values.items():
            f.write(f'#COLUMNVOID= {colnr+1}, -9999.0\n')

        f.write(
                f'#COLUMN= {len(cpt.columninfo)}\n' + # aantal kolommen
                f'#LASTSCAN= {len(cpt.data)}\n' + # aantal meetpunten
                '#EOH=\n' +
                content # de data
        )

def check_al_in_BRO(cpt, buffer):
    # bepaal of op dit coördinaat al een sondering beschikbaar is binnen een buffer
    return Point(cpt.easting, cpt.northing).within(buffer)

def haal_xy_uit_GIS(cpt, gisData):
    # er zijn GEF waar geen xy-coördinaten in zitten omdat die in een GIS bestand werden bijgehouden.
    # deze functie voegt coördinaten uit het gis-bestand toe aan de cpt
    cpt.easting = gisData.loc[cpt.testid.rstrip(), 'geometry'].x
    cpt.northing = gisData.loc[cpt.testid.rstrip(), 'geometry'].y
    
    return cpt


def check_benodigdheden(cpt):
    # controle of alle benodigde elementen aanwezig zijn en een correcte waarde hebben
    checks = []
    if cpt.easting is not None and cpt.northing is not None:
        checks.append(float(cpt.easting) != 0.) # check of x en y niet 0 zijn, veel gef gemaakt zonder eigen xy (staan in een GIS)
        checks.append(float(cpt.northing) != 0.) # check of x en y niet 0 zijn, veel gef gemaakt zonder eigen xy (staan in een GIS)
    else:
        checks.append(False)
    checks.append(cpt.groundlevel is not None)
    checks.append(cpt.testid is not None) 
    checks.append(cpt.projectid is not None) 
    return checks


def check_in_bbox(cpt):
    # check of de locatie binnen een bounding box is
    westVanBox = cpt.easting > organisatieSpecifiek.get('west', 0)
    oostVanBox = cpt.easting < organisatieSpecifiek.get('oost', 999_999)
    noordVanBox = cpt.northing < organisatieSpecifiek.get('noord', 999_999)
    zuidVanBox = cpt.northing > organisatieSpecifiek.get('zuid', 0)

    return all([westVanBox, oostVanBox, noordVanBox, zuidVanBox])

def convert_batch(files, reedsGeleverd=None, gisData=None, verwijderDiepte=False):
    # wat dingen om bij te houden wat er wel en niet is omgezet
    columns=["testid", "x", "y", "lengte"]
    if reedsGeleverd is None:
        uniekCorrect = pd.DataFrame(columns=columns)
        j = 0
    else:
        uniekCorrect = pd.read_csv(reedsGeleverd, index_col=0) # TODO: dit verandert nogal eens in deze applicatie. Trek dat gelijk! , sep=';', decimal=','
        j = len(uniekCorrect)

    nietUniekCorrect = pd.DataFrame(columns=columns)
    i = 0

    # lees coördinaten uit GIS in
    if gisData is not None:
        gisData = gpd.read_file(gisData)
        gisData.set_index('TestID', drop=True, inplace=True)
        gisData = gisData[gisData['GEF_Type'] == 'GEF-CPT']

    # lees een GIS bestand in met locaties van onderzoek dat al in BRO aanwezig is
    broGpkg = organisatieSpecifiek.get('broGpkg', None)

    if broGpkg is not None:
        broCptVolledigeSet = gpd.read_file(broGpkg) 
        broCptVolledigeSet = broCptVolledigeSet.to_crs('epsg:28992')
        # maak een buffer om de punten van 1 meter vanwege afronding
        buffer = broCptVolledigeSet['geometry'].buffer(1).unary_union

    # maak een bestand om foutmeldingen te verzamelen
    with open('./output/errors.txt', 'w') as errors:
        for f in files:
            print(f)
            if f.lower().endswith('gef'):
                try:
                    cpt = Cpt()
                    # laad de cpt in
                    cpt.load_gef(f)

                    # diepte is soms groter dan sondeerlengte, dat is niet correct
                    # omdat diepte niet verplicht is, kan het verwijderd worden
                    if verwijderDiepte and 'depth' in cpt.data.columns:
                        # verwijder de kolom uit de data
                        cpt.data.drop(columns=['depth'], inplace=True)
                        # verwijder de gegevens uit de columninfo
                        for key, value in cpt.columninfoQuantNr.items():
                            if int(value) == 11: # depth is 11
                                del cpt.columninfo[key]
                                del cpt.columninfoQuantNr[key]
                                del cpt.columninfoUnit[key]
                                break

                    # doe checks of xyz-coördinaten, testid en projectid aanwezig zijn en niet 0
                    checkContents = check_benodigdheden(cpt)
                    # check of het bestand een duplicaat is

                    # check of er coördinaten zijn, als ze ontbreken inlezen uit GIS bestand 
                    if checkContents[0] == False and gisData is not None:
                        cpt = haal_xy_uit_GIS(cpt, gisData)
                        checkContents[0] = True

                    # check of de benodigde informatie aanwezig is (checkContents)
                    # en check of het geen dubbele is
                    if all(checkContents) and not (uniekCorrect[['x', 'y', 'lengte']] == [cpt.easting, cpt.northing, len(cpt.data)]).all(1).any():
                        
                        # check of op deze locatie al een sondering in de BRO zit.
                        if broGpkg is not None:
                            checkInBro = check_al_in_BRO(cpt, buffer) # geeft True als op deze locatie al een CPT in BRO aanwezig is
                        else:
                            checkInBro = False

                        # check of deze locatie binnen een bounding box valt
                        checkInBbox = check_in_bbox(cpt) # geeft True als de locatie binnen de bounding box is
                        if not checkInBro and checkInBbox:

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
                            # tellertje om mappen te kunnen maken met 100 stuks
                            i += 1
                        else:
                            # als al in BRO of als buiten bounding box, dan wat gegevens wegschrijven
                            nietUniekCorrect.loc[j] = [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]
                            # tellertje voor index van niet unieke of niet correcte bestanden
                            j += 1
                    else:
                        # als niet uniek of niet correct is, dan wat gegevens wegschrijven
                        nietUniekCorrect.loc[j] = [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]
                        # tellertje voor index van niet unieke of niet correcte bestanden
                        j += 1
                except Exception as e:
                    errors.write(f'{f}, {e}\n')
    
    # bestanden wegschrijven
    uniekCorrect.to_csv('./output/uniekCorrect.csv', sep=';', decimal=',')
    nietUniekCorrect.to_csv('./output/nietUniekCorrect.csv', sep=';', decimal=',')