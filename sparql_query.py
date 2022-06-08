import re
from SPARQLWrapper import SPARQLWrapper, JSON


def run_query(resource: str) -> list:
    """ Runs a sparql query and returns the results as a list."""
    # resource = "http://scta.info/resource/wodehamordinatio"
    # resource = "http://scta.info/resource/b1-d1-q13"
    # resource = "http://scta.info/resource/lectio1"
    resource = """
        SELECT ?manifestations ?transcriptions ?xmlfiles 
        WHERE {
        <%s> <http://scta.info/property/hasManifestation> ?manifestations .
        ?manifestations <http://scta.info/property/hasTranscription> ?transcriptions . 
        ?transcriptions <http://scta.info/property/hasXML> ?xmlfiles .
        }
        """ % resource

    sparql = SPARQLWrapper("https://sparql-docker.scta.info/ds/query")
    sparql.setQuery(resource)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    num_manif = len(results["results"]["bindings"])

    transcriptions = []

    for result in results["results"]["bindings"]:
        if 'critical' not in result["transcriptions"]["value"]:
            URL = result["xmlfiles"]["value"]
            pattern = r"([^/]+)(?=/transcription)"
            slug = re.search(pattern, URL).group(1)
            transcriptions.append([slug, URL])

    return transcriptions
