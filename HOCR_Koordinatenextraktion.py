'''
Created on 16.01.2018
'''

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import argparse
from Parser_WiTTFind.Text_Area_Recognition_and_Config_File_Generation.Werkzeugkasten import *

arg_parser = argparse.ArgumentParser(description="""Programm zur Extrahierung der Koordinaten""")
arg_parser.add_argument("verzeichnis", help="Pfad des HOCR-Verzeichnis")
arg_parser.add_argument("datei", help="Name der HOCR-Datei")
arg_parser.add_argument("quellpfad", help="Pfad der Quellbilder zur Hervorhebung")
arg_parser.add_argument("zielpfad", help="Zielordner")
arguments = arg_parser.parse_args()

xmlOrdner = arguments.verzeichnis
print("xmlOrdner: ", xmlOrdner)
arbeitsordner = "D:\LMU\Informationsver\seminar"                            # os.path.split(hocrOrdner)[0]

datei = arguments.datei
rohdatei = datei[0:-5]

drehung='x'
if (rohdatei[-1]=='r' or rohdatei[-1]=='v'): 
    drehung=rohdatei[-1]

zielpfad = arguments.zielpfad
quellpfad = arguments.quellpfad
print(arbeitsordner)
konfiguration=leseKonfigurationsdatei(arbeitsordner+"/Konfiguration.txt")


schwellePixelProdukt=1000000 # Nutzt einen absoluten Wert in Pixel! Der vorhandene Wert ist z.B. geeignet für MS-102
relativeSchwelle=50 # Nutzt die relative Größe des ermittelten Textbereiches verglichen mit der Gesamtfläche der Seite


def geeigneteFlaecheBestimmenAbsolut(paragraph_coordinates):
    ergebnis=1, 1, 1, 1
    anfangsErgebnis=ergebnis
    for i in paragraph_coordinates:
        flaeche=flaecheBerechnen(i)
        if flaeche>schwellePixelProdukt:
            ergebnis = i
    if ergebnis == anfangsErgebnis:
        ergebnis = erzeugeUniversalTextbereich(konfiguration, drehung)
    return ergebnis


def geeigneteFlaecheBestimmenRelativ(paragraph_coordinates, relativeSchwelle = 50):
    ergebnis=[1,1,1,1]
    anfangsErgebnis=ergebnis
    for i in paragraph_coordinates:
        flaeche=flaecheBerechnen(i)
        prozentualerAnteilDerFlaecheAnDerSeite=flaeche/einProzentDerSeitenflaeche
        if prozentualerAnteilDerFlaecheAnDerSeite>relativeSchwelle or True:
            print("Doa", i)
            if ergebnis == anfangsErgebnis:
                print("Hier kommt Berta")
                ergebnis=i
            else:
                print ("Hier kommt Else")
                x0, y0, x1, y1= i
                if ergebnis[0] > x0:
                    ergebnis[0] = x0
                if ergebnis[1] > y0:
                    ergebnis[1] =y0
                if ergebnis[2] < x1:
                    ergebnis[2] =x1
                if ergebnis[3] < y1:
                    ergebnis[3] =y1

    if ergebnis==anfangsErgebnis:
        ergebnis=erzeugeUniversalTextbereich(konfiguration, drehung)
    return ergebnis

parserobjekt = XMLParser(xmlOrdner + "/" + datei)
paragraphes=parserobjekt.ocrparagraphs
print(paragraphes)
areas=parserobjekt.ocrareas
lines=parserobjekt.lines

page=parserobjekt.ocrpages[0]
einProzentDerSeitenflaeche=(flaecheBerechnen(page)/100)

textBereich=geeigneteFlaecheBestimmenRelativ(areas)
flaecheDesTextBereiches=flaecheBerechnen(textBereich)
prozentualerAnteilDesTextbereichesAnDerSeite=flaecheDesTextBereiches/einProzentDerSeitenflaeche

#print (prozentualerAnteilDesTextbereichesAnDerSeite)

#ueberpruefteParagrafen=[]
#paragrafenListe=parserobjekt.paragrafenObjektListe
#anzahlderParagrafen=len(paragrafenListe)
#paragrafenListe[1].printCoordinates()

#print(areas)
#print("Achtung: ",page)

# Verschiedene Bereiche
# output_highlighting_multiple_rectangles(paragraphes, quellpfad+"/"+rohdatei+".jpg", "/home/benutzer/Schreibtisch/test.jpg", rot)
# output_highlighting_multiple_rectangles(lines, "/home/benutzer/Schreibtisch/test.jpg", "/home/benutzer/Schreibtisch/test.jpg", blau)
# output_highlighting_multiple_rectangles(areas, "/home/benutzer/Schreibtisch/test.jpg", "/home/benutzer/Schreibtisch/test.jpg", gruen)
jsonSchluessel=rohdatei

#output_highlighting_absolute_Schwelle(areas, quellpfad+"/"+rohdatei+".jpg", zielpfad+"/"+rohdatei+"_hervorgehoben.jpg", schwellePixelProdukt)

output_highlighting_single_rectangle(textBereich, quellpfad+"/"+rohdatei+".jpg", zielpfad+"/"+rohdatei+"_hervorgehoben.jpg")

koordinaten={}

koordinaten['version']='b'

koordinaten[jsonSchluessel]={
  'PAGE_WIDTH': page[2],
  'PAGE_HEIGHT': page[3],
  "MARGIN_TOP": textBereich[1],
  "MARGIN_LEFT": textBereich[0],
    "MARGIN_DOWN": textBereich[3],
    "MARGIN_RIGHT": textBereich[2],
  "BLOCK_WIDTH": textBereich[2]-textBereich[0],
  "BLOCK_HEIGHT": textBereich[3]-textBereich[1]
  }


#print (koordinaten)

JSONAusgabePfad=arbeitsordner+"/"+konfiguration["dokument"]+".conf.json"

print(JSONAusgabePfad)

JSON_Ausgabe(JSONAusgabePfad, koordinaten, jsonSchluessel)


def higlight_OCR_in_different_results():
    # Verschiedene Bereiche
    output_highlighting_multiple_rectangles(paragraphes, quellpfad+"/"+rohdatei+".jpg", "/home/benutzer/Schreibtisch/test.jpg", rot)
    output_highlighting_multiple_rectangles(lines, "/home/benutzer/Schreibtisch/test.jpg", "/home/benutzer/Schreibtisch/test.jpg", blau)
    output_highlighting_multiple_rectangles(areas, "/home/benutzer/Schreibtisch/test.jpg", "/home/benutzer/Schreibtisch/test.jpg", gruen)
