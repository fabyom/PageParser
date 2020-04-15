import os, argparse, logging
from collections import OrderedDict
from Parser_WiTTFind.Coordinates_Alignment.Alignment import *
from Parser_WiTTFind.Parser_OCR.Alto_JSON_Reader import Alto_JSON_Reader

# Hier werden die Parameter geparst
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("Arbeitsverzeichnis", help="Arbeitsverzeichnis")
arg_parser.add_argument("Dokumentenname", help="Name des Dokuments")
args=arg_parser.parse_args()
arbeitsverzeichnis=args.Arbeitsverzeichnis
document_name=args.Dokumentenname

# In diesem Block werden die Informationen aus der Edition angelegt
norm_edition_file_path = arbeitsverzeichnis+document_name+"/Edition/"+args.Dokumentenname+"_OA_NORM.xml"
edition_parser = EditionParser(norm_edition_file_path)
document_object = edition_parser.parse()

# In diesem Block werden die Informationen aus der OCR angelegt
hocr_directory_path = arbeitsverzeichnis+document_name+"/Binaer_Schwelle_70_HOCR_PSM_3"
ocr_object_dict = OrderedDict()
ocr_page_dict = OrderedDict()

# Hier werden
counter = 0
if document_name.startswith("Ts"): # Falls es sich um HOCR-Daten handelt
    logging.info("Der HOCR-Pfad ist:" + hocr_directory_path)
    for filename in os.listdir(hocr_directory_path):
        if filename.endswith(".hocr"):
            counter += 1
            hocr_filepath=os.path.join(hocr_directory_path, filename)
            logging.debug("Aktueller Ausführungsdurchlauf, Zähler: " + str(counter) + " Pfad: "+ hocr_filepath)
            hocr_parser = HocrParser(hocr_filepath)
            ocr_object = hocr_parser.generate_ocr_object()
            logging.debug("OCR-Objekt-iD"+" "+ ocr_object.id)
            ocr_object_dict[ocr_object.id]=ocr_object
            ocr_page_dict[ocr_object.pages[0].id]=ocr_object.pages[0]
        else:
            continue
elif document_name.startswith("Ms"): #OCR-Quelle Alto-XML
    alto_json_reader = Alto_JSON_Reader("/home/benutzer/Schreibtisch/test_output.json")
    ocr_page_dict=alto_json_reader.read_alto_file()

print("OCR-Page-Dict: "+str(ocr_page_dict))

# Abgleich Block
error_list = []
aligned_page_list = []

# In dieser Schleife werden die Alignierten Seiten angelegt
for edition_page in document_object.pages:
    #print(edition_page)
    try:
        corresponding_ocr_page=ocr_page_dict[str(edition_page.id)] # +"."] #Für Ts-235
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

ausgabepfad=arbeitsverzeichnis+document_name+"_coordinates_relative.json"
print("Schreibe Ausgabe nach: ", ausgabepfad)

aligned_document = Aligned_Document()
aligned_document.aligned_pages = aligned_page_list
aligned_document.save_json(ausgabepfad)

print("Abgeschlossen!")