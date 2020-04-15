'''
Created on 18.03.2018

@author: benutzer
'''

import xml.etree.ElementTree as ET, json, os, cv2, re

from string import punctuation
punctuation += '«°“”©‘’„—'

def load_JSON_data(path):
    fileHandler = open(path)
    data = json.load(fileHandler)
    fileHandler.close()
    return data

def save_JSON_data(path, data):
    fileHandler = open(path, "w")
    fileHandler.write(json.dumps(data, indent=2,
                                 separators=(',', ':'),
                                 sort_keys=True, ensure_ascii=False))
    fileHandler.close()
    
def leseKonfigurationsdatei(konfigurationsdateipfad):
    konfigurationsdatei=open(konfigurationsdateipfad, 'r')    
    zeilen=konfigurationsdatei.readlines()
    konfiguration={}    
    for zeile in zeilen:
        if (zeile[0:8]=="dokument"):
            konfiguration["dokument"]=zeile[9:-1]
        if(zeile[0:4]=="oben"):
            konfiguration["oben"]=zeile[5:-1]
        if (zeile[0:5]=="unten"):
            konfiguration["unten"]=zeile[6:-1]
        if (zeile[0:11]=="recto_links"):
            konfiguration["recto_links"]=zeile[12:-1]
        if (zeile[0:11]=="verso_links"):
            konfiguration["verso_links"]=zeile[12:-1]
        if (zeile[0:12]=="recto_rechts"):
            konfiguration["recto_rechts"]=zeile[13:-1]
        if (zeile[0:12]=="verso_rechts"):
            konfiguration["verso_rechts"]=zeile[13:-1]
    return konfiguration

'''
Methode zur Berechnung des Flächeninhalts von Vierecken angegeben durch Zwei XY-Koordinatenpare
@param TwoXYKoordinaten: Liste mit zwei XY-Koordinaten in der Form x0, y0, x1, y1
'''
def flaecheBerechnen(TwoXYKoordinaten):
    x0, y0, x1, y1 = TwoXYKoordinaten
    breite=y1-y0
    hoehe=x1-x0
    flaeche=hoehe*breite
    return flaeche

def erzeugeUniversalTextbereich(konfiguration, drehung='x'):
    y0=int(konfiguration['oben'])
    y1=int(konfiguration['unten'])
    if (drehung=='v'):
        x0=int(konfiguration['verso_links'])
        x1=int(konfiguration['verso_rechts'])
    else:
        x0=int(konfiguration['recto_links'])
        x1=int(konfiguration['recto_rechts'])
    ergebnis=x0,y0,x1,y1
    return ergebnis


def JSON_Ausgabe(JSONAusgabePfad, koordinaten, jsonSchluessel):
    ausgabe_json_datei=json.dumps(koordinaten, sort_keys=True, indent=3)
    print(ausgabe_json_datei)
    if os.path.isfile(JSONAusgabePfad):
        print("Datei existiert bereits")
        jsonDaten=load_JSON_data(JSONAusgabePfad)
        #print(jsonDaten)
        jsonDaten[jsonSchluessel]=koordinaten[jsonSchluessel]
        #print(jsonDaten)
        ausgabe_json_datei=json.dumps(jsonDaten, sort_keys=True, indent=3)
        datei=open(JSONAusgabePfad, 'w' )
        datei.write(ausgabe_json_datei)
        datei.close()
        
    else:
        print ("Lege eine neue JSON_Koordinatendatei an")
        datei=open(JSONAusgabePfad, 'w' )
        datei.write(ausgabe_json_datei)
        datei.close()

def output_highlighting_single_rectangle(einzelkoordinaten, originialbild, ausgabebild):
    """ Highlights paragraphs in original image

    This method opens the original image and highlights all found paragraphs.
    The highlighted paragraphs are then saved into a file.

    # Argumente
      einzelkoordinaten   : User defined filename for paragraph coordinates
      originialbild          : Filename of original image
      ausgabebild            : Filename of output image
    """
    img = cv2.imread(originialbild)
    x0, y0, x1, y1 = einzelkoordinaten
    cv2.rectangle(img, (x0, y0), (x1, y1), rot, 10)
    cv2.imwrite(ausgabebild, img)
    
blau=(255,0,0)

gruen=(0,255,0)

rot=(0,0,255)
    
def output_highlighting_multiple_rectangles(paragraph_coordinates, original_image, output_image, farbe=(50,50,50)):
    """ Highlights paragraphs in original image

    This method opens the original image and highlights all found paragraphs.
    The highlighted paragraphs are then saved into a file.

    # Arguments
      paragraph_coordinates   : User defined filename for paragraph coordinates
      original_image          : Filename of original image
      output_image            : Filename of output image
    """
    img = cv2.imread(original_image)
    for i in paragraph_coordinates:
        x0, y0, x1, y1 = i
        cv2.rectangle(img, (x0, y0), (x1, y1), farbe, 20)   
    cv2.imwrite(output_image, img)

def output_highlighting_absolute_Schwelle(paragraph_coordinates, original_image, output_image,schwellePixelProdukt):
    """ Highlights paragraphs in original image

    This method opens the original image and highlights all found paragraphs.
    The highlighted paragraphs are then saved into a file.

    # Arguments
      paragraph_coordinates   : User defined filename for paragraph coordinates
      original_image          : Filename of original image
      output_image            : Filename of output image
    """
    img = cv2.imread(original_image)
    for i in paragraph_coordinates:
        flaeche=flaecheBerechnen(i)
        if flaeche>schwellePixelProdukt:
            x0, y0, x1, y1 = i
            cv2.rectangle(img, (x0, y0), (x1, y1), (50, 50, 50), 20)   
    cv2.imwrite(output_image, img)

class XMLParser():
    """
    hocr-Parser_WiTTFind for tesseract hocr-output
    """
    def __init__(self, xml_path):
        """
        Constructor
        hocr_path = path to hocr-file
        """
        # Try to open the OCR-file
        try:
            hocr = open(xml_path).read()
        except:
            print("hocr-file not found.")
            print(xml_path)
            exit()
        try:
            body = re.match(r".+?(<Page.+</Page>).*",
                            hocr, re.DOTALL).group(1)
        except AttributeError:
            print("No body-tags")
            exit()
        # Parse <body> ... </body>
        root = ET.fromstring(body)
        # all line nodes
               
        ocr_page_path = "div[@class='ocr_page']"
        ocr_area_path = "div/div[@class='ocr_carea']"
        ocr_par_path  = "div/div/p[@class='ocr_par']"
        ocr_line_path = "div/div/p/span[@class='ocr_line']"
        
        self.ocrpages = [self.getPageVector(node)for node in root.findall(ocr_page_path) ] #if self.getPageVector(node)!= 0
        self.ocrareas = [self.getVector(node)for node in root.findall(ocr_area_path) if self.getVector(node)!= 0]
        self.ocrparagraphs = [self.getVector(node)for node in root.findall(ocr_par_path) if self.getVector(node)!=0]
        self.lines = [self.getVector(node) for node in root.findall(ocr_line_path)if self.getVector(node) != 0]

    def getVector(self, node):
        title = node.attrib.get("title")
        coordsSTR = re.match(r'bbox (\d+) (\d+) (\d+) (\d+);?', title).groups()
        coordsINT = [int(coord) for coord in coordsSTR]
        left, top, right, bottom = coordsINT
        vector = [left, top, right, bottom]
        return vector
 
    
    def getPageVector(self, node): # ACHTUNG!!!! Funktioniert nur bei Dokumenten Seitenzahl < 10 !!!
        title = node.attrib.get("title")
        xs=title[-20:-16]
        ys=title[-15:-11]
        x=int(xs)
        y=int(ys)
        vector = [0, 0, x, y]
        return vector



