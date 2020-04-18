class PageLine:
    '''

    '''
    def __init__(self, line_id, content, hpos, vpos, height, width):
        self.page_id = ''
        self.line_id = line_id
        self.text = content

        self.x0 = int(hpos)
        self.y0 = int(vpos)
        self.x1 = int(hpos)+int(width)
        self.y1 = int(vpos)+int(height)


class PagePage:
    '''

    '''
    def __init__(self, page_id):
        self.page_id = page_id
        self.lines = []

    def add_line(self, line):
        line.page_id = self.page_id
        self.lines.append(line)


class PageDocument:
    '''

    '''
    def __init__(self, document_id):
        self.document_id = document_id
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)