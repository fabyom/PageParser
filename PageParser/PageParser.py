import os
import sys

from lxml import etree

from PageUtil import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def ns(tag):
    """
    Add PAGEXML namespace to tag name
    :param tag: given tag
    :return: combined string
    """
    return '{http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15}'+tag


class PageParser:
    """
    class for a Page xml parser
    """

    def __init__(self, page_path, document_id):
        self.document = PageDocument(document_id)
        self.path = page_path
        self.files = os.listdir(page_path)

    def read_files(self):
        """
        xml files preprocessing
        :return: none
        """
        for filename in self.files:
            full_path = self.path+'/'+filename
            tree = etree.parse(full_path)
            root = tree.getroot()                                           # converting tree to root element for better information extraction
            self.parse_page(os.path.splitext(filename)[0], root)

    def parse_page(self, page_id, tree):
        """
        checks line of document if eligible,
        ignores lines without information (meta etc),
        uses functions parse_line and points_and_dimensions to extract information
        and appends information to document
        :param page_id: name of xml document
        :param tree: content of xml file
        :return: none
        """
        page = PagePage(page_id)
        for text_line in tree.findall('.//'.format((ns('TextRegion')))):    # search for key word TextRegion, other key words e.g. ImageRegion, SeparatorRegion
            try:  # hacky lösung                                            # ignore lines without coordinates
                points = text_line[0].get('points')                         # extract coordinate from line
                if points is not None:
                    dimensions = self.points_and_dimensions(points)         # calculate dimensions from pixel coordinates
                    page.add_line(self.parse_line(text_line, dimensions))   # extract information except pixels from line

            except IndexError:
                continue

        self.document.add_page(page)                                        # append information of given line to document

    @staticmethod
    def parse_line(text_line, dimensions):
        """
        parse and store the tag content and the coordinates
        :param dimensions: list with paragraph coordinates
        :param text_line: pagecontent of a given tag
        :return: list containing information about a text block
        """
        text = ''
        text_extraction_helper = text_line[1]
        for x in text_extraction_helper.getchildren():                      # extract recognized text from document
            text = x.text                                                   # convert to String
        content = text                                                      # save in defined content variable

        attributes = text_line.attrib                                       # extract attributes, id & type
        line_id = attributes.get('id')                                      # save id
        hpos = dimensions[0]                                                # get y min from array
        vpos = dimensions[1]                                                # get x min from array
        height = dimensions[2]                                              # get height from array
        width = dimensions[3]                                               # get width from array

        #if len(text_line) > 1:                                             # old warning from Alto Parser
        #    print('WARNING: TextLine with more than one child does occur:', text_line[1].tag)

        return PageLine(line_id, content, hpos, vpos, height, width)        # return all relevant information

    @staticmethod
    def points_and_dimensions(coord_points):
        """
        calculates dimension of block from given pixel coordinates
        by searching for highest & lowest value for each axis,
        subtracting lowest from highest to calculate height & width
        :param coord_points: extracted from document,
        form: "1468,3768 1467,3988 4963,4000 4964,3780" - type: String
        :return: list of coordinates & dimensions of a text region - type: int array
        [0] = y min
        [1] = x min
        [2] = height
        [3]= width
        """
        coord_points = coord_points.replace('\'', '')                       # manipulate String into int array
        coord_points = coord_points.replace(',', ' ')
        coord_points = list(map(int, coord_points.split(' ')))
        xmin = coord_points[0]                                              # using values from array for init values, ensuring correct extraction
        ymin = coord_points[1]
        xmax = coord_points[0]
        ymax = coord_points[1]
        for i in range(0, len(coord_points), 2):                            # extracting all x axis values
            if coord_points[i] < xmin:                                      # search for min
                xmin = coord_points[i]
            if coord_points[i] > xmax:                                      # search for max
                xmax = coord_points[i]
        for i in range(1, len(coord_points), 2):                            # extraction y axis values
            if coord_points[i] < ymin:                                      # search for min
                ymin = coord_points[i]
            if coord_points[i] > ymax:                                      # search for max
                ymax = coord_points[i]
        height = ymax-ymin                                                  # calculating height of block
        width = xmax-xmin                                                   # calculating width of block
        return [ymin, xmin, height, width]                                  # return array
