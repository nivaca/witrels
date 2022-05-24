""" createcollation.py
Part of Witness Relationships v.0.1
🄯 2022 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

from os import path
import json

try:
    import defaults
except ImportError:
    raise ImportError("\n[!] defaults module not available.\nAborting...")

# progress bars
try:
    from tqdm import tqdm
except ImportError:
    raise ImportError("\n[!] tqdm module not available.\nAborting...")

try:
    from collatex import Collation, collate
except ImportError:
    raise ImportError("\n[!] collatex module not available.\nAborting...")

# debug:
# try:
#     from pprint import pprint
# except ImportError:
#     raise ImportError("\n[!] pprint module not available.\nAborting...")


# -------------------------------------------------------------------------------


def prepare_collation(witnesses: list) -> list:
    parnum = len(witnesses[0].paragraphs)
    collation = []
    for p in range(parnum):
        row = []
        for w in witnesses:
            tup = (w.id, w.paragraphs[p])
            row.append(tup)
        collation.append(row)
    return collation


# ----------------------------------------------------

def writedatafile(data: list) -> None:
    fname = defaults.datadir + defaults.prefix + "_data.json"
    with open(fname, "w") as outfile:
        json.dump(data, outfile, indent=2)
    return


# ----------------------------------------------------
def qrecreatecollationfile(fname: str) -> bool:
    ans = input(f"[!] {fname} exists. Recreate? (y/[n]) ").lower()
    if ans == 'y':
        return True
    elif ans == 'n' or ans == '':
        return False


# ----------------------------------------------------

def writecollationfile(fullcollation: list, fname: str) -> None:
    print(f"Writing to file: {fname}...")
    with open(fname, "w") as outfile:
        json.dump(fullcollation, outfile, indent=2)
    return


# ----------------------------------------------------

def readcollationfile(fname: str) -> list:
    print(f"Reading collation file: {fname}...")
    with open(fname, "r") as infile:
        data = json.load(infile)
    return data


# ----------------------------------------------------

def processitem(item: any) -> str:
    if not item:  # if "null" value in the json
        return '---'
    elif len(item) == 1:  # if there is only one string in segment
        return str(item[0]["n"])
    else:  # if there are multiple strings, join them
        subseg = ""
        for ss in item:
            subseg += ss["n"] + " "
        return subseg.strip()


# ----------------------------------------------------

# def createcollation(data: list, firstline: int = 0, lastline: int = 0) -> list:
def createcollation(data: list, firstline: int = 0, lastline: int = 0) -> list:
    """
    Creates a collatex collation for each paragraph in the data list.
    Returns a list of all variation segments (all witnesses)
    for all paragrpahs.
    The optional arguments firstline and lastline contain the first and
    last lines of the data to be processed.
    """

    if lastline == 0:
        lastline = defaults.parnum

    fname = defaults.datadir + defaults.prefix + '_variants.json'

    # Check if "{prefix}_variants.json" file exists
    # (to avoid recreating it).
    # If it does, is asks for confirmation.
    # debug: comment the following
    if path.exists(fname):
        if not qrecreatecollationfile(fname):
            return readcollationfile(fname)

    fullcollation = []

    print("\nCreating collation of variants...")

    # range across the No. of <p> ---------------------------------------------
    for parnum in tqdm(range(firstline, lastline)):
        # create a new, empty Collation object
        mycollation = Collation()

        for witseg in data[parnum]:
            # witseg[0] is the witness' siglum
            # witseg[1] is the contents of a <p>
            # add_plain_witness requires both
            mycollation.add_plain_witness(witseg[0], witseg[1])

        # build a dictionary from the json object
        # resulting from the collation.
        # the dictionary has two items:
        # first, "table", the table of differences;
        # second, "witnesses", the table of sigla of the witnesses
        colldict = json.loads(collate(mycollation, output="json"))

        # store the "table" part of the collation
        # table[0] contains the segments of the first witness, and so on
        table = colldict["table"]

        # get amount of segments in each paragraph
        # (in first witness only, as all are equal in length)
        segnum = len(table[0])

        # in each <p>, range across the No. of segments
        for s in range(segnum):
            # in each segment, range across the No. of witnesses
            variants = [processitem(wit[s]) for wit in table]
            fullcollation.append(variants)

    writecollationfile(fullcollation, fname)

    return fullcollation
