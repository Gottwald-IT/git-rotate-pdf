import configparser
import tkinter as tk
from tkinter import Button, Canvas, Frame
from PIL import Image, ImageTk  # Pillow-Bibliothek für die Bildanzeige
import fitz  # PyMuPDF
from io import BytesIO
import screeninfo  # Zur Ermittlung der Bildschirmgröße
import os
import tempfile
import shutil

antwort = [None]  # Verwenden einer Liste für die mutable Referenz
def zeige_pdf_seite_und_frage(pdf_pfad):


    def set_antwort(drehung):
        antwort[0] = drehung
        window.destroy()

    def tastendruck(event):
        if event.char == 'd':
            set_antwort("drehen")
        elif event.char == 'l':
            set_antwort("links")
        elif event.char == 'r':
            set_antwort("rechts")
        elif event.char == 'w':
            set_antwort("weiter")
        elif event.char == 'b':
            set_antwort("beenden")

    window = tk.Tk()
    window.title("PDF Vorschau und Entscheidung")

    # Fenstergröße und Position einstellen
    screen = screeninfo.get_monitors()[0]
    window.geometry(f"{screen.width}x{screen.height}+0+0")

    # PDF-Seite anzeigen
    doc = fitz.open(pdf_pfad)
    seite = doc.load_page(0)
    pix = seite.get_pixmap()
    img = Image.open(BytesIO(pix.tobytes("png")))

    # Bildskalierung und Anzeige
    img_ratio = img.width / img.height
    new_height = min(img.height, screen.height - 120)
    new_width = int(new_height * img_ratio)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    img_tk = ImageTk.PhotoImage(img)
    canvas = Canvas(window, width=screen.width, height=screen.height - 120)
    canvas.create_image(screen.width // 2 - new_width // 2, (screen.height - 120) // 2 - new_height // 2, anchor="nw",
                        image=img_tk)
    canvas.pack()

    # Buttons
    button_frame = Frame(window)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)

    Button(button_frame, text="Drehen", command=lambda: set_antwort('drehen')).pack(side=tk.LEFT, padx=10, pady=10)
    Button(button_frame, text="Links", command=lambda: set_antwort('links')).pack(side=tk.LEFT, padx=10, pady=10)
    Button(button_frame, text="Rechts", command=lambda: set_antwort('rechts')).pack(side=tk.LEFT, padx=10, pady=10)
    Button(button_frame, text="Weiter", command=lambda: set_antwort('weiter')).pack(side=tk.LEFT, padx=10, pady=10)
    Button(button_frame, text="Beenden", command=lambda: set_antwort('beenden')).pack(side=tk.RIGHT, padx=10, pady=10)
    window.bind("<Key>", tastendruck)
    window.focus_set()
    window.mainloop()
    doc.close()

    return antwort[0]


def drehe_pdf_wenn_nötig(pdf_pfad, temp_verzeichnis):
    doc = fitz.open(pdf_pfad)
    geändert = False

    antwort = zeige_pdf_seite_und_frage(pdf_pfad)

    for seite in doc:
        aktuelle_rotation = seite.rotation
        if antwort == 'drehen':
            neue_rotation = (aktuelle_rotation + 180) % 360
            seite.set_rotation(neue_rotation)
            geändert = True
        elif antwort == 'links':
            neue_rotation = (aktuelle_rotation + 270) % 360
            seite.set_rotation(neue_rotation)
            geändert = True
        elif antwort == 'rechts':
            neue_rotation = (aktuelle_rotation + 90) % 360
            seite.set_rotation(neue_rotation)
            geändert = True
        elif antwort == 'beenden':
            doc.close()
            exit()  # Beendet das gesamte Programm sofort

    if geändert:
        temp_pfad = os.path.join(temp_verzeichnis, os.path.basename(pdf_pfad))
        doc.save(temp_pfad)
        doc.close()
        os.remove(pdf_pfad)
        shutil.move(temp_pfad, pdf_pfad)

def durchsuche_verzeichnis_und_drehe_pdfs(verzeichnis):
    with tempfile.TemporaryDirectory() as temp_verzeichnis:
        for root, dirs, files in os.walk(verzeichnis):
            for file in files:
                if file.endswith('.pdf'):
                    pdf_pfad = os.path.join(root, file)
                    drehe_pdf_wenn_nötig(pdf_pfad, temp_verzeichnis)
                    if antwort == 'beenden':
                        return  # Beendet das Durchsuchen der Verzeichnisse

# Konfiguration laden und Programm starten
config = configparser.ConfigParser()
config.read('config.ini')
verzeichnis = config['DEFAULT']['Verzeichnis']
durchsuche_verzeichnis_und_drehe_pdfs(verzeichnis)
