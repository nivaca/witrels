#!/usr/bin/env python3

""" witnessrelations.py
Witness Relationships v.0.1
🄯 2021 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

import sys
import json
from os import path

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


# ----------------------------------------------------
# ----------------------------------------------------

def read_config_file() -> None:
    configfile = "config.json"
    if not path.exists(configfile):
        print(f"[!] Error! Missing {configfile}. Aborting...")
        sys.exit(1)

    with open(configfile, 'r') as file:
        conf = json.load(file)
        # set globals in defaults.py
        defaults.datafilename = conf["datafilename"]
        defaults.defaultdatadir = conf["defaultdatadir"]
        defaults.tempdatadir = conf["tempdatadir"]
        defaults.resultfile = conf["resultfile"]
        defaults.plotresults = conf["plotresults"]

    datafilename = defaults.datafilename
    if not path.exists(datafilename):
        print(f"[!] Error: {datafilename} doesn't exist! Aborting...")
        sys.exit(1)
    else:
        with open(datafilename, "r") as datafile:
            entries = getdata.clean_urllist(datafile.readlines())
            defaults.witnum = len(entries)  # set globals.witnum
            entry = entries[0].split('/')
            defaults.prefix = entry[-2]  # set globals.prefix
            defaults.datadir = "data_" + defaults.prefix + "/"  # set globals.datadir
            defaults.sigla = sorted(defaults.sigla)  # set globals.sigla
    return


# -----------------------------------------------------
def main() -> None:
    """ Main function. """
    # read configfile and set global variables in defaults.py
    read_config_file()

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
