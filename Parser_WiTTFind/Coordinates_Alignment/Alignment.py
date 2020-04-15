from collections import  OrderedDict
from Parser_WiTTFind.Coordinates_Alignment.Aligned_Result import *
import logging

from pylev3 import Levenshtein

def zero_list_builder(n): # Eine Methode die Null listen der Länge n erzeugt
    '''The method creates a list object with the length of n
    :param n length of the list to build
    '''
    list_of_zeros = [0]*n
    return list_of_zeros

def remove_multiple_indixes(max_similarity_index_dict):
    '''
    # Entfernt aus den Ähnlichkeitslisten einen Eintrag wenn dies in einer anderen Ähnlichkeitsliste der Einzige ist
    :param max_similarity_index_dict:
    :return:
    '''
    for max_similarity_index_list in max_similarity_index_dict.values():
        if len(max_similarity_index_list) > 1:
            # print("Before: ", max_similarity_index_list)
            for second_max_similarity_index_list in max_similarity_index_dict.values():
                if len(second_max_similarity_index_list) == 1:
                    if second_max_similarity_index_list[0] in max_similarity_index_list and len(max_similarity_index_list) > 1:
                        max_similarity_index_list.remove(second_max_similarity_index_list[0])
                        # print("REMOVED")
            # print("After: ", max_similarity_index_list)
    return max_similarity_index_dict

def allign_lines(edition_lines, ocr_lines, page_id):
    '''
    The method compares the given edition_lines list with the ocr_lines_list and returns an aligned page object
    :param edition_lines: list of edition lines
    :param ocr_lines: list of ocr lines
    :param page_id: Seiten ID
    :return: aligned page object
    '''
    alligned_page = Aligned_Page()
    alligned_page.id=page_id # Seite mit Dokumentname im Format Ts-XXX,X
    max_similarity_index_dict = OrderedDict() # Speichert unter dem Schlüssel edition_line die maximale Ähnlichkeitsindexliste
    max_ocr_line_index = len(ocr_lines)
    for edition_line in edition_lines: # Die Schleife prüft auf jede OCR-Zeile die Ähnlichkeit zur Editionszeile.
        compare_list=zero_list_builder(len(ocr_lines)) # Eine Null liste die einen Ähnlichkeitswert repräsentiert!
        splitted_edition_line = edition_line.text.split() # Erzeugt eine Liste mit den Einzelwörtern der Editionszeile
        counter = 0 # Zählvaribale zum zählen der OCR-Zeile
        for ocr_line in ocr_lines: # Durchläuft die OCR Zeilen
            splitted_ocr_line=ocr_line.text.split()
            if len(splitted_ocr_line) == len(splitted_edition_line): # Überprüft ob die Zahl der Wörter in der Editions- und der OCR-Zeile übereinstimmen
                compare_list[counter] += 1
            for word in splitted_edition_line: # Überprüft jedes Wort aus der Edition ob es in der gesplitteten OCR Zeile enthalten ist
                if any(word in s for s in splitted_ocr_line):
                    compare_list[counter] += 1 # Aufrechnen von Wertungspunkten
            # Hier ist der Ansatzpunkt weiter zu verbessern
            #Levenshtein.classic(edition_line.text, ocr_line.text)
            counter += 1
        max_similarity=max(compare_list)
        max_similarity_index_list = [ i for i, j in enumerate(compare_list) if j == max_similarity] # Durchläuft die compare-List und gibt eine Liste zurück mit den Indizes der ähnlichsten OCR Zeilen
        max_similarity_index_dict[edition_line] = max_similarity_index_list
        logging.debug("Ähnlichkeitsliste: ", max_similarity_index_list)
    # The method removes multiple indices
    remove_multiple_indixes(max_similarity_index_dict) # Entfernen doppelter Indizes
    remove_multiple_indixes(max_similarity_index_dict) # Entfernen doppelter Indizes
    check_if_lines_are_in_order(max_similarity_index_dict, max_ocr_line_index)
    # This loop links editions lines an OCR lines together in an alligned_page object
    logging.debug("Fertige Ähnlichkeitsliste für Seite "+str(page_id))
    for edition_line in edition_lines:
        logging.debug("Ähnlichkeitsliste: ", max_similarity_index_dict[edition_line][0])
        if max_similarity_index_dict[edition_line][0] == -1:
            #print ("Die Zeile wurde nicht erkannt!")
            alligned_line = Alligned_Line(edition_line, None)
        else:
            alligned_line=Alligned_Line(edition_line, ocr_lines[max_similarity_index_dict[edition_line][0]])
        alligned_page.aligned_lines.append(alligned_line)
    return alligned_page


def check_if_lines_are_in_order(max_similarity_index_dict, max_ocr_line_index):
    #max_similarity_index_list_to compare
    # Kopiert die im dict gespeicherten Index-Listen in eine neue Liste
    index_index_list_generated_from_dict = []
    for max_index_list in max_similarity_index_dict.values():
        index_index_list_generated_from_dict.append(max_index_list)
    counter = 0
    vorher = -1
    index  = -1
    nachher = -1
    last_line = False

    for key, index_list in max_similarity_index_dict.items(): # Das Nachschlagewerk wird sowohl mit Schlüssel als auch Wert durchlaufen, es kann immer nur der aktuelle Schlüssel geändert werden
        index = index_list[0]
        if counter > 0:
            vorher = index_index_list_generated_from_dict[counter - 1][0] # Der Index in der Indexliste vorher
        if len(index_index_list_generated_from_dict)-1 > counter:
            nachher = index_index_list_generated_from_dict[counter + 1][0] # Der Index in der Indexliste nachher
        else:
            #print("Die Letzte Zeile Wurde erreicht")
            nachher = index_index_list_generated_from_dict [counter][0]
            last_line = True
        if index == vorher+1 or index == nachher-1:
            #print("Die Zeile ist in Reihenfolge")
            if len(index_list) > 1:
                index_list = [index_list[0]]
        # Hier noch einen Block für gleiche Werte einfügen
        elif (index == vorher or index == nachher) and not last_line:
            #print("Eine Zeile wurde doppelt erkannt")
            if index == vorher:
             #print("Die Zeile vorher wurde doppelt erkannt")
             if check_if_index_is_not_in_use_anywhere_else(index+1, index_index_list_generated_from_dict, counter):
                    index_list = [index+1]
            elif index == nachher:
                #print("Die Zeile nachher wurde doppelt erkannt")
                if check_if_index_is_not_in_use_anywhere_else(index-1, index_index_list_generated_from_dict, counter):
                    index_list =  [index-1]
        else:
            #print("Die Zeile bricht aus der Reihe aus")
            schwelle = 2
            hohe_schwelle = 5
            #   Der Index ist viel zu groß                                 Der Index ist viel zu klein
            if (abs(index-vorher)>hohe_schwelle) or (abs(index-vorher) > schwelle and abs(index-nachher) > schwelle) or (last_line and (vorher-index>schwelle)): # Falls der Index nach oben und unten um mehr als den Betrag 2 abweicht, andernfalls tue nichts
                #print("Ich will korrigieren", vorher+1)
                if vorher+1 >= max_ocr_line_index:
                    index_list = [-1]
                elif  check_if_index_is_not_in_use_anywhere_else(vorher+1, index_index_list_generated_from_dict, counter):
                    index_list = [vorher+1]
                elif check_if_index_is_not_in_use_anywhere_else(nachher-1, index_index_list_generated_from_dict, counter):
                    index_list = [nachher-1]
                else:
                    #print("Setze den Index auf -1") # Schalte diese Zeile aus!
                    index_list = [-1]
        index_index_list_generated_from_dict[counter] = index_list
        max_similarity_index_dict[key] = index_list
        vorher = -1
        nachher = -1
        counter += 1
    # print("Neue Indexliste: ", index_index_list_generated_from_dict)
    # print("-----------------------------------------------------------------------------------------------------------")
    # print("-----------------------------------------------------------------------------------------------------------")
    # print("-----------------------------------------------------------------------------------------------------------")
    last_line = False

# def check_if_index_exists_already_in_single_use(index_to_check, index_list_list):
#     for index_list in index_list_list:
#         for index in index_list:
#             if len(index_list) == 1 and index != index_to_check:
#                 return True
#     return False
#
# def check_if_index_exists_already_in_use(index_to_check, index_list_list):
#     for index_list in index_list_list:
#         for index in index_list:
#             if index != index_to_check:
#                 return True
#     return False

def check_if_index_is_not_in_use (index_to_check, index_list_list):
    for index_list in index_list_list:
        for index_to_compare in index_list:
            if index_to_compare == index_to_check:
                return False
    return True

def check_if_index_is_not_in_use_anywhere_else (index_to_check, index_list_list, affected_counter):
    counter = 0
    for index_list in index_list_list:
        if counter == affected_counter:
            continue
        for index_to_compare in index_list:
            if index_to_compare == index_to_check:
                return False
        counter += 1
    return True


