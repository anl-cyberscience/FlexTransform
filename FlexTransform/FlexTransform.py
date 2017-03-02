"""
Created on Jul 27, 2014

@author: ahoying
"""

import logging

import rdflib

from .Configuration import Config
from .OntologyOracle import Oracle


# TODO: Document in Sphinx compatible format
# TODO: Optimization - Too much pass by value for large dictionary objects currently, need to move to more pass by reference to minimize cpu and memory resource usage

class FlexTransform(object):
    '''
    API for accessing performing Flexible Transform of source documents to target documents based on syntax and schema mappings against the ontology
    '''
    
    def __init__(self, logging_level=logging.WARN, tracelist=[]):
        '''
        Constructor
        '''
        self.Parsers = {}
        self.logging = logging.getLogger('FlexTransform')
        self.logging.setLevel(logging_level)
        self.oracle = None
        self.tracelist = tracelist
        
    def add_parser(self, parser_name, config_file):
        """
        Add Parser to FlexTransform Object

        :param parser_name: String name of parser to add
        :param config_file: File of parser

        :type parser_name: String
        :type config_file: File Object
        :return:
        """
        
        parserConfig = Config(config_file, trace_list=self.tracelist)
        
        if parser_name in self.Parsers:
            self.logging.warn('Parser %s already configured, configuration will be overwritten', parser_name)
        
        if parserConfig:
            self.Parsers[parser_name] = parserConfig
            
    def add_oracle(self, tbox_loc, schema_IRI):
        '''
        Add oracle to the FlexTransform object"
        '''
        
        #TODO add error checking for locations
        self.oracle = Oracle(tbox_loc, rdflib.URIRef(schema_IRI), tracelist=self.tracelist)
        
    def transform(self, source_file, source_parser_name, target_parser_name,
                  target_file=None, source_meta_data=None, oracle=None):
        """
        Transform the data from fileName using sourceParserName as the source and targetParserName as the destination.
        Returns transformed data to the caller.

        :param source_file: File containing information to be transformed
        :param source_parser_name: String descriptor of parser to be used for source
        :param target_parser_name:String descriptor of parser to be used for destination
        :param target_file: File to place transformed information
        :param source_meta_data:
        :param oracle: An instance of the OntologyOracle, initialized with the TBOX URI.  If NONE, will not be used.

        :type source_file: File Object
        :type source_parser_name: String
        :type target_parser_name: String
        :type target_file: File Object
        :return:
        """
        
        if source_file is None or source_parser_name is None or target_parser_name is None:
            raise Exception('MissingParameter', 'Required parameter is not defined')
        
        if source_parser_name not in self.Parsers:
            raise Exception('ParserNotFound', 'Source parser %s has not been configured' % source_parser_name)

        if target_parser_name not in self.Parsers:
            raise Exception('ParserNotFound', 'Target parser %s has not been configured' % target_parser_name)
        
        if source_meta_data is not None and not isinstance(source_meta_data, dict):
            raise Exception('IncorrectFormat', 'sourceMetaData must be in dictionary format')
        
        if self.oracle:
            oracle = self.oracle
        
        # Parse and validate configurations
        SourceConfig = self.Parsers[source_parser_name]
        DestinationConfig = self.Parsers[target_parser_name]

        # Calculate "DerivedData" functions
        SourceConfig.calculate_derived_data(source_file=source_file, dest_file=target_file)

        # Parse source file into dictionary object
        SourceData = SourceConfig.Parser.Read(source_file, SourceConfig)
        
        if SourceData is None:
            raise Exception('NoSourceData', 'Source data file could not be parsed, no data')
        
        # Map source file data to source schema
        MappedData = SourceConfig.SchemaParser.MapDataToSchema(SourceData, oracle)
        
        if source_meta_data is not None:
            SourceConfig.SchemaParser.MapMetadataToSchema(source_meta_data)
        
        # Map source data to destination schema
        TransformedData = DestinationConfig.SchemaParser.TransformData(MappedData, oracle)
        
        # Finalize data to be written
        FinalizedData = DestinationConfig.Parser.Finalize(TransformedData)
        self.logging.debug("FlexTransform.Transform(): FinalizedData Dictionary: ")
        
        if target_file is not None:
            DestinationConfig.Parser.Write(target_file, FinalizedData)
        
        return FinalizedData


if __name__ == '__main__':
    raise Exception("Unsupported", "FlexTransform.py should not be called directly, use helper script FlexT.py")

