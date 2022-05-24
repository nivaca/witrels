""" getdata.py
Part of Witness Relationships v.0.1
🄯 2022 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

import os
import sys
import urllib
import requests
from os import path, makedirs
import hashlib
import shutil
import re

try:
    from tqdm import tqdm
except ImportError:
    raise ImportError("\n[!] tqdm module not available.\nAborting...")

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("\n[!] bs4 module not available.\nAborting...")

try:
    from xmlcleaners import meta_cleanup, clean_str
except ImportError:
    raise ImportError("\n[!] xmlcleaners module not available.\nAborting...")

try:
    import defaults
except ImportError:
    raise ImportError("\n[!] defaults module not available.\nAborting...")


# =================================================================================
def clean_urllist(urllist: list) -> list:
    # ignore comment lines (viz. containing "#")
    urllist = [entry for entry in urllist if not re.match(r"#", entry)]
    # strip whitespace in entries
    urllist = [entry.strip() for entry in urllist]
    # prune empty entries
    urllist = [entry for entry in urllist if not entry == '']
    return urllist


# ----------------------------------------------------
def get_input_data() -> list:
    # if defaultdatadir exists, use it as datadir
    if path.exists(defaults.defaultdatadir):
        defaults.datadir = defaults.defaultdatadir
        print(f"Using {defaults.datadir} as default data directory...")
        return get_files()

    # if not, create a new one based on the prefix
    if not path.exists(defaults.datadir):
        makedirs(defaults.datadir, exist_ok=True)
        print(f"Created {defaults.datadir} to use as data directory...")

    # check if data.lst file exists
    if not path.exists(defaults.datafilename):
        print(f"[!] Error! {defaults.datafilename} doesn't exist. Aborting...")
    else:
        # parse file and download xml files
        with open(defaults.datafilename, "r") as datafile:
            urllist = clean_urllist(datafile.readlines())
            download_xml_files(urllist)

    return get_files()


# ----------------------------------------------------
def get_file_hash(fname: str) -> str:
    with open(fname, "rb") as f:
        filehash = hashlib.sha256()
        while chunk := f.read(8192):
            filehash.update(chunk)
    return filehash.hexdigest()


# ----------------------------------------------------
def validate_url(url: str) -> bool:
    if requests.get(url).status_code == 200:
        return True
    else:
        return False


# ----------------------------------------------------
def download_xml_files(urllist: list) -> None:
    """ Given an input urllist, download each of the URLs
    and calculate its sha256sum. If the file already exists in the datadir,
    calculate and compare its sha256sum with the new file.
    If the sha256sum is identical, skip.  Otherwise,
    replace the file in the datadir to ensure working
    with the latest version.
    """
    print("Downloading data files...")
    # create datadir if it doesn't exist
    for url in urllist:
        if url == '':
            continue
        if not validate_url(url):
            print(f"[!] Error! {url} isn't available. Aborting...")
            sys.exit(1)
        fname = defaults.datadir + os.path.basename(url)
        fname = fname.strip()
        tempfname = defaults.tempdatadir + os.path.basename(url)
        tempfname = tempfname.strip()
        existingfilehash = ""
        if path.exists(fname):
            existingfilehash = get_file_hash(fname)

        print(f"  Downloading {os.path.basename(fname)}...", end=" ")
        with urllib.request.urlopen(url) as f:
            data = f.read().decode('utf-8')
            # create tempdatadir
            if not path.exists(defaults.tempdatadir):
                os.makedirs(defaults.tempdatadir, exist_ok=True)
            with open(tempfname, "w") as temporaryfile:
                temporaryfile.writelines(data)
            temporaryfilehash = get_file_hash(tempfname)
            if existingfilehash == temporaryfilehash:
                print("File already exists and is identical to upstream. Skipping...")
            else:
                shutil.move(tempfname, fname)
                print("OK!")
            # delete tempdatadir
            try:
                shutil.rmtree(defaults.tempdatadir)
            except OSError as e:
                print(f"[!] Error: {defaults.tempdatadir} : {e.strerror}")
    return


# ----------------------------------------------------
def get_files() -> list:
    """ Returns the list of names of the xml files
    in the data directory. """
    files = os.listdir(defaults.datadir + '.')
    filelist = []

    for file in files:
        fname = os.path.splitext(file)[0]
        fext = os.path.splitext(file)[1]
        # check whether fname has required extension
        if fext == '.xml':
            filelist += [fname]

    filelist = sorted(filelist)

    if len(filelist) == 0:
        print("[!] Error: No XML files to process. Aborting...")
        sys.exit(1)

    return filelist


# ---------------------------------------------------------


def get_wit_id(file: str) -> str:
    """ Returns the witness id. """
    soup = BeautifulSoup(open(file), "lxml-xml")
    witdesc = soup.find('witness')
    wit = '#' + witdesc["xml:id"]
    return wit


# ---------------------------------------------------------

def parse_file(fname: str) -> list:
    """ Parses a given TEI-XML file.
    Returns a list of couples, like so:
    [('b1d3qun-cdtvet', 'Circa ...'), etc.]
    """

    print(f'  Parsing {fname}... ', end='')

    soup = BeautifulSoup(open(fname), "lxml-xml")
    soup = meta_cleanup(soup)

    # Checks whether tag has 'xml:id'
    def p_with_id(tag):
        return tag.name == 'p' and \
               tag.has_attr('xml:id') and \
               not tag.has_attr('ana')  # needed to escape some headings

    paragraphs = soup.find_all(p_with_id)

    p_tags = []

    for parag in paragraphs:
        buf = ''
        for pa in parag:
            pa = str(pa)
            buf += str(pa)
        buf = clean_str(buf)
        p_tags.append(buf)

    # Provides a list of all @xml:ids containing "b1d3qun":
    xml_ids = [p["xml:id"] for p in paragraphs]

    print("OK")

    # Returns a list of tuples of the parsed XML, like so:
    # [('b1d3qun-cdtvet', 'Circa ...'), etc.]
    return list(zip(xml_ids, p_tags))


# ---------------------------------------------------------


def checkwitnesses(witnesses: list) -> None:
    """ Checks that all files have the same number of <p>,
        and if their prefixes coincide.
    """
    witnum = defaults.witnum
    print(f'Checking {witnum} witnesses... ', end='')

    for i in range(1, witnum):
        if len(witnesses[0]) != len(witnesses[i]):
            print('\nError! Files do not have the same number of <p xml:id="..."> tags!')
            print(f"{witnesses[0].name}: {len(witnesses[0])}")
            print(f"{witnesses[i].name}: {len(witnesses[i])}")
            print('Aborting...')
            sys.exit(1)
        elif witnesses[0].xml_prefix != witnesses[i].xml_prefix:
            print('\nError! Files do not have the same XML prefix!')
            print('Aborting...')
            sys.exit(1)
    print('OK!')

    defaults.parnum = len(witnesses[0])  # set globals.parnum
    print(f"Number of total paragraphs: {defaults.parnum}")
    return
