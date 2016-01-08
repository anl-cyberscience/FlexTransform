#!/usr/local/bin/python3
# encoding: utf-8
'''
Utils.addSchemaConfigToTBOX -- shortdesc

Utils.addSchemaConfigToTBOX is a simple command line interface to parse a JSON configuration file for flexible transform and
populate an ontology file with the definitions according to the config file.

It defines:

@author:     Chris Strasburg

@copyright:  2015 Ames Laboratory, Department of Energy

@contact:    cstras@ameslab.gov
@deffield    updated: 2015-05-17
'''

import sys
import os
import json
import rdflib
import rdflib.namespace
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2015-05-17'
__updated__ = '2015-05-17'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class SchemaOntologyProducer(object):
    supportsSemanticComponentRelation = rdflib.URIRef(u'{}'.format("http://www.anl.gov/cfm/transform.owl#supportsSemanticComponent"))
    requiresSemanticComponentRelation = rdflib.URIRef(u'{}'.format("http://www.anl.gov/cfm/transform.owl#requiresSemanticComponent"))

    ''' This class produces an ontology given a JSON schema definition file. '''
    def __init__(self, jsonConfigFile, tboxRDFLibGraph, tboxIRI, schemaIRI):
        '''
        jsonConfigFile - a json object from the json module, e.g. by using json.load(<fileDescriptor>)
        tboxRDFLibGraph - An RDFLibGraph object of the TBOX
        tboxIRI - The IRI of the ontology we are loading from the tbox File
        schemaIRI - The IRI of the schema we are working with; if not present in the graph, it will be added
        '''
        self.jsonConfig = jsonConfigFile
        self.graph = tboxRDFLibGraph
        self.namespace = rdflib.Namespace(tboxIRI)
        self.graph.bind("cfmft",self.namespace)
        self.graph.bind("rdf",rdflib.namespace.RDF)
        self.graph.bind("rdfs",rdflib.namespace.RDFS)
        self.initNS = {"cfmft": self.namespace,
                       "rdf": rdflib.namespace.RDF,
                       "rdfs": rdflib.namespace.RDFS}
        self.newConcepts = 0
        self.newDescriptions = 0

        self.schemaIRI = rdflib.URIRef(u'{}'.format(schemaIRI))
        if (self.schemaIRI,None,None) not in self.graph:
            self.graph.add((self.schemaIRI, rdflib.namespace.RDF.type, rdflib.namespace.RDFS.Class))
            self.graph.add((self.schemaIRI, rdflib.namespace.RDFS.subClassOf, self.namespace.DocumentSchema))
            logging.info("[W]: Document schema {} added new.".format(self.schemaIRI))

        # Now, parse the json file, and load elements into the graph:
        self._parseJsonData()

    def _parseJsonData(self):
        '''
        Will parse the associated json data looking for elements which meet the following criteria:
        1) Have a defined 'field' name
        2) Have a defined ontologyMapping value
        3) Have an ontologyMappingType of 'simple'

        When met, statements will be added to a list of statements to insert into the Tbox and stored as a
        list.
        '''
        for k in self.jsonConfig.keys():
            if "fields" in self.jsonConfig[k].keys():
                for field in self.jsonConfig[k]["fields"].keys():
                    if "ontologyMappingType" in self.jsonConfig[k]["fields"][field].keys() and \
                       self.jsonConfig[k]["fields"][field]["ontologyMappingType"] != "None":
                        
                        if self.jsonConfig[k]["fields"][field]["ontologyMappingType"] == "simple":
                            if "ontologyMapping" in self.jsonConfig[k]["fields"][field].keys() and \
                               self.jsonConfig[k]["fields"][field]["ontologyMapping"] != "":
                                ''' In this case, just add the ontology mapping straight in, respecting the required
                                    flag.
                                '''
                                self._addSchemaConceptMapping(self.jsonConfig[k]["fields"][field]["ontologyMapping"], self.jsonConfig[k]["fields"][field])
                            else:
                                logging.warn("Ontology mapping not defined for field {0}:{1} ; skipping.".format(self.schemaIRI, field))

                        elif self.jsonConfig[k]["fields"][field]["ontologyMappingType"] == "enum":
                            ''' In this case, we need to create a concept in the ontology which is the 'one of' of each enum value. '''
                            # Create a concept which includes all of the enum value concepts
                            eValList = list()
                            for eVal in self.jsonConfig[k]["fields"][field]["enumValues"].keys():
                                if "ontologyMapping" in self.jsonConfig[k]["fields"][field]["enumValues"][eVal].keys() and \
                                   self.jsonConfig[k]["fields"][field]["enumValues"][eVal]["ontologyMapping"] is not None and \
                                   not self.jsonConfig[k]["fields"][field]["enumValues"][eVal]["ontologyMapping"] == "":
                                    eValList.append(self.jsonConfig[k]["fields"][field]["enumValues"][eVal]["ontologyMapping"])
                                else:
                                    logging.warn("Ontology mapping not defined for enum value {0}:{1}={2} ; skipping.".format(self.schemaIRI, field, eVal))
                            aggConceptIRI = self._createOneOfBagConcept(field,eValList)

                            # Add the link to the new concept
                            self._addSchemaConceptMapping(aggConceptIRI, self.jsonConfig[k]["fields"][field])

                        elif self.jsonConfig[k]["fields"][field]["ontologyMappingType"] == "multiple":
                            ''' In this case, we need to create a concept in the ontology which is the 'one of' for each concept. '''
                            # Create a concept which includes all of the enum value concepts
                            eValList = list()
                            if "ontologyMappings" in self.jsonConfig[k]["fields"][field].keys() and \
                               not len(self.jsonConfig[k]["fields"][field]["ontologyMappings"]) == 0:
                                for eVal in self.jsonConfig[k]["fields"][field]["ontologyMappings"]:
                                    eValList.append(eVal)
                            else:
                                logging.warn("Ontology mappings not defined for field {0}:{1} ; skipping.".format(self.schemaIRI, field))

                            aggConceptIRI = self._createOneOfBagConcept(field,eValList)

                            # Add the link to the new concept
                            self._addSchemaConceptMapping(aggConceptIRI, self.jsonConfig[k]["fields"][field])
                            
    def _addSchemaConceptMapping(self, concept, data):
        '''
        Given a concept IRI, and a snippet of the data associated with the concept to add,
        '''
        # Check to see if the triple is in there
        iri = rdflib.term.URIRef(u'{}'.format(concept))
        self.graph.add((self.schemaIRI, self.supportsSemanticComponentRelation, iri))
        if "required" in data.keys() and \
           data["required"] == "true":
            self.graph.add((self.schemaIRI, self.requiresSemanticComponentRelation, iri))

        sanityQuery = """SELECT ?parent WHERE {
            <%s> rdfs:subClassOf ?parent .
            }"""%(iri)
        resList = self.graph.query(sanityQuery, initNs = self.initNS)
        if len(resList) == 0:
            self.newConcepts += 1
            logging.info("Adding new semantic concept {0}".format(iri))
            ## Add it:
            self.graph.add((iri, rdflib.namespace.RDF.type, rdflib.namespace.RDFS.Class))
            self.graph.add((iri, rdflib.namespace.RDFS.subClassOf, self.namespace.SemanticComponent))
            if (iri, rdflib.namespace.RDFS.comment, None) not in self.graph:
                self.newDescriptions += 1
                self.graph.add((iri, rdflib.namespace.RDFS.comment,rdflib.Literal(data["description"], lang="en")))
                logging.info("Augmenting semantic concept {0} with description {1}".format(
                    iri,
                    data["description"]))
                
    def _createOneOfBagConcept(self,field,eValList):
        '''
        Given a list of IRI values, will create a named concept mapping to a bag which includes all those
        concepts in the graph, and return a reference to the bag.  The concept name will be based on the field.
        '''
        bag = rdflib.URIRef("{0}{1}-Bag".format(self.namespace,field))
        self.graph.add((bag, rdflib.namespace.RDF.type, rdflib.namespace.RDF.Bag))
        count = 1
        for eVal in eValList:
            self.graph.add((bag, rdflib.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#_{0}'.format(count)),rdflib.URIRef(eVal)))
            count += 1
            
        return bag

    def dumpGraph(self, fileHandle=None):
        '''
        Return the current graph as a string.
        - fileName -- If defined, the graph will be written to the specified file handle; otherwise,
          it will be returned as a string.
        '''
        self.graph.serialize(format='xml', destination=fileHandle)

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Ames Laboratoy on %s.
  Copyright 2015 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-w', '--destination', dest="destinationFile", help="File path to write the resulting ontology to; if empty will write to stdout")
        #parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')
        parser.add_argument(dest="schemaFile", help="path to the json schema definition file", metavar="schemaFile")
        parser.add_argument(dest="ontologyIRI", help="IRI of the ontology [e.g. http://www.anl.gov/cfm/transform.owl]", metavar="ontologyIRI")
        parser.add_argument(dest="ontologyFile", help="File path of the ontology", metavar="ontologyFile")
        parser.add_argument(dest="schemaIRI", help="IRI of the schema we are parsing [e.g. http://www.anl.gov/cfm/transform.owl#cfm13schema]", metavar="schemaIRI")

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose
        schemaFile = args.schemaFile
        ontologyIRI = args.ontologyIRI
        ontologyFile = args.ontologyFile
        schemaIRI = args.schemaIRI
        destination = args.destinationFile

        if verbose is not None and verbose > 0:
            logging.info("Verbose mode on")
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

#        if inpat and expat and inpat == expat:
#            raise CLIError("include and exclude pattern are equal! Nothing will be processed.")

        # Read in the schema file as a json object
        sfd = json.load(open(schemaFile,'r'))

        # Read in the ontology as an RDFLib object
        g=rdflib.Graph()
        g.load(ontologyFile)
        sop = SchemaOntologyProducer(sfd,g,ontologyIRI,schemaIRI)
        logging.debug ("{}".format(sop.dumpGraph()))
        sop.dumpGraph(destination)
        return 0

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
       # sys.argv.append("-h")
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'Utils.addSchemaConfigToTBOX_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
