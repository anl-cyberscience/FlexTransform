'''
Created on Jul 27, 2014

@author: ahoying
'''

import logging
import rdflib
import pprint
import sys
from .Configuration import Config
from .OntologyOracle import Oracle

# TODO: Document in Sphinx compatible format
# TODO: Optimization - Too much pass by value for large dictionary objects currently, need to move to more pass by reference to minimize cpu and memory resource usage

class FlexTransform(object):
    '''
    API for accessing performing Flexible Transform of source documents to target documents based on syntax and schema mappings against the ontology
    '''
    
    def __init__(self, tracelist=[]):
        '''
        Constructor
        '''
        self.pprint = pprint.PrettyPrinter()
        self.Parsers = {}
        self.logging = logging.getLogger('FlexTransform')
        self.oracle = None
        self.tracelist = tracelist
        
    def AddParser(self, parserName, configFile, sourceFileName = None, destFileName = None) :
        '''
        Add parsers to the FlexTransform object
        '''
        
        parserConfig = Config(configFile, sourceFileName, destFileName, tracelist = self.tracelist)
        
        if (parserName in self.Parsers) :
            self.logging.warn('Parser %s already configured, configuration will be overwritten', parserName)
        
        if (parserConfig) :
            self.Parsers[parserName] = parserConfig
            
    def AddOracle(self, tbox_loc, schema_IRI):
        '''
        Add oracle to the FlexTransform object"
        '''
        
        #TODO add error checking for locations
        self.oracle = Oracle(tbox_loc, rdflib.URIRef(schema_IRI), tracelist=self.tracelist)
        
    def TransformFile(self, sourceFileName, sourceParserName, targetParserName, targetFileName=None, sourceMetaData=None, oracle=None):
        '''
        Transform the data from fileName using sourceParserName as the source and 
        targetParserName as the destination. Returns transformed data to the caller.
        
        Params:
        * sourceFileName
        * sourceParserName
        * targetParserName
        * targetFileName
        * sourceMetaData
        * oracle - An instance of the OntologyOracle, initialized with the TBOX URI.  If NONE, the ontology
          will not be used.
        * tracelist - A list of source schema elements to trace through the program execution.
        '''
        
        if (sourceFileName is None or sourceParserName is None or targetParserName is None) :
            raise Exception('MissingParameter', 'Required parameter is not defined')
        
        if (sourceParserName not in self.Parsers) :
            raise Exception('ParserNotFound', 'Source parser %s has not been configured' % sourceParserName)

        if (targetParserName not in self.Parsers) :
            raise Exception('ParserNotFound', 'Target parser %s has not been configured' % targetParserName)
        
        if (sourceMetaData is not None and not isinstance(sourceMetaData,dict)) :
            raise Exception('IncorrectFormat', 'sourceMetaData must be in dictionary format')
        
        if self.oracle:
            oracle = self.oracle
        
        # Parse and validate configurations
        SourceConfig = self.Parsers[sourceParserName]
        DestinationConfig = self.Parsers[targetParserName]
    
        # Parse source file into dictionary object
        SourceData = SourceConfig.Parser.Read(sourceFileName, SourceConfig)
        
        '''
        self.logging.debug("FlexTransform.Transform(): SourceData Dictionary: ")
        self.pprint.pprint(SourceData)
        '''
        
        if (SourceData is None) :
            raise Exception('NoSourceData', 'Source data file could not be parsed, no data')
        
        # Map source file data to source schema
        MappedData = SourceConfig.SchemaParser.MapDataToSchema(SourceData, oracle)

        '''
        self.logging.debug("FlexTransform.Transform(): MappedData Dictionary: ")
        self.pprint.pprint(MappedData)
        '''
        
        if (sourceMetaData is not None) :
            SourceConfig.SchemaParser.MapMetadataToSchema(sourceMetaData)
        
        # Map source data to destination schema
        TransformedData = DestinationConfig.SchemaParser.TransformData(MappedData, oracle)

        self.logging.debug("FlexTransform.Transform(): TransformedData Dictionary: ")
        self.pprint.pprint(TransformedData)
        
        # Finalize data to be written
        FinalizedData = DestinationConfig.Parser.Finalize(TransformedData)
        self.logging.debug("FlexTransform.Transform(): FinalizedData Dictionary: ")
        self.pprint.pprint(FinalizedData)
        
        if (targetFileName is not None) :
            DestinationConfig.Parser.Write(targetFileName, FinalizedData)
        
        return FinalizedData


if __name__ == '__main__':
    raise Exception("Unsupported","FlexTransform.py should not be called directly, use helper script FlexT.py")

