import sys, os
from lxml import etree
from PageUtil import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def ns(tag):
    '''
    Add PAGEXML namespace to tag name
    :param tag: given tag
    :return: combined string
    '''
    return '{http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15}'+tag


class PageParser:
    '''


    '''
    def __init__(self, page_path, document_id):
        self.document = PageDocument(document_id)
        self.path = page_path
        self.files = os.listdir(page_path)

    def read_files(self):
        '''

        :return:
        '''
        for filename in self.files:
            full_path = self.path+'/'+filename
            tree = etree.parse(full_path)
            root = tree.getroot()
            self.parse_page(os.path.splitext(filename)[0], root)

    def parse_page(self, page_id, tree):
        '''

        :param page_id: name of xml document
        :param tree: content of xml file
        :return: none
        '''
        page = PagePage(page_id)
        points = 0
        for text_line in tree.findall('.//'.format((ns('TextRegion')))):
            try:  # hacky lösung TODO fehler besser abfangen - hier wird null geliefert?
                points = text_line[0].get('points')
                if points is not None:
                    dimensions = self.get_points_and_dimensions(points)
                    page.add_line(self.parse_line(text_line, dimensions))

            except IndexError:
                continue

        self.document.add_page(page)

    @staticmethod
    def parse_line(text_line, dimensions):
        '''

        :param text_line:
        :return:
        '''
        text = ''
        text_extraction_helper = text_line[1]
        for x in text_extraction_helper.getchildren():
            text = x.text
        attributes = text_line.attrib
        content = text
        line_id = attributes.get('id')
        hpos = dimensions[0]
        vpos = dimensions[1]
        height = dimensions[2]
        width = dimensions[3]

        if len(text_line) > 1:
            print('WARNING: TextLine with more than one child does occur:', text_line[1].tag)

        return PageLine(line_id, content, hpos, vpos, height, width)


    @staticmethod
    def get_points_and_dimensions(coord_points):
        """

        :param coord_points:
        :return: list of coordinates of a text region
        """
        coord_points = coord_points.replace('\'', '')
        coord_points = coord_points.replace(',', ' ')
        coord_points = list(map(int, coord_points.split(' ')))

        xmin = coord_points[0]
        ymin = coord_points[1]
        xmax = coord_points[0]
        ymax = coord_points[1]
        for i in range(0, len(coord_points), 2):
            if(coord_points[i]<xmin):
                xmin=coord_points[i]
            if(coord_points[i]>xmax):
                xmax=coord_points[i]
        for i in range(1, len(coord_points), 2):
            if(coord_points[i]<ymin):
                ymin=coord_points[i]
            if(coord_points[i]>ymax):
                ymax = coord_points[i]
        height = ymax-ymin
        width = xmax-xmin
        return [ymin, xmin, height, width]
