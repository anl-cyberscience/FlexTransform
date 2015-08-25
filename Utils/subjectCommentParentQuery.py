#! /usr/bin/env python3

import sys

import argparse
import rdflib


DEFAULT_QUERY = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://www.anl.gov/cfm/transform.owl#>
SELECT DISTINCT ?subject ?comment ?parent
    WHERE { ?parent rdfs:subClassOf* :SemanticComponent .
         ?subject rdfs:subClassOf ?parent .
        OPTIONAL { ?subject rdfs:comment ?comment . } }
    ORDER BY ?parent'''


def buildAndParseGraph(rdfFile):
    '''Instantiate a graph, parse `rdfFile`, and return graph after
    parsing.

    :param rdfFile: rdf filename to parse
    :type rdfFile: str
    :returns: rdflib.Graph
    '''
    g = rdflib.Graph()
    g.parse(rdfFile)
    return g


def queryGraph(graph, query=DEFAULT_QUERY):
    '''Return the result of `query` on the rdflib.Graph object `graph`.

    Convenience helper function to use DEFAULT_QUERY if no query is
    provided.

    :param graph: graph to query
    :type graph: rdflib.Graph
    :param query: SPARQL query to run on `graph`
    :type query: str
    :returns: rdflib.query.Result
    '''
    return graph.query(query)


def writeSubjectAndCommentToCSV(queryRes, outFile=None):
    '''Write the `subject`, `comment` and `parent` fields of each row in 
    `queryRes` to a CSV file `outFile`.

    If outfile is not supplied, results are written to stdout.  If a row does
    not have a comment, 'None' is printed.
    
    :param queryRes: queryResults to print
    :type queryRes: rdflib.query.Result
    :param outFile: CSV output filename
    :type outFile: string
    '''
    f = open(outFile) if outFile else sys.stdout
    # add a comment at the top of the file describing fields
    f.write('#subject,comment,parent\n')
    for row in queryRes:
        f.write('{0},{1},{2}\n'.format(row.subject, row.comment, row.parent))
    if f is not sys.stdout:
        f.close()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', action='store', required=True,
                        help='RDF input filename')
    parser.add_argument('-o', '--output-file', action='store', required=False,
                        help='CSV output filename. If absent, use stdout.')

    args = parser.parse_args()

    g = buildAndParseGraph(args.input_file)
    q = queryGraph(g)
    writeSubjectAndCommentToCSV(q, args.output_file)
