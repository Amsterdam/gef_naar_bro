import os
import pandas as pd
import sys

from functions import aanleveren, check_in_bbox, to_gef113, validate

sys.path.insert(0, '../gefxml_viewer')
from gefxml_reader import Cpt

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

checkInAdam = False
if checkInAdam:
    for i in range(vanMap, totMap+1):
        if not os.path.isdir(f'C:/Users/linden082/Documents/iets mis/buitenAdam/{i}/'):
            os.mkdir(f'C:/Users/linden082/Documents/iets mis/buitenAdam/{i}/')
        folder = f'C:/Users/linden082/Documents/{i}/xml'
        files = [f'{folder}/{f}' for f in os.listdir(folder) if f.lower().endswith('xml')]
        for f in files:

            oostVanA, westVanA, noordVanA, zuidVanA = check_in_bbox(folder)
            # als een van deze True is dan moet het bestand verplaatst worden
            if any([oostVanA, westVanA, noordVanA, zuidVanA]):
                filename = f.split('/')[-1]

                dest = f'C:/Users/linden082/Documents/iets mis/buitenAdam/{i}/{filename}'
                os.rename(f, dest)            # als een van deze True is dan moet het bestand verplaatst worden
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