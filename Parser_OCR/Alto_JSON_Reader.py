import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import json, collections, logging

from Parser_WiTTFind.Parser_OCR.Ocr import Ocr, Page, Line

testcase=False

class Alto_JSON_Reader:

    def __init__(self, pfad):
        self.pfad = pfad
        self.datei=open(self.pfad)
        self.daten=json.load(self.datei)

        self.document_id=(self.daten["document_id"])
        print("Der Alto-Leser liest jetzt die JSON-Datei für: "+self.document_id)

        self.ocr_object = Ocr()
        self.ocr_object.id=self.document_id
        self.ocr_page_dict = collections.OrderedDict()

        self.Seitenliste=self.daten["pages"]

    def read_alto_file(self):
        for seite in self.Seitenliste:
            seite_id=seite["page_id"]
            #logging("Bearbeite Seite: "+seite["page_id"])
            neue_ocr_seite=Page()
            neue_ocr_seite.id=seite_id
            #neue_ocr_seite.page_height=seite["height"]
            #neue_ocr_seite.page_width=seite["width"]
            config=Config_JSON_Reader("/home/benutzer/Schreibtisch/Ms-114.conf.json").return_config()
            neue_ocr_seite.page_height=config[seite_id]["PAGE_HEIGHT"]
            neue_ocr_seite.page_width=config[seite_id]["PAGE_WIDTH"]


            zeilen=seite["lines"]
            for zeile in zeilen:
                neue_ocr_zeile=Line()
                neue_ocr_zeile.id=zeile["line_id"]
                neue_ocr_zeile.page=seite_id
                neue_ocr_zeile.text=zeile["text"]
                neue_ocr_zeile.coordinates=[zeile["x0"],zeile["y0"],zeile["x1"],zeile["y1"]]
                neue_ocr_seite.lines.append(neue_ocr_zeile)
                logging.debug("Der Alto Reader hat soeben folgende neue OCR-Zeile erzeugt: "+ str(neue_ocr_zeile))
            neue_ocr_seite.reduce_number_of_lines()
            neue_ocr_seite.generate_splitted_lines(neue_ocr_seite.lines)
            self.ocr_page_dict[neue_ocr_seite.id]=neue_ocr_seite
            logging.debug("OCR Page Dict Eintrag eingefügt: " + neue_ocr_seite.id)
        return self.ocr_page_dict

class Config_JSON_Reader:
    def __init__(self, pfad):
        self.pfad = pfad
        self.datei = open(self.pfad)
        self.daten = json.load(self.datei)

    def return_config(self):
        return self.daten


if testcase:
    print("Teste den ALTO-JSON-Reader")
    alto_json_reader = Alto_JSON_Reader("/home/benutzer/Schreibtisch/test_output.json")
    alto_json_reader.read_alto_file()



