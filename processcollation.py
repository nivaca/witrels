""" processcollation.py
Part of Witness Relationships v.0.1
🄯 2022 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

import itertools
import operator

# try:
#     import pandas
# except ImportError:
#     raise ImportError("\n[!] pandas module not available.\nAborting...")

try:
    import defaults
except ImportError:
    raise ImportError("\n[!] defaults module not available.\nAborting...")

try:
    # noinspection PyUnresolvedReferences
    import plotly.graph_objects as go
except ImportError:
    print("[!] Plotly module not available. Outputing plain text...")
    defaults.plotresults = False

try:
    import kaleido
except ImportError:
    print("[!] kaleido module not available. Outputing plain text...")
    defaults.plotresults = False


# ------------------------------------------------------------------------------
def generate_permutations() -> list:
    """
    Creates a list of strings containing all permutations:
    ["AAAA", "AAAB", ...]
    len = (witnum ** 2)
    """
    witnum = defaults.witnum
    x = []
    for i in range(witnum):
        x.append(chr(65 + i))
    out = [list(p) for p in itertools.product(x, repeat=witnum)]
    return out


# -----------------------------------------------------------------------------------
def classify_variant_set(inputlist) -> int:
    """
    Given a single inputlist of variations (segments), the function
    compares them and assigns a string (e.g. 'ABBD') to the comparison.
    Then it searches that string in the variationlist and returns
    its index integer.
    ----
    TODO: generalise for an arbitrary number of witnesses.
    Currently only works for four. (4 ** 2) == 256
    """
    out = ['A']
    if inputlist[0] == inputlist[1]:
        out.append('A')
    else:
        out.append('B')

    if inputlist[0] == inputlist[2]:
        out.append('A')
    elif inputlist[1] == inputlist[2]:
        out.append('B')
    else:
        out.append('C')

    if inputlist[0] == inputlist[3]:
        out.append('A')
    elif inputlist[1] == inputlist[3]:
        out.append('B')
    elif inputlist[2] == inputlist[3]:
        out.append('C')
    else:
        out.append('D')

    # returns the index of the variation in the variation list
    permutations = generate_permutations()
    return permutations.index(out)


# -----------------------------------------------------------------------------
def classify_variations(segmentlist: list) -> list:
    """For each (non empty) segment, classify the kind of
    variation according the permutation list.
    Return a list of integers correponding to
    the index of the permutation list.
    """
    freqlist = []
    for segment in segmentlist:
        value = classify_variant_set(segment)
        # prune "0" freqs
        if value == 0:
            continue
        freqlist.append(value)
    return freqlist


# -----------------------------------------------------------------------------

def calculate_percentages(variationlist: list) -> list:
    varnum = len(variationlist)
    percentlist = []
    templist = []
    permutations = generate_permutations()

    # count the number of occurances of item on a list
    def countocc(lst: list, x: int) -> int:
        accurances = 0
        for ele in lst:
            if ele == x:
                accurances += 1
        return accurances

    for value in variationlist:
        count = countocc(variationlist, value)
        percentage = round(count / varnum * 100, 2)
        if value not in templist:  # ensure no repetitions
            outlist = ["".join(permutations[value]), percentage]
            percentlist.append(outlist)
        templist.append(value)

    # sort them inversely according to percentage
    percentlist = sorted(percentlist, key=operator.itemgetter(1), reverse=True)

    return percentlist


# -----------------------------------------------------------------------------


# def generate_plot(percentlist: list) -> None:
#     percentages = [value[1] for value in percentlist]
#     varnames = [value[0] for value in percentlist]
#     fig, ax = plt.subplots()
#     ax.pie(percentages, labels=varnames, autopct='%1.1f%%', shadow=False, startangle=90)
#     ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#     # plt.show()
#     plt.savefig(globals.datadir + globals.prefix + ".pdf")
#     plt.close()
#     return


# -----------------------------------------------------------------------------
def generate_plot(percentlist: list) -> None:
    percentages = [value[1] for value in percentlist]
    varnames = [value[0] for value in percentlist]

    for item in percentlist:
        line = f"{item[0]}: {str(item[1])}%"
        print(line)
        fname = defaults.datadir + defaults.resultfile
        with open(fname, "w") as file:
            file.write(line)

    if defaults.plotresults:
        trace = go.Pie(labels=varnames,
                       values=percentages,
                       hoverinfo='label+percent+name')

        layout = go.Layout(height=600,
                           width=600,
                           autosize=False,
                           title=f'Variants for {defaults.prefix}')
        fig = go.Figure(data=trace, layout=layout)
        fig.show()

    return


# # -----------------------------------------------------------------------------
# def interpret_results(percentlist: list) -> None:
#     percentages = [value[1] for value in percentlist]
#     varnames = [value[0] for value in percentlist]
#
#     sigla = defaults.sigla
#     witnum = defaults.witnum  # 4
#
#     # only interpret the 5 higher values
#     for item in percentlist[:5]:
#         for l1 in range(witnum):
#             for l2 in range(witnum):
#                 if l1 == l2:
#
#
#
#     return


# -----------------------------------------------------------------------------


