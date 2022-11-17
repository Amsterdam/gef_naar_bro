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

from functions import convert_batch, validate

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

if main_win.sourceFolder != '':
    filelist = os.listdir(main_win.sourceFolder)
    files = [f'{main_win.sourceFolder}/{f}' for f in filelist]
    convert_batch(files)

elif len(main_win.sourceFiles) > 0: 
    files = list(main_win.sourceFiles)
    convert_batch(files)


elif main_win.validateFiles != '':
    validate(main_win.validateFiles)


