""" defaults.py
Part of Witness Relationships v.0.1
🄯 2022 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

# +++++++++++++++++++ GLOBAL VARIABLES +++++++++++++++++++++

datafilename: str
defaultdatadir: str
tempdatadir: str
resultfile: str
plotresults: bool

sigla = []    # dynamically assigned later in witnesses.py
datadir: str   # dynamically assigned later in set_globals_from_datafile()
prefix: str    # dynamically assigned later in set_globals_from_datafile()
witnum: int    # dynamically assigned later in set_globals_from_datafile()
parnum: int    # dynamically assigned later in checkwitnesses()
