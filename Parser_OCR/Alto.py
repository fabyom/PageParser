class AltoLine:
    """
    An AltoLine gets created from a TextLine element in ALTO XML.
    It holds the string content of the line, as well as its coordinates.
    """
    def __init__(self, line_id, content, hpos, vpos, height, width):
        self.page_id = ""  # e.g. Ms-114,100v
        self.line_id = line_id  # e.g. r1l1
        self.text = content  # string, can be empty

        # Bounding box of the line
        self.x0 = int(hpos)  # horizontal, a.k.a. left margin
        self.y0 = int(vpos)  # vertical, a.k.a. top margin
        self.x1 = int(hpos) + int(width)
        self.y1 = int(vpos) + int(height)


class AltoPage:
    """
    An AltoPage gets created from a single ALTO XML document.
    It holds a list of lines on the page, as well as the coordinates of the page's text area.
    """
    def __init__(self, page_id):
        self.page_id = page_id  # e.g. Ms-114,100v
        self.lines = []

    def add_line(self, line):
        line.page_id = self.page_id
        self.lines.append(line)


class AltoDocument:
    """
    Wrapper class for a collection of ALTO XML documents, i.e., for one document in WiTTFind.
    It holds a list of pages that are part of the document.
    """
    def __init__(self, document_id):
        self.document_id = document_id  # e.g. Ms-114
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)
