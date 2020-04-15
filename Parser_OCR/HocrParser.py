import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import re,  logging
from lxml import etree

from Parser_WiTTFind.Parser_OCR.Ocr import Ocr, Page, Line

hocrLogger = logging.getLogger("hocrLogger")
hocrLogger.setLevel(logging.DEBUG)

def ns(tag):
    """
    Add the required namespace to the tag name
    """
    return '{http://www.w3.org/1999/xhtml}' + tag

class HocrParser:
    def __init__(self, hocr_path):

        self.tree=etree.parse(hocr_path)
        self.hocr_path=hocr_path
        self.file_name_from_image_file= ""
        self.page_number_from_image_file=""
        self.page_height=0
        self.page_width=0

        self.div_tags=[]
        self.span_tags=[]
        self.ocr_lines=[]
        self.ocr_pages=[]

        self.ocr_object=None
        self.parse_ocr_pages()
        self.parse_ocr_lines()
        self.parse_file_name()
        self.parse_page_number()
        self.parse_page_size()

    def parse_file_name(self):
        title_String=self.ocr_pages[0].get("title")
        #print(title_String)
        title=re.search(r'[TM]{1}[s]{1}-(\d+)[a-z]{0,1},[A-Z]{0,10}(\d*)[a-z]{0,1}', title_String).group() # Der reguläre Ausdruck passt auf eine Zeichenkette die mit einem Großbuchstaben T oder M beginnt, ein Bindestrich folgt
        self.file_name_from_image_file=title
        logging.debug("filename_from_image_file: " + self.file_name_from_image_file)

    def parse_page_number(self):
        #self.page_number_from_image_file = re.search(r',(...)', self.file_name_from_image_file).group(1)
        try:
            self.page_number_from_image_file=re.search(r',[0-9]{0,3}[XIVFCBC]{0,10}[rv]{0,1}', self.file_name_from_image_file).group()[1:]
            # Der Regex nimmt den String ab dem Komma, dann wird durch den Stringoperator in eckigen Klammern am Schluss das Komma abgeschnitten
            #print(self.file_name_from_image_file)
            #print(self.page_number_from_image_file)
        except:
            print(self.file_name_from_image_file)
            logging.error( "Fehler beim Parsen der Seitennummer!: " + self.hocr_path )

    def parse_page_size(self):
        title = self.ocr_pages[0].get("title")
        coordsSTR = re.search(r'bbox (\d+) (\d+) (\d+) (\d+);?', title).groups()
        coordsINT = [int(coord) for coord in coordsSTR]
        left, top, right, bottom = coordsINT
        coordinates_list = [left, top, right, bottom]
        self.page_width = coordinates_list[2]
        self.page_height = coordinates_list[3]

    def parse_div_tags(self):
        for div_tag in self.tree.findall('.//{}'.format(ns('div'))):
            self.div_tags.append(div_tag)

    def parse_ocr_pages(self):
        for div_tag in self.tree.findall('.//{}'.format(ns('div'))):
            if self.check_if_div_tag_is_page(div_tag):
                self.ocr_pages.append(div_tag)

    def parse_span_tags(self):
        for span_tag in self.tree.findall('.//{}'.format(ns('span'))):
            self.span_tags.append(span_tag)

    def parse_ocr_lines(self):
        for span_tag in self.tree.findall('.//{}'.format(ns('span'))):
            if self.check_if_span_tag_is_line(span_tag):
                self.ocr_lines.append(span_tag)

    def get_ocr_lines_from_given_element(self, element):
        '''
        Returns a list of ocr_line span elements found in the given element
        :param element: The element from wich the ocr_lines are parsed from
        :return: list of ocr_line span elements
        '''
        found_ocr_lines = []
        for span_tag in element.findall('.//{}'.format(ns('span'))):
            if self.check_if_span_tag_is_line(span_tag):
               found_ocr_lines.append(span_tag)
        return found_ocr_lines

    def check_if_span_tag_is_line(self, span_tag):
        if span_tag.get("class") == "ocr_line":
            return True
        else:
            return False

    def check_if_div_tag_is_page(self, div_tag):
        if div_tag.get("class") == "ocr_page":
            return True
        else:
            return False

    def parse_tag_text(self, span_tag):
        text = ' '.join(' '.join(span_tag.itertext()).split())
        return text

    def generate_coordinates_list(self, hocr_element):
        '''
        Generates an int-List containing the coordinates in the format x0,y0,x1,y1
        The method was adapted from Roman Capsamus first implementation
        :param hocr_element: the hocr_element to extract the coordinates from
        :return: A list of integer values representing the coordinates of the given element
        '''
        title = hocr_element.get("title")
        coordsSTR = re.match(r'bbox (\d+) (\d+) (\d+) (\d+);?', title).groups()
        coordsINT = [int(coord) for coord in coordsSTR]
        left, top, right, bottom = coordsINT
        coordinates_list = [left, top, right, bottom]
        return coordinates_list

    def generate_line_Objects(self, ocr_line_elements):
        '''
        Generates line objects
        :param ocr_line_elements:
        :return:
        '''
        generated_lines=[]
        for ocr_line in ocr_line_elements:
            new_line_object = Line()
            new_line_object.id=ocr_line.get("id")
            new_line_object.page = self.file_name_from_image_file
            new_line_object.coordinates=self.generate_coordinates_list(ocr_line)
            new_line_object.text=self.parse_tag_text(ocr_line)
            generated_lines.append(new_line_object)
        return generated_lines

    def generate_page_objects(self, page_elements):
        '''
        Generates page objects
        :param page_elements:
        :return:
        '''
        page_objects_list = []
        for ocr_page in page_elements:
            new_page_object = Page()
            new_page_object.id = self.file_name_from_image_file # Die Seitennummer kommt nur aus dem Dateinamen, ohne Dateiendung!!!
            new_page_object.lines=self.generate_line_Objects(self.get_ocr_lines_from_given_element(ocr_page))
            new_page_object.set_line_links()
            new_page_object.page_width=self.page_width
            new_page_object.page_height=self.page_height
            #print(new_page_object.page_height, new_page_object.page_width)
            page_objects_list.append(new_page_object)
        return page_objects_list

    def generate_ocr_object(self):
        '''
        Generates ocr object
        :return:
        '''
        self.ocr_object=Ocr()
        self.ocr_object.pages=self.generate_page_objects(self.ocr_pages)
        self.ocr_object.id=self.file_name_from_image_file
        self.ocr_object.pages[0].reduce_number_of_lines()
        return self.ocr_object

    def get_ocr_object(self):
        if self.ocr_object is not None:
            return self.ocr_object
        else:
            return "OCR Objekt wurde noch nicht erzeugt!"





