# gef naar gef 1.1.3 omzetter t.b.v. aanleveren als imbro/a
Deze applicatie:
* zet oude gef formaten om in gef 1.1.3. Er wordt informatie waar nodig aangevuld of aangepast. Deze bestanden kunnen vervolgens met het programma GEF-CPT2BRO-XML (van Fugro en Wiertsema & Partners, verkrijgbaar bij BRO) omgezet worden in IMBRO/A. De xml kunnen worden geleverd aan de BRO.
* Ook is er een optie om XMl te valideren en te leveren via de API van de BRO. Hiervoor zijn een inlognaam en wachtwoord benodigd.
Meer over de validatie op: [bro-website] https://basisregistratieondergrond.nl/inhoud-bro/aanleveren-gebruiken/tools-tips/validatieservice/
Meer over de API op: [bro-api] https://www.bronhouderportaal-bro.nl/doc/api.html

Voor gebruik van de API is een apart bestand met de naam organisatieSpecifiek.py nodig
Hierin staan username en wachtwoord voor de API, kvk-nummer en naam van de organisatie en
ook een link naar de bestandslocatie van de geopkg met sondeerlocaties die al aanwezig zijn in de BRO. Dit alles op te geven, met de onderstaande namen:
* username = '' Code bestaande uit letters en cijfers, wordt gegenereerd in het Bronhouderportaal
* password = '' Code bestaande uit letters en cijfers, wordt gegenereerd in het Bronhouderportaal
* projectId = '1234' Type: string. Dit is het projectnummer dat je vindt onder Projectgegevens in het bronhouderportaal
* kvk = '12345678' Type: string. Dit is het registratienummer van je organisatie bij de KvK
* broGpkg = './path/to/brocptvolledigeset_11-07-2022_14-09_v0.03.gpkg' Locatie en naam van een geopackage met sonderingen om dubbele te voorkomen.
* naam = 'Gemeente Amsterdam' Naam van je organisatie
* oost = 135000 Maximale RD x-coördinaat van het gebied waaruit je wil aanleveren
* west = 105000 Minimale RD x-coördinaat van het gebied waaruit je wil aanleveren
* noord = 495000 Maximale RD y-coördinaat van het gebied waaruit je wil aanleveren
* zuid = 476000 Minimale RD y-coördinaat van het gebied waaruit je wil aanleveren
De BRO CPT geopackage is te downloaden op: [PDOK] https://service.pdok.nl/bzk/brocptvolledigeset/atom/v1_0/brocptvolledigeset.xml. Dit bestand bevat sonderingen in heel Nederland en kan vanwege de verwerkingssnelheid beter eerst gefilterd worden voor het gebied waar je werkt.

## Dependencies
* Zie environment.yml
* [gefxml_reader](https://github.com/Amsterdam/gefxml_viewer)

# Heb je geen ervaring met Python? Volg dan deze stappen

## De applicatie opslaan
1. Voer eerst de stappen uit van de [gefxml_reader](https://github.com/Amsterdam/gefxml_viewer)
1. Ga naar de map _scripts_. Klik met de rechtermuisknop en kies voor _Git bash here_
1. Kopieer en plak (met rechtse muisknop of shift + Insert):
`git clone https://github.com/Amsterdam/gef2gef113.git`
1. Je kan het Git bash venster nu afsluiten met `exit`
1. Controleer of er in de map _lengteprofiel_ een map is met de naam _input_ en een map _output_

## GEF omzetten naar GEF 1.1.3
1. Ga naar de Windows startknop en type daar `cmd`
1. Kies _Anaconda Prompt (Miniconda3)_
1. Ga in de prompt naar de map _gef2gef113_ 
1. Kopieer en plak:
* `conda activate geo_env` (dit moet je iedere keer doen wanneer je begint met een sessie)
* `python gui_2gef113.py`
1. Klik _Select files_
1. Selecteer de bestanden die je om wil zetten
1. Klik _Continue_
1. Kijk in de map _output_ of daar mapjes met als naam een nummer gemaakt zijn
1. In deze mapjes staan de omgezette bestanden

## GEF 1.1.3 omzetten naar BRO-XML
1. Zet deze bestanden om naar BRO-XML met het programma _GEF-CPT2BRO-XML_

## BRO-XML bestanden valideren (dit is niet verplicht)
1. Kopieer en plak in de prompt nog eens:
* `python gui_2gef113.py`
1. Klik _Select Validate_
1. Selecteer een map met BRO-XML-bestanden die je wil valideren
1. Klik _Continue_
1. Er wordt een bestand in deze map gemaakt met het resultaat (valide / niet valide en reden)

## Aanleveren aan de BRO
1. Lever de bestanden op de gebruikelijke wijze aan bij de BRO. 
2. Of gebruik de functies die daarvoor beschikbaar zijn in functions.py
Tips hierbij:
* Doe het in kleine batches (maximaal 500 stuks per keer)

## Vragen of opmerkingen?
1. Stuur een bericht aan Thomas van der Linden, bijvoorbeeld via [LinkedIn](https://www.linkedin.com/in/tjmvanderlinden/)

## Resultaten?
1. Heb je mooie resultaten gemaakt met deze applicatie? We vinden het heel leuk als je ze deelt (en Thomas tagt)
