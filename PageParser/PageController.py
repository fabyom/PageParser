import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import argparse, jsonpickle, re

from PageParser import PageParser

def save_json(parser, path):
    """
    Write the parser object and its children to JSON.
    :param parser: PAGEParser object.
    :param path: Full path to the target file.
    """
    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', indent=4, ensure_ascii=False)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(jsonpickle.dumps(parser.document, unpicklable=False))
    json_clean_up(path)



def json_clean_up(jsonfile):
    '''
    hacky lösung
    JSON Datei enthält am ende jedes dokumentes Einträge mit den wert 'null'
    TO-DO: nachschauen warum überhaupt null geprinted wird
    :param jsonfile:
    :return:
    '''
    #TODO!!!
    with open(jsonfile,encoding='utf-8') as file:
            for line in file:
                if(re.match(r'.+null.+\n',line)):
                    re.sub(r'.+\n','',line)



# Call: ./PageParser.py page-path document-name json-path
def handle_args():
    """
    Parse command line arguments.

    :return: Directory containing PAGE XML files, name of the document, target path for JSON output.
    """
    parser = argparse.ArgumentParser(description="Convert a set of PAGE XML documents into a JSON file containing the "
                                                 "coordinates and content of each analysed text line.")

    parser.add_argument("page-path", nargs=1, type=str, metavar="PAGE-PATH",
                        help="Path to directory containing the PAGE XML files to parse. Please use an absolute path.")
    parser.add_argument("document-name", nargs=1, type=str, metavar="DOC-NAME",
                        help="Name of the document.")
    parser.add_argument("json-path", nargs=1, type=str, metavar="JSON-PATH",
                        help="Path to save the JSON output to. Please use an absolute path.")

    args = parser.parse_args()
    return args


def main():
    # Variables for testing in IDE
    document_id = "Ms-114"
    page_path = "./Ms-114/page"
    json_path = "./Ms-114/test_output.json"

    # Actual arguments when calling from command line
    #page_path, document_id, json_path = handle_args()

    #parser = PageParser()
    #parser = PageParser('./','./json')
    parser = PageParser(page_path, document_id)
    parser.read_files()
    save_json(parser, json_path)


if __name__ == "__main__":
    main()
