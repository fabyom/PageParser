import json, os
from PIL import Image, ImageDraw

class Aligned_Document:
    '''
    Class to represent an aligned document
    '''
    def __init__(self):
        self.aligned_pages = None
        self.id = None

    def save_json(self, filepath):
        """
        Saves a JSON file describing the paragraphs; adheres to the format output by Roman Capsamun's code
        :param filepath: Output file
        """
        with open(filepath, 'w') as f:
            json.dump(self._get_root_ocr_dict(), f, indent=4, ensure_ascii=False)

    def _get_root_ocr_dict(self):
        root_dict = {'ocr': []}
        for i, page in enumerate(self.aligned_pages):
            root_dict['ocr'] += page._get_block_dicts_for_typoscripts()
        return root_dict


class Aligned_Page:
    '''
    Class to represent an aligned Page
    '''
    def __init__(self):
        self.id = '' # Edition Page id, name parsed from edition
        self.aligned_lines=[]
        self.aligned_blocks = []

        # Pointer to the corresponding ocr and edition pages
        self.coresponding_ocr_page=None
        self.coresponding_edition_page=None


    def set_coreesponding_ocr_page(self, coresponding_ocr_page):
        if coresponding_ocr_page == None:
            return False
        self.coresponding_ocr_page=coresponding_ocr_page
        return True

    def set_coresponding_edition_page(self, coresponding_edition_page):
        if coresponding_edition_page == None:
            return False
        self.coresponding_edition_page = coresponding_edition_page
        return True

    def __str__(self):
        return self.id

    def print_aligned_lines(self):
        for line in self.aligned_lines:
            print(line)

    def create_blocks_from_lines(self):
        '''
        The method creates html block text for the json-export object
        :return:
        '''
        recent_block =None
        paragraphes_on_page = 0
        for aligned_line in self.aligned_lines:
            if (recent_block == None) or (aligned_line.edition_line.block != recent_block.coresponding_edition_block):
                recent_block = Alligned_Block(aligned_line.edition_line.block)
                self.aligned_blocks.append(recent_block)
            recent_block.aligned_lines.append(aligned_line)
            if recent_block.text == None:
                recent_block.text=aligned_line.edition_line.text
            else:
                recent_block.text = recent_block.text + "<br>"+ aligned_line.edition_line.text
        for aligned_block in self.aligned_blocks:
            aligned_block.generate_coordinates()

    def _get_block_dicts_for_typoscripts(self):
        '''
        The methode generates block dicts for manuscripts
        :param conf:
        :return: A list containing the exiting block dicts
        '''
        return_list = []

        for i, block in enumerate(self.aligned_blocks):
            block_dict = {
                'siglum': block.coresponding_edition_block._get_siglum_for_page(self.id),# Page id
                'page': self.id,
                'text': block.text,
                'origin_recto_x': 0,
            }
            if block.coordinates!=None:
                coordinates = block.coordinates
            else:
                coordinates = [1000, 1000, 1000, 1000]
                print("ACHTUNG!:  Nur Standart Koordinaten gesetzt! (ALIGNED_Result)")
            left = coordinates[0] / self.coresponding_ocr_page.page_width
            top = coordinates[1] / self.coresponding_ocr_page.page_height
            block_height = coordinates[3] - coordinates[1]
            block_width = coordinates[2] - coordinates[0]
            width = block_width / self.coresponding_ocr_page.page_width
            height = block_height / self.coresponding_ocr_page.page_height
            coordinates_dict = {
                'left': float('{0:.2f}'.format(left)),
                'top': float('{0:.2f}'.format(top)),
                'width': float('{0:.2f}'.format(width)),
                'height': float('{0:.2f}'.format(height)),
            }
            block_dict['coordinates'] = coordinates_dict
            return_list.append(block_dict)
        return return_list

    def show_lines_in_comparison(self):
        return_string="Zeilen auf Seite "+str(self.id)+"\n"
        for aligned_line in self.aligned_lines:
            return_string=return_string+str(aligned_line)+"\n"
        return return_string


class Alligned_Block:
    '''
    Class to represent an aligned Block
    '''
    def __init__(self, coresponding_edition_block):
        self.aligned_lines = []
        self.coresponding_edition_block = coresponding_edition_block
        self.text = None
        self.coordinates = None

    def __str__(self):
        return self.coresponding_edition_block

    def generate_coordinates(self):
        '''
        Erzeugt Koordinaten für den Block aus den Zeileninformationen im Format x0 y0 x1 y1
        :return:
        '''
        for aligned_line in self.aligned_lines:
            if aligned_line.ocr_line == None:
                continue
            else:
                ocr_line = aligned_line.ocr_line
                if self.coordinates == None:
                    self.coordinates = ocr_line.coordinates
                    continue
                # x0
                #print(ocr_line.coordinates)
                if self.coordinates[0] > ocr_line.coordinates[0]:
                    self.coordinates[0] = ocr_line.coordinates[0]
                if self.coordinates[1] > ocr_line.coordinates[1]:
                    self.coordinates[1] = ocr_line.coordinates[1]
                if self.coordinates[2] < ocr_line.coordinates[2]:
                    self.coordinates[2] = ocr_line.coordinates[2]
                    #print(ocr_line.coordinates)
                if self.coordinates[3] < ocr_line.coordinates[3]:
                    self.coordinates[3] = ocr_line.coordinates[3]
        self.resize_calculated_coordinates()

    def resize_calculated_coordinates(self, resize_factor=1.005):
        '''
        Resizes the calculated coordinates
        :param resize_factor: factor in percent
        :return:
        '''
        counter=0
        if self.coordinates != None:
            for coordinate in self.coordinates:
                if counter == 0 or counter == 1:
                    alt = self.coordinates[counter]
                    neu = self.coordinates[counter]*resize_factor
                    differenz = neu -alt
                    self.coordinates[counter] = alt - differenz
                else:
                    self.coordinates[counter]=self.coordinates[counter]*resize_factor
                counter += 1
        else:
            print("Achtung!!! Keine Koordinaten gefunden!!!", self.coresponding_edition_block.id)

class Alligned_Line:
    '''
    Class to represent an aligned line
    '''
    def __init__(self):
        self.edition_line=None
        self.ocr_line=None

    def __init__(self, edition_line, ocr_line):
        self.edition_line=edition_line
        self.ocr_line=ocr_line

    def __str__(self):
        if self.edition_line is not None and self.ocr_line is not None:
            print_string="Editionszeile: "+self.edition_line.text+", \t\t\t\t OCR-Zeile: "+self.ocr_line.text
        else:
            print_string="Zeilen wurden noch nicht gesetzt!"
        return print_string