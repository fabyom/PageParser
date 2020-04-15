def check_if_string_contains_alphabetic_characters(test_String):
    return any(c.isalpha() for c in test_String)

class Ocr:
    """
    Collection of pages: A manuscript or typoscript
    """

    def __init__(self):
        self.id = ''
        self.pages=[]

    def __str__(self):
        return self.id
    

class Page:
    def __init__(self):
        self.id = '' # String mit der Seitennummer
        self.lines = []
        self.reduced_lines = [] # Gekürzte Liste ohne Sinnlose zeile
        self.splitted_lines= [] # Liste mit einzelnen Worten
        self.page_height = 0
        self.page_width = 0

    def __str__(self):
        return self.id

    def set_line_links(self):
        for line in self.lines:
            line.Page=self

    def reduce_number_of_lines(self):
        '''
        The method reduces the number of lines!
        :return: nothing
        '''
        for line in self.lines:
            if check_if_string_contains_alphabetic_characters(line.text) and len(line.text) > 5:
                self.reduced_lines.append(line)

    def generate_splitted_lines(self, lines):
        '''
        The method splitts the line in single words and saves them into a word list
        :param lines:
        :return:
        '''
        self.splitted_lines = []
        for line in lines:
            splitted_line = line.text.split()
            self.splitted_lines.append(splitted_line)


class Line:
    """
    Represents a written line within a block (!= <s>)
    """

    def __init__(self):
        self.id = "" # Was im HOCR Attribut steht
        self.coordinates = "" # String list im Format [x0, y0, x1, y1]
        self.page = None # Page id als String erwartet
        self.text = ""
        
    def __str__(self):
        return_text="Zeile "+self.id+", Text: "+self.text
        return return_text