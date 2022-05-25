""" witnesses.py
Part of Witness Relationships v.0.2
🄯 2022 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

import os

try:
    from getdata import get_wit_id, parse_file
except ImportError:
    raise ImportError("\n[!] getdata module not available.\nAborting...")

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("\n[!] BeautifulSoup 4 module not available.\nAborting...")

try:
    import defaults
except ImportError:
    raise ImportError("\n[!] defaults module not available.\nAborting...")


# --------------------------------------------------------------------------


class Witness:
    """ This is the class of witnesses. """

    def __init__(self, name) -> None:
        self.name = name
        self.short_file_name = self.name + ".xml"
        self.file_name = os.path.join(defaults.datadir, ''.join([self.name, ".xml"]))
        self.xml_list = []
        self.xml_ids = []
        self.paragraphs = []
        self.len = 0
        self.id = ''
        self.get_my_id()
        self.parse_me()
        self.xml_prefix = ''
        self.get_my_prefix()

    def get_my_id(self) -> None:
        """ Returns the witness id. """
        self.id = get_wit_id(self.file_name)
        defaults.sigla.append(self.id)

    def parse_me(self) -> None:
        """ Parses the file to obtain XML data. """
        self.xml_list = list(parse_file(self.file_name))
        self.xml_ids = [xid[0] for xid in self.xml_list]
        self.paragraphs = [xid[1] for xid in self.xml_list]
        self.len = len(self.xml_ids)

    def get_my_prefix(self) -> None:
        """ Returns the witness XML prefix. """
        prefix = self.xml_ids[0]
        self.xml_prefix = prefix.split('-')[0]

    def get_par_by_index(self, index):
        """ Returns the contents of a certain paragraph
        depending on its numbered index (0-len). """
        return self.paragraphs[index]

    def get_par_by_xmlid(self, xmlid):
        """ Returns the contents of a certain paragraph
        depending on its xml:id. """
        return self.paragraphs[self.xml_ids.index(xmlid)]

    def __len__(self) -> int:
        """ Returns the number of paragraphs in the witness. """
        return self.len
