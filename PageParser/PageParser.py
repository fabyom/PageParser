import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from lxml import etree
from PageUtil import *

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
            self.helper_function_for_understanding_tree(tree)
            root = tree.getroot()
            self.parse_page(os.path.splitext(filename)[0],root)

    def helper_function_for_understanding_tree(self,tree):
        #print(etree.tostring(tree))
        #print(len(tree))
        #root = tree.getroot()
        #print(root.tag)
        #print(etree.tostring(root))
        #for element in root.iter('*'):
        #    print(etree.tostring(element))
        #root.SubElement('Metadata')
        #metadata = root.Element('Metadata')
        #print(metadata)
        #page = tree.Element('Page')
        #imageRegion = tree.Element("ImageRegion")
        #print(imageRegion.tag)
       # children = list(imageRegion)
        #print(children)
        #print(imageRegion.id)
        #print(sorted(root.keys()))
        #for text_line in root.findall('.//{}'.format(ns('TextRegion'))):
            #print(text_line.keys())
            #content=text_line[1]
            #print(etree.tostring(content))
            #print(content.text)
            #print('contenttag: '+content.tag)
            #innerthings = content.attrib
            #print(innerthings)
            #tail = content.tail
            #print(tail)
            #print(content.find('.//Unicode'))
            #text = content.getchildren()
            #print(text.text)
            #print(content.getchildren())
            #for x in content.getchildren():
            #    print(etree.tostring(x))
            #    print('tag: '+x.tag)
            #    print('text: '+x.text)
            #    print('unicode: '+x.get('Unicode'))
            #print(innerthings)
            #print(etree.tostring(text_line[0]))
            #print(etree.tostring(text_line[1]))
            #print(len(content))
            #cont2 = content.attrib
            #print(cont2)
            #for x in content.iter:
            #    print(x.tag, x.text)

            #print(etree.tostring(text_line[2]))
            #print(etree.tostring(content))
            #print(content.get('Unicode'))
            #print('stop')
            #points = text_line[0].get('points')
            #print(points)
            #resarray = self.get_points_and_dimensions(points)
            #print(resarray)
            '''for elem in text_line:
                print(elem.keys())
                print(elem)
                points = elem.get('points')
                print(points)
                #elem.SubElement
                coords=elem.get('Coords')
                print(coords)'''
            #for elem in text_line.findall('Coord points'):
                #print(elem)
            #attributes = text_line.attrib
            #print(attributes)
            #print (etree.tostring(text_line))
            #print(text_line.tag)
            #print(attributes.get('id'))
            #print(text_line.SubElement.tag)
            #print(text_line.get('ID'))
            #coords = text_line.get('points')
            #coords = text_line.findall('.//{}'.format(ns('Coords points')))
            #print(etree.tostring(coords))
        #for child in text_line:
            #print(child.tag)
        #for child in root:
            #print(child.tag)
           # print(child.get('ID'))

    def parse_page(self, page_id, tree):
        '''

        :param page_id:
        :param tree:
        :return:
        '''
        page = PagePage(page_id)
        points = 0
        for text_line in tree.findall('.//'.format((ns('ImageRegion')))):
            try:  # hacky lösung TODO fehler besser abfangen
                points = text_line[0].get('points')
                if (points is not None):
                    dimensions = self.get_points_and_dimensions(points)
                    page.add_line(self.parse_line(text_line, dimensions))
                    self.document.add_page(page)
            except IndexError:
                continue

        for text_line in tree.findall('.//'.format(ns('TextRegion'))):
            try: #hacky lösung TODO fehler besser abfangen
                points = text_line[0].get('points')
                if (points is not None):
                    dimensions = self.get_points_and_dimensions(points)
                    page.add_line(self.parse_line(text_line,dimensions))
                    self.document.add_page(page)
            except IndexError:
                continue

    @staticmethod
    def parse_line(text_line,dimensions):
        '''

        :param text_line:
        :return:
        '''
        text = ''
        text_extraction_helper = text_line[1]
        for x in text_extraction_helper.getchildren():
            text = x.text
        attributes = text_line.attrib
        type = attributes.get('type')
        #content = text_line[0].get('CONTENT')
        content = text
        #line_id = text_line.get('ID')
        line_id = attributes.get('id')
        hpos= dimensions[0]
        vpos = dimensions[1]
        height = dimensions[2]
        width = dimensions[3]

        if len(text_line)>1:
            print('WARNING: TextLine with more than one child does occur:', text_line[1].tag)

        return PageLine(line_id,content,hpos,vpos,height,width)


    @staticmethod
    def get_points_and_dimensions(coord_points):
        coord_points = coord_points.replace('\'','')
        coord_points = coord_points.replace(',',' ')
        coord_points = list(map(int,coord_points.split(' ')))

        xmin = coord_points[0]
        ymin = coord_points[1]
        xmax = coord_points[0]
        ymax = coord_points[1]
        for i in range(0,len(coord_points),2):
            if(coord_points[i]<xmin):
                xmin=coord_points[i]
            if(coord_points[i]>xmax):
                xmax=coord_points[i]
        for i in range(1,len(coord_points),2):
            if(coord_points[i]<ymin):
                ymin=coord_points[i]
            if(coord_points[i]>ymax):
                ymax=coord_points[i]
        height = ymax-ymin
        width = xmax-xmin
        return([ymin,xmin,height,width])
