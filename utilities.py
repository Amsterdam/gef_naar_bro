import os
import pandas as pd
import geopandas as gpd
import sys
import math

from functions import aanleveren, check_al_in_BRO, check_benodigdheden, check_in_bbox, to_gef113, validate

sys.path.insert(0, '../gefxml_viewer')
from gefxml_reader import Cpt

import organisatieSpecifiek

hoofdMap = 'C:/Users/linden082/Documents/batch1run2'
outputMap = f'{hoofdMap}/batch1run2'
vanMap = 0
totMap = 6

doRun2 = False
if doRun2:
    # onderstaande is om bestanden die niet valide opnieuw om te zetten
    # in de eerste run waren er vaker terugkerende fouten:
    # 1. datum uitvoering na datum rapportage
    # 2. voorboring op onjuiste wijze opgegeven
    # bestanden waarvoor dit geldt staan in de map 'iets mis'
    broCptVolledigeSet = gpd.read_file(organisatieSpecifiek.broGpkg)
    broCptVolledigeSet = broCptVolledigeSet.to_crs('epsg:28992')
    buffer = broCptVolledigeSet['geometry'].buffer(1).unary_union
    columns=["testid", "x", "y", "lengte"]
    uniekCorrect = pd.DataFrame(columns=columns)
    nietUniekCorrect = pd.DataFrame(columns=columns)
    j, k = 0, 0 # bestandenteller

    # itereer de mappen
    for i in range(vanMap, totMap+1):
        print(f'start map {i}')
        # itereer de bestanden in de map
        folder = f"{hoofdMap}/iets mis/{i}"
        files = [f.split('.')[0] for f in os.listdir(folder) if 'gef' in f.lower() or 'xml' in f.lower()]

        with open(f'{outputMap}/errors.txt', 'w') as errors:

            for f in files:
                print(f)
                try:
                    cpt = Cpt()

                    gefFile = f'../../data/cpt/GEF/niet_omegam/{f}.gef'
                    cpt.load_gef(gefFile)

                    checkContents = check_benodigdheden(cpt)
                    if all(checkContents) and not (uniekCorrect[['x', 'y', 'lengte']] == [cpt.easting, cpt.northing, len(cpt.data)]).all(1).any():
                        checkInBro = check_al_in_BRO(cpt, buffer)
                        checkInBbox = check_in_bbox(cpt)
                        if not checkInBro and checkInBbox:
                            uniekCorrect.loc[i] = [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]
                            if not os.path.isdir(f'{outputMap}/{math.floor(j/100)}'):
                                os.mkdir(f'{outputMap}/{math.floor(j/100)}')

                            filePath = f"{outputMap}/{math.floor(j/100)}/{f}.gef"
                            to_gef113(cpt, filePath)

                            j += 1
                        else:
                            # als al in BRO of als buiten bounding box, dan wat gegevens wegschrijven
                            nietUniekCorrect.loc[k] = [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]
                            # tellertje voor index van niet unieke of niet correcte bestanden
                            k += 1
                    else:
                        # als niet uniek of niet correct is, dan wat gegevens wegschrijven
                        nietUniekCorrect.loc[j] = [cpt.testid, cpt.easting, cpt.northing, len(cpt.data)]
                        # tellertje voor index van niet unieke of niet correcte bestanden
                        j += 1
                except Exception as e:
                    errors.write(f'{f}, {e}\n')

    uniekCorrect.to_csv(f'{outputMap}/uniekCorrect.csv', sep=';', decimal=',')
    nietUniekCorrect.to_csv(f'{outputMap}/nietUniekCorrect.csv', sep=';', decimal=',')

doOpnieuw = False
if doOpnieuw:
    # onderstaande is om een correctie uit te kunnen voeren
    # in veel bestanden ontbreekt een voorboordiepte vanwege een onhandige check
    # die bestanden kunnen opnieuw omgezet worden in gef113
    for i in range(vanMap, totMap+1):
        validatieResult = pd.read_csv(f'{hoofdMap}/{i}/xml/validate.csv', sep=';')
        nietValide = validatieResult[validatieResult['status'] == 'NIET_VALIDE']
        nietValide['filename'] = nietValide['Unnamed: 0'].str.split('/').str.get(-1)
        for filename in nietValide['filename']:
            cpt = Cpt()
            try:
                f = f"C:/Users/linden082/data/cpt/GEF/niet_omegam/{filename.replace('xml', 'gef')}"
                cpt.load_gef(f)
                print(f)
            except:
                f = f"C:/Users/linden082/data/cpt/GEF/niet_omegam/{filename.replace('xml', 'GEF')}"
                cpt.load_gef(f)
                print(f)
                
            filePath = f"{hoofdMap}/{i}/{filename.replace('xml', 'gef')}"
            
            to_gef113(cpt, filePath)

doValidatie = False
if doValidatie:
    for i in range(vanMap, totMap+1):
        folder = f'{hoofdMap}/batch1run2/{i}/xml'
        validate(folder)

moveInvalidXML = False
if moveInvalidXML:
    for i in range(vanMap, totMap+1):
        validatieResult = pd.read_csv(f'{hoofdMap}/{i}/xml/validate.csv', sep=';')
        nietValide = validatieResult[validatieResult['status'] == 'NIET_VALIDE']
        nietValide['filename'] = nietValide['Unnamed: 0'].str.split('/').str.get(-1)

        if not os.path.isdir(f'{hoofdMap}/iets mis/{i}/'):
            os.mkdir(f'C:/Users/linden082/Documents/iets mis/{i}/')

        for filename in nietValide['filename']:
            f = f'{hoofdMap}/{i}/xml/{filename}'
            dest = f'{hoofdMap}/iets mis/{i}/{filename}'
            os.rename(f, dest)

checkInAdam = False
if checkInAdam:
    for i in range(vanMap, totMap+1):
        if not os.path.isdir(f'{hoofdMap}/iets mis/buitenAdam/{i}/'):
            os.mkdir(f'{hoofdMap}/iets mis/buitenAdam/{i}/')
        folder = f'{hoofdMap}/Documents/{i}/xml'
        files = [f'{folder}/{f}' for f in os.listdir(folder) if f.lower().endswith('xml')]
        for f in files:

            oostVanA, westVanA, noordVanA, zuidVanA = check_in_bbox(folder)
            # als een van deze True is dan moet het bestand verplaatst worden
            if any([oostVanA, westVanA, noordVanA, zuidVanA]):
                filename = f.split('/')[-1]

                dest = f'{hoofdMap}/iets mis/buitenAdam/{i}/{filename}'
                os.rename(f, dest)            # als een van deze True is dan moet het bestand verplaatst worden
            if any([oostVanA, westVanA, noordVanA, zuidVanA]):
                filename = f.split('/')[-1]

                dest = f'{hoofdMap}/iets mis/buitenAdam/{i}/{filename}'
                os.rename(f, dest)

doLeveren = True
if doLeveren:
    folders = [f'{hoofdMap}/{i}/xml' for i in range(vanMap, totMap+1)]
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