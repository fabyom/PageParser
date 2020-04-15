import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from lxml import etree

from Parser_WiTTFind.Parser_OCR.Alto import AltoDocument, AltoPage, AltoLine

def ns(tag):
    """
    Add the ALTO namespace to the tag name.
    """
    return '{http://www.loc.gov/standards/alto/ns-v2#}' + tag


class AltoParser:
    """
    Parser_WiTTFind to read a set of ALTO XML documents into a Python object graph containing the coordinates and content of each
    analysed text line.
    """
    def __init__(self, alto_path, document_id):
        self.document = AltoDocument(document_id)
        self.path = alto_path
        self.files = os.listdir(alto_path)

    def read_files(self):
        """
        Read the files in the alto_path of the parser and build the object graph from them.
        """
        for filename in self.files:
            full_path = self.path + "/" + filename
            tree = etree.parse(full_path)
            self.parse_page(os.path.splitext(filename)[0], tree)

    def parse_page(self, page_id, tree):
        """
        Read ALTO XML of a single page.
        Add the result to the page collection / document.
        :param page_id: Full name of the page, such as 'Ms-114,1r'.
        :param tree: ElementTree read from an ALTO XML file by lxml.
        """
        page = AltoPage(page_id)

        for text_line in tree.findall(".//{}".format(ns("TextLine"))):
            page.add_line(self.parse_line(text_line))

        self.document.add_page(page)

    @staticmethod
    def parse_line(text_line):
        """
        Parse a line from an ALTO document.

        :param text_line: An lxml TextLine element.
        :return: The line as an AltoLine object.
        """
        content = text_line[0].get("CONTENT")
        line_id = text_line.get("ID")
        hpos = text_line.get("HPOS")
        vpos = text_line.get("VPOS")
        height = text_line.get("HEIGHT")
        width = text_line.get("WIDTH")

        if len(text_line) > 1:
            print("WARNING: TextLine with more than one child does occur:", text_line[1].tag)

        return AltoLine(line_id, content, hpos, vpos, height, width)
