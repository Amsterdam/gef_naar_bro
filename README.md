# gef naar gef 1.1.3 omzetter t.b.v. aanleveren als imbro/a
Deze applicatie:
* zet oude gef formaten om in gef 1.1.3. Er wordt informatie waar nodig aangevuld of aangepast. Deze bestanden kunnen vervolgens met het programma GEF-CPT2BRO-XML (van Fugro en Wiertsema & Partners, verkrijgbaar bij BRO) omgezet worden in IMBRO/A. De xml kunnen worden geleverd aan de BRO.
* Ook is er een optie om XML te valideren en te leveren via de API van de BRO. Hiervoor zijn een inlognaam en wachtwoord benodigd.  

Meer over de validatie op: [bro-website](https://basisregistratieondergrond.nl/inhoud-bro/aanleveren-gebruiken/tools-tips/validatieservice/)  
Meer over de API op: [bro-api](https://www.bronhouderportaal-bro.nl/doc/api.html)

Voor sommige onderdelen is een apart bestand met de naam _organisatieSpecifiek.py_ nodig
Hierin staan een variabelen die je kan opgeven als een dict met deze _keys_ (een toelichting op de _values_ staat eronder):

```python
organisatieSpecifiek = {  
    'username': username uit bro,  
    'password': password uit bro,  
    'projectId': projectid,  
    'kvk': kvk-nummer,  
    'naam': organisatienaam,  
    'broGpkg': adres van gpkg-bestand,  
    'oost': oostgrens,  
    'west': westgrens,  
    'noord': noordgrens,  
    'zuid': zuidgrens  
}
```

| Variabele | Type | Voorbeeld | Verplicht? | Toelichting |
|-----------|------|------------|------------|-------------|
| username | string | nvt | alleen voor validatie en levering aan BRO | Code bestaande uit letters en cijfers*¹ |
| password | string | nvt | alleen voor validatie en levering aan BRO | Code bestaande uit letters en cijfers*¹ |
| projectId | int | 1234 | alleen voor levering aan BRO | Projectnummer dat je vindt onder Projectgegevens in het bronhouderportaal |
| kvk | int | 12345678 | Verplicht | Registratienummer van je organisatie bij de KvK |
| naam | string | 'Gemeente Amsterdam' | Verplicht | Naam van je organisatie |
| broGpkg | string | './path/to/bestand.gpkg' | Optioneel | Locatie van een geopackage*² met cpt-locaties om dubbele te voorkomen |
| oost | int of float | 135000 | Optioneel | Maximale RD x-coördinaat van het gebied waaruit je wil aanleveren |
| west | int of float | 105000 | Optioneel | Minimale RD x-coördinaat van het gebied waaruit je wil aanleveren |
| noord | int of float | 495000 | Optioneel | Maximale RD y-coördinaat van het gebied waaruit je wil aanleveren |
| zuid | int of float | 476000 | Optioneel | Minimale RD y-coördinaat van het gebied waaruit je wil aanleveren |

\*¹ wordt gegenereerd in het Bronhouderportaal  
\*² De BRO CPT geopackage is te downloaden op: [PDOK](https://service.pdok.nl/bzk/brocptvolledigeset/atom/v1_0/brocptvolledigeset.xml). Dit bestand bevat sonderingen in heel Nederland en kan vanwege de verwerkingssnelheid beter eerst gefilterd worden voor het gebied waar je werkt.

## Dependencies
* geotexxx
* geopandas

# Heb je geen ervaring met Python? Volg dan deze stappen
## Benodigde programma's
1. Download en installeer deze programma's met de standaardinstellingen:
* [Miniconda](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)
* [Git](https://github.com/git-for-windows/git/releases/download/v2.36.1.windows.1/Git-2.36.1-64-bit.exe)

## De applicatie opslaan (dit is allemaal eenmalig)
1. Maak een map waarin je de bestanden willen opslaan, noem deze bijvoorbeeld _scripts_
1. Ga naar de map _scripts_. Klik met de rechtermuisknop en kies voor _Git bash here_
1. Kopieer en plak (met rechtse muisknop of shift + Insert):
`git clone https://github.com/Amsterdam/gef_naar_bro.git`
1. Je kan het Git bash venster nu afsluiten met `exit`
1. Controleer of er nu in de map _scripts_ een map is met de naam _gef\_naar\_bro_ en daarin een map is met de naam _output_ (let op kleine o, geen hoofdletter)
1. Is die er niet? Maak deze dan

1. Ga naar de Windows startknop en type daar `cmd`
1. Kies _Anaconda Prompt (Miniconda3)_
1. Ga in de prompt naar de map _gef\_naar\_bro_
1. kopieer en plak:
* `conda env create --file environment.yml`

## GEF omzetten naar GEF 1.1.3
1. Ga naar de Windows startknop en type daar `cmd`
1. Kies _Anaconda Prompt (Miniconda3)_
1. Ga in de prompt naar de map _gef\_naar\_bro_ 
1. Kopieer en plak:
* `conda activate geotexxx` (dit moet je iedere keer doen wanneer je begint met een sessie)
* `python gui_gef2gef113.py`
1. Klik _Select files_
1. Selecteer de bestanden die je om wil zetten
1. Klik _Continue_
1. Kijk in de map _output_ of daar mapjes met als naam een nummer gemaakt zijn
1. In deze mapjes staan de omgezette bestanden

## GEF 1.1.3 omzetten naar BRO-XML
1. Zet deze bestanden om naar BRO-XML met het programma _GEF-CPT2BRO-XML_

## BRO-XML bestanden valideren (dit is niet verplicht)
1. Kopieer en plak in de prompt nog eens:
* `python gui_gef2gef113.py`
1. Klik _Select Validate_
1. Selecteer een map met BRO-XML-bestanden die je wil valideren
1. Klik _Continue_
1. Er wordt een bestand in deze map gemaakt met het resultaat (valide / niet valide en reden)

## Aanleveren aan de BRO
1. Lever de bestanden op de gebruikelijke wijze aan bij de BRO via het bronhouderportaal 
2. Of gebruik de functies die daarvoor beschikbaar zijn in functions.py
Tips hierbij:
* Doe het in kleine batches (maximaal 500 stuks per keer)

## Vragen of opmerkingen?
1. Stuur een bericht aan Thomas van der Linden, bijvoorbeeld via [LinkedIn](https://www.linkedin.com/in/tjmvanderlinden/)

## Bedankt
Frank van Lier (gemeente Almere) voor het testen

## Resultaten?
1. Heb je mooie resultaten gemaakt met deze applicatie? We vinden het heel leuk als je ze deelt (en Thomas tagt)
