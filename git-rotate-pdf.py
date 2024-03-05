from __version__ import __version__
import configparser
import fitz  # PyMuPDF
import os
from matplotlib import pyplot as plt
from io import BytesIO
import tempfile
import shutil  # Zum Verschieben/Löschen von Dateien

# Konfiguration laden
config = configparser.ConfigParser()
config.read('config.ini')
verzeichnis = config['DEFAULT']['Verzeichnis']


def zeige_pdf_seite(pdf_pfad):
    doc = fitz.open(pdf_pfad)
    seite = doc.load_page(0)  # lädt die erste Seite
    pix = seite.get_pixmap()
    img_data = pix.tobytes("png")  # Konvertiert die Seite in PNG-Bytes
    img = BytesIO(img_data)  # Erstellt einen BytesIO Stream aus den Bilddaten

    plt.figure()  # Erstellt eine neue Figur für die Anzeige
    img_for_plt = plt.imread(img, format='png')  # Lädt das Bild aus dem BytesIO Stream
    plt.imshow(img_for_plt)
    plt.axis('off')  # Versteckt die Achsen
    plt.show()
    plt.close()  # Schließt das Fenster nach der Anzeige
    doc.close()


def drehe_pdf_wenn_nötig(pdf_pfad, temp_verzeichnis):
    doc = fitz.open(pdf_pfad)
    geändert = False

    # Zeigt die erste Seite des PDFs an und lässt den Benutzer entscheiden
    zeige_pdf_seite(pdf_pfad)
    antwort = input("Soll dieses PDF gedreht werden? (j/n): ").lower()
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
durchsuche_verzeichnis_und_drehe_pdfs(verzeichnis)
