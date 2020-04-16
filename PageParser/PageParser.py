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
    return '{https://www.primaresearch.org/schema/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd}'+tag


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
            self.parse_page(os.path.splitext(filename)[0],tree)

    def parse_page(self, page_id, tree):
        '''

        :param page_id:
        :param tree:
        :return:
        '''
        page = PagePage(page_id)

        for text_line in tree.findall('.//{}'.format((ns('TextLine')))):
            page.add_line(self.parse_line(text_line))

        self.document.add_page(page)

    @staticmethod
    def parse_line(text_line):
        '''

        :param text_line:
        :return:
        '''
        content = text_line[0].get('CONTENT')
        line_id = text_line.get('ID')
        hpos= text_line.get('HPOS')
        vpos = text_line.get('VPOS')
        height = text_line.get('HEIGHT')
        width = text_line.get('WIDTH')

        if len(text_line)>1:
            print('WARNING: TextLine with more than one child does occur:', text_line[1].tag)

        return PageLine(line_id,content,hpos,vpos,height,width)
