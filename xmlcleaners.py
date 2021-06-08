""" xmlcleaners.py
Part of Witness Relationships v.0.1
🄯 2021 Nicolas Vaughan
n.vaughan@uniandes.edu.co
Universidad de los Andes, Colombia
Runs on Python 3.8+ """

try:
    from bs4 import BeautifulSoup, Comment
except ImportError:
    raise ImportError("\n[!] BeautifulSoup 4 module not available.\nAborting...")

import re

# ------------------------------------------------------------------------------


def clean_str(thetext: str) -> str:
    thetext = re.sub(r"¶", "", thetext)
    thetext = re.sub(r"\n", " ", thetext)
    thetext = re.sub(r"[.,:;]", " ", thetext)
    thetext = re.sub(r"\t{1,8}", " ", thetext)
    thetext = re.sub(r"[ ]{2,8}", " ", thetext)
    thetext = re.sub(r"[ ]{2,8}", " ", thetext)
    thetext = thetext.lower()
    thetext = thetext.strip()
    # thetext = re.sub("\n", " ", thetext)
    return thetext


# ------------------------------------------------------------------------------
def fix_empty_p_tags(insoup: BeautifulSoup) -> BeautifulSoup:
    """ Take care of empty <p> elements. """
    for match in insoup.find_all("p"):
        if len(match.get_text(strip=True)) == 0:
            match.string = "---"
    return insoup


# ------------------------------------------------------------------------------
def unwrap_tags(insoup: BeautifulSoup) -> BeautifulSoup:
    """ Unwraps selected tags leaving their contents. """
    wrapped_tags = ['add',
                    'c',
                    'cb',
                    'choice',
                    'cit',
                    'corr',
                    'g',
                    'hi',
                    'lb',
                    'mentioned',
                    'name',
                    'pb',
                    'pc',
                    'quote',
                    'ref',
                    'reg',
                    'seg',
                    'sic',
                    'subst',
                    'title',
                    'unclear', ]
    #               'p', 'head', 'div', 'body', 'TEI', 'text'
    for tag in wrapped_tags:
        for match in insoup.find_all(tag):
            match.unwrap()
    return insoup


# ------------------------------------------------------------------------------
def decompose_tags(insoup: BeautifulSoup) -> BeautifulSoup:
    """ Completely deletes selected tags and their contents. """
    invalid_tags = ['abbr',
                    'bibl',
                    'del',
                    'gap',
                    'note',
                    'orig',
                    'space',
                    'supplied', ]
    for tag in invalid_tags:
        for match in insoup.find_all(tag):
            match.decompose()
    return insoup


# ------------------------------------------------------------------------------
def clean_comments(insoup: BeautifulSoup) -> BeautifulSoup:
    """ Removes all comments from the soup. """
    comments = insoup.find_all(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    return insoup


# ------------------------------------------------------------------------------
def meta_cleanup(insoup: BeautifulSoup) -> BeautifulSoup:
    """ Performs all defined cleanups. """
    cleaners = [
                fix_empty_p_tags,
                unwrap_tags,
                decompose_tags,
                clean_comments,
                ]
    for cleaner in cleaners:
        cleaner(insoup)
    return insoup
