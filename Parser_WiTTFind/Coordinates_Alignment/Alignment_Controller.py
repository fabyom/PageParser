import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import argparse, logging
from pathlib import Path

from Parser_WiTTFind.Parser_OCR.HocrParser import HocrParser
from Parser_WiTTFind.Parser_OCR.Alto_JSON_Reader import Alto_JSON_Reader
from Parser_WiTTFind.Parser_Edition.EditionParser import EditionParser
from Parser_WiTTFind.Coordinates_Alignment.Alignment import *

# Hier werden die Parameter geparst
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("Arbeitsverzeichnis", help="Arbeitsverzeichnis: z.B.: /home/benutzer/Bilder/Ms-101")
args=arg_parser.parse_args()

# Hier werden die Pfade angelegt
working_directory_path=Path(args.Arbeitsverzeichnis)
document_name=working_directory_path.name
norm_edition_file_path = working_directory_path.joinpath(Path("Edition/"+document_name+"_OA_NORM.xml"))
ausgabepfad=working_directory_path.joinpath(Path(document_name+"_coordinates_relative.json"))

# In diesem Block werden die Informationen aus der Edition angelegt
edition_parser = EditionParser(str(norm_edition_file_path))
document_object_from_Edition_Parser = edition_parser.parse()

# In diesem Block werden die Informationen aus der OCR angelegt
hocr_directory_path = working_directory_path.joinpath("Binaer_Schwelle_60_HOCR_PSM_3")
hocr_object_dict = OrderedDict()
ocr_page_dict = OrderedDict()
counter = 0
if document_name.startswith("Ts"): # Falls es sich um HOCR-Daten handelt
    logging.info("Der HOCR-Pfad ist:" + str(hocr_directory_path))
    for filename in os.listdir(str(hocr_directory_path)):
        if filename.endswith(".hocr"):
            counter += 1
            hocr_filepath=hocr_directory_path.joinpath(filename)
            print(str(hocr_filepath))
            logging.debug("Aktueller Ausführungsdurchlauf, Zähler: " + str(counter) + " Pfad: "+ str(hocr_filepath))
            hocr_parser = HocrParser(str(hocr_filepath))
            hocr_object = hocr_parser.generate_ocr_object()
            logging.debug("OCR-Objekt-iD" +" " + hocr_object.id)
            hocr_object_dict[hocr_object.id]=hocr_object
            ocr_page_dict[hocr_object.pages[0].id]=hocr_object.pages[0]
        else:
            continue
elif document_name.startswith("Ms"): #OCR-Quelle Alto-XML
    alto_json_reader = Alto_JSON_Reader("/home/benutzer/Schreibtisch/test_output.json")
    ocr_page_dict=alto_json_reader.read_alto_file()

logging.debug("OCR-Page-Dict: "+str(ocr_page_dict))

# Abgleich Block
error_list = []
aligned_page_list = []

# In dieser Schleife werden die alignierten Seiten angelegt
for edition_page in document_object_from_Edition_Parser.pages:
    #print(edition_page)
    try:
        corresponding_ocr_page=ocr_page_dict[str(edition_page.id)]
    except:
        logging.error("Fehler beim Anlegen der alignierten Seite: "+ str(edition_page.id)+ " HOCR-Datei bzw. Faksimile fehlt")
        error_list.append(edition_page)
        continue
        pass
    edition_page.fill_line_list()
    try:
        aligned_page = allign_lines(edition_page.lines, corresponding_ocr_page.reduced_lines, edition_page.id)
    except:
        print("Fehler beim alignieren: ")
        continue
    aligned_page.set_coreesponding_ocr_page(corresponding_ocr_page)
    aligned_page.set_coresponding_edition_page(edition_page)
    aligned_page.create_blocks_from_lines()
    aligned_page_list.append(aligned_page)
    if aligned_page.id=="Ts-220,48":
        test=aligned_page.show_lines_in_comparison()
        print(test)


print("Schreibe Ausgabe nach: ", ausgabepfad)

aligned_document = Aligned_Document()
aligned_document.aligned_pages = aligned_page_list
aligned_document.save_json(str(ausgabepfad))

print("Abgeschlossen!")