import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from Parser_WiTTFind.Parser_OCR.HocrParser import HocrParser

# Durch die Methiode join path wird der Pfad zusammengebaut, der Konstruktor akzeptiert als Argument nur ein Argument (Dateipfad) ist sehr hilfreich bei Wechsel # # #zwischen verschiedenen BS,
# Docstring informieren über die Parameter, sie sind im Quellcode enthalten


hocr_path = ("/home/benutzer/Bilder/Ms-114/Binaer_Schwelle_60_HOCR_PSM_3/Ms-114,12r.hocr")
hocr_parser = HocrParser(hocr_path)

ocr_objekt=hocr_parser.generate_ocr_object()

for page in ocr_objekt.pages:
    for line in page.lines:
        print(line)
        print(type(line.page))
        print(line.coordinates)

testPage=ocr_objekt.pages[0]



print(hocr_parser.file_name_from_image_file)

print ("Ich bin fertig!")
