#!/usr/bin/env python3

""" witrels.py
Witness Relationships v.0.2
🄯 2022 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

import sys
import json
from os import path

import sparql_query

try:
    import defaults
except ImportError:
    raise ImportError("\n[!] defaults module not available.\nAborting...")

try:
    import getdata
except ImportError:
    raise ImportError("\n[!] getdata module not available.\nAborting...")

try:
    from witnesses import Witness
except ImportError:
    raise ImportError("\n[!] witnesses module not available.\nAborting...")

try:
    from xmlcleaners import meta_cleanup, clean_str
except ImportError:
    raise ImportError("\n[!] xmlcleaners module not available.\nAborting...")

try:
    import processcollation
except ImportError:
    raise ImportError("\n[!] processcollation module not available.\nAborting...")

try:
    import createcollation
except ImportError:
    raise ImportError("\n[!] createcollation module not available.\nAborting...")

import argparse
import requests
import json
import re


# ----------------------------------------------------
# ----------------------------------------------------

class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_resource_url(resource_id: str) -> str:
    """ Checks if resource_id is valid and if so
    returns the corresponding URL.
    """
    url = re.sub('https:', 'http:', resource_id)

    response = requests.get(
        url,
        headers={'Accept': 'application/json'},
    )

    if len(response.json()) == 0:
        print(f"{Bcolors.FAIL}error:{Bcolors.ENDC} invalid resource ({resource_id})")
        sys.exit(1)

    return url


def parse_options():
    parser = argparse.ArgumentParser(
        description="Compute coincidence frequencies in witnesses' readings",
        usage="%(prog)s [resource_id]",
    )
    parser.add_argument('resource_id', metavar='resource_id',
                        help='(e.g. <http://scta.info/resource/b1-d1-q13>')
    return parser.parse_args()


# -----------------------------------------------------

def main() -> None:
    """ Main function. """

    args = parse_options()
    resource_id = args.resource_id
    resource_url = get_resource_url(resource_id)

    print(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} Parsing {resource_url}")

    transcriptions = sparql_query.run_query(resource_url)

    print(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {len(transcriptions)} transcriptions found")

    quit()

    # Create a list of xml files from the data dir
    filelist = getdata.get_input_data()

    print(f'Parsing {defaults.witnum} files... ')

    # Creates a lists of Witness objects.
    # E.g. wit[0] is a Witness object whose name is contained in file[0].
    # These witnesses are parsed upon creation.
    witnesslist = [Witness(fname) for fname in filelist]

    getdata.checkwitnesses(witnesslist)

    # "data" is a list which contains, in each entry, a list of tuples.
    # Each tuple is composed of a witness id (e.g. '#M') and a string
    # containing the text of the correspoding <p> element.
    # For example, "data[0]" contains the list corresponding to the first
    # <p> element in all witnesses.
    # And "data[0][0]" contains the tuple (id, text) of the first <p>
    # of the first witness.
    # And "data[0][0][1]" will contain that text.
    # [[["#M", "tertiodecimo..." ], ...], ...]
    data = createcollation.prepare_collation(witnesslist)

    # save "data" as "{prefix}_data.json"
    createcollation.writedatafile(data)

    # create the list of collations
    # structured as: collist[paragraph_num][segment]
    # createcollation(data[, firstline=, lastline=])

    # collist = createcollation.createcollation(data=data, firstline=0, lastline=0)
    collist = createcollation.createcollation(data, firstline=0, lastline=0)

    print("Collation ready.")

    variationlist = processcollation.classify_variations(collist)

    percentlist = processcollation.calculate_percentages(variationlist)

    processcollation.generate_plot(percentlist)

    # processcollation.interpret_results(percentlist)

    print("Finished!")

    return


if __name__ == "__main__":
    main()
