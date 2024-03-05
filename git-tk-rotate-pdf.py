from __version__ import __version__

import tkinter as tk
from tkinter import Button
from PIL import Image, ImageTk  # Pillow-Bibliothek für die Bildanzeige

import configparser
import fitz  # PyMuPDF
import os
from matplotlib import pyplot as plt
from io import BytesIO
import tempfile
import shutil  # Zum Verschieben/Löschen von Dateien

def zeige_pdf_seite_und_frage(pdf_pfad):
    def ja_gedrückt():
        nonlocal antwort
        antwort = 'j'
        window.destroy()

    def nein_gedrückt():
        nonlocal antwort
        antwort = 'n'
        window.destroy()

    max_width = 800
    max_height = 600

    window = tk.Tk()
    window.title("PDF Vorschau und Entscheidung")

    doc = fitz.open(pdf_pfad)
    seite = doc.load_page(0)
    pix = seite.get_pixmap()
    img = Image.open(BytesIO(pix.tobytes("png")))

    # Bild skalieren, wenn es zu groß ist
    img_width, img_height = img.size
    scale = min(max_width / img_width, max_height / img_height, 1)
    img_width, img_height = int(img_width * scale), int(img_height * scale)
    img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)  # Geändert von Image.ANTIALIAS zu Image.Resampling.LANCZOS

    img_tk = ImageTk.PhotoImage(img)

    canvas = tk.Canvas(window, width=img_width, height=img_height)
    canvas.pack()

    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

    antwort = None

    ja_button = Button(window, text="Ja", command=ja_gedrückt)
    ja_button.pack(side=tk.LEFT)

    nein_button = Button(window, text="Nein", command=nein_gedrückt)
    nein_button.pack(side=tk.RIGHT)

    window.mainloop()
    doc.close()

    return antwort

def drehe_pdf_wenn_nötig(pdf_pfad, temp_verzeichnis):
    doc = fitz.open(pdf_pfad)
    geändert = False

    # Zeigt die erste Seite des PDFs an und fragt den Benutzer
    antwort = zeige_pdf_seite_und_frage(pdf_pfad)

    if antwort == 'j':
        for seite in doc:
            aktuelle_rotation = seite.rotation
            neue_rotation = (aktuelle_rotation + 180) % 360
            seite.set_rotation(neue_rotation)
            geändert = True

    if geändert:
        temp_pfad = os.path.join(temp_verzeichnis, os.path.basename(pdf_pfad))
        doc.save(temp_pfad)  # Speichert die bearbeitete PDF-Datei temporär
        doc.close()
        os.remove(pdf_pfad)  # Löscht die Original-PDF-Datei
        shutil.move(temp_pfad, pdf_pfad)  # Verschiebt die bearbeitete PDF zurück


def durchsuche_verzeichnis_und_drehe_pdfs(verzeichnis):
    # Verwendet das vom Betriebssystem bereitgestellte temporäre Verzeichnis
    with tempfile.TemporaryDirectory() as temp_verzeichnis:
        for root, dirs, files in os.walk(verzeichnis):
            for file in files:
                if file.endswith('.pdf'):
                    pdf_pfad = os.path.join(root, file)

                    drehe_pdf_wenn_nötig(pdf_pfad, temp_verzeichnis)

# Ersetzen Sie 'verzeichnis' mit dem tatsächlichen Pfad zum Verzeichnis mit Ihren PDF-Dateien
print (f"*******************************************************************")
print(f"GIT-ROTATE-PDF - Version {__version__}")
print (f"*******************************************************************")
print(f"Copyright 2024, Frank Gottwald IT, 64653 Lorsch")
print (f"*******************************************************************")
print(f"Das Programm durchsucht ein Verzeichnis aus der config.ini")
print(f"nach PDF Dateien. Es wird jeweils die erste Seite angezeigt")
print(f"und gefragt, ob das PDF gedreht werden soll. (j) dreht das PDF,")
print(f"jede andere antwort führt das Programm mit dem nächsten PDF ")
print(f"fort. Wurde das letzte PDF angezeigt wird das Programm beendet.")
print(f"Das Programm kann vorzeitig mit CTRL-C beendet werden.")
print (f"*******************************************************************")
print()
# Konfiguration laden
config = configparser.ConfigParser()
config.read('config.ini')
verzeichnis = config['DEFAULT']['Verzeichnis']
durchsuche_verzeichnis_und_drehe_pdfs(verzeichnis)
