# lengteprofiel
Dit script zet oude gef formaten om in gef 1.1.3. Er wordt informatie waar nodig aangevuld of aangepast.
Deze bestanden kunnen vervolgens met het programma GEF-CPT2BRO-XML (van Fugro en Wiertsema & Partners, verkrijgbaar bij BRO) omgezet worden in IMBRO/A.
De xml kunnen worden geleverd aan de BRO.
Ook is er een optie om XMl te valideren via de API van de BRO. Hiervoor zijn een inlognaam en wachtwoord benodigd.
Meer over de validatie op: [bro-website] https://basisregistratieondergrond.nl/inhoud-bro/aanleveren-gebruiken/tools-tips/validatieservice/

Er is een apart bestand met de naam organisatieSpecifiek.py nodig
Hierin staan wachtwoorden en kvk-nummer van de organisatie
en een link naar de bestandslocatie van de geopkg met sondeerlocaties die al aanwezig zijn in de BRO ?CHECK BIJ MARTIN WAAR JE DIE HAALT?
Dit alles op te geven als string, met de onderstaande namen
#validatieUsername = ''
#validatiePassword = ''
#kvk = ''
#broGpkg = ''


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
1. Selecteer de BRO-XML-bestanden die je wil valideren
1. Klik _Continue_
1. In de prompt verschijnt nu steeds de bestandsnaam en de reactie van de BRO

## Aanleveren aan de BRO
1. Lever de bestanden op de gebruikelijke wijze aan bij de BRO. Tips hierbij:
* Doe het in kleine batches (maximaal 500 stuks per keer)

## Vragen of opmerkingen?
1. Stuur een bericht aan Thomas van der Linden, bijvoorbeeld via [LinkedIn](https://www.linkedin.com/in/tjmvanderlinden/)

## Resultaten?
1. Heb je mooie resultaten gemaakt met deze applicatie? We vinden het heel leuk als je ze deelt (en Thomas tagt)
