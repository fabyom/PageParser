from Parser_WiTTFind.Parser_Edition.EditionParser import EditionParser
from Parser_WiTTFind.Parser_OCR.HocrParser import HocrParser
from Parser_WiTTFind.Coordinates_Alignment.Alignment import allign_lines

hocr_path = ("/home/benutzer/Bilder/Ts-221a/Binaer_Schwelle_60_HOCR_PSM_3/Ts-221a,142.hocr")
hocr_parser = HocrParser(hocr_path)
ocr_objekt=hocr_parser.generate_ocr_object()


edition_parser = EditionParser('/home/benutzer/Bilder/Ts-221a/Edition/Ts-221a_OA_NORM.xml')
document_object = edition_parser.parse() # document_object ist vom Typ Edition, Python interne Repräsentation der NormXML Datei die übergeben wurde

test_ocr_page = ocr_objekt.pages[0]

test_edition_Page=document_object.pages[4]

test_edition_Page.fill_line_list()

aligned_page = allign_lines(test_edition_Page.lines, test_ocr_page.reduced_lines, test_edition_Page.id)

for aligned_line in aligned_page.aligned_lines:
 print(aligned_line)

for line in test_edition_Page.lines:
    print(line)
