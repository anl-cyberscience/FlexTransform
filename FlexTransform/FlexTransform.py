"""
Created on Jul 27, 2014

@author: ahoying
"""

import logging
import warnings

import rdflib

from .Configuration import Config
from .OntologyOracle import Oracle


# TODO: Document in Sphinx compatible format

class FlexTransform(object):
    '''
    API for accessing performing Flexible Transform of source documents to target documents based on syntax and schema mappings against the ontology
    '''
    
    def __init__(self,
                 logging_level=logging.WARN,
                 trace=None,
                 source_fields=None,
                 destination_fields=None,
                 source_iri=None,
                 destination_iri=None):
        self.Parsers = {}
        self.logging = logging.getLogger('FlexTransform')
        self.logging.setLevel(logging_level)
        self.oracle = None

        if trace is None and (source_fields or source_iri or destination_fields or destination_iri):
            self.trace = True
        else:
            self.trace = trace

        self.trace_list = []
        if self.trace:
            self._create_trace_list(source_fields=source_fields, destination_fields=destination_fields,
                                    source_iri=source_iri, destination_iri=destination_iri)

    def add_parser(self, parser_name, config_file):
        """
        Add Parser to FlexTransform Object

        :param parser_name: String name of parser to add
        :param config_file: File of parser

        :type parser_name: String
        :type config_file: File Object
        :return:
        """
        
        parser_config = Config(config_file, parser_name, self.trace, trace_list=self.trace_list)

        if parser_name in self.Parsers:
            self.logging.warn('Parser %s already configured, configuration will be overwritten', parser_name)

        if parser_config:
            self.Parsers[parser_name] = parser_config
            
    def add_oracle(self, tbox_location, schema_iri):
        '''
        Add oracle to the FlexTransform object"
        '''
        
        # TODO add error checking for locations
        self.oracle = Oracle(tbox_location, rdflib.URIRef(schema_iri), self.trace, trace_list=self.trace_list)
        
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
        source_config = self.Parsers[source_parser_name]
        destination_config = self.Parsers[target_parser_name]

        # Calculate "DerivedData" functions
        source_config.calculate_derived_data(source_file=source_file, dest_file=target_file)

        # Parse source file into dictionary object
        source_data = source_config.Parser.Read(source_file, source_config)
        
        if source_data is None:
            raise Exception('NoSourceData', 'Source data file could not be parsed, no data')
        
        # Map source file data to source schema
        mapped_data = source_config.SchemaParser.map_data_to_schema(source_data, oracle)
        
        if source_meta_data is not None:
            source_config.SchemaParser.map_metadata_to_schema(source_meta_data)
        
        # Map source data to destination schema
        transformed_data = destination_config.SchemaParser.TransformData(mapped_data, oracle)
        
        # Finalize data to be written
        finalized_data = destination_config.Parser.Finalize(transformed_data)
        
        if target_file is not None:
            destination_config.Parser.Write(target_file, finalized_data)
        
        return finalized_data

    def _create_trace_list(self, source_fields=None, destination_fields=None, source_iri=None, destination_iri=None):

        trace_list = []
        if source_fields:
            for arg in source_fields:
                trace_list.append({"src_fields": [arg], "src_IRIs": list(), "dst_fields": list(), "dst_IRIs": list()})
        if source_iri:
            for arg in source_iri:
                trace_list.append({"src_fields": list(), "src_IRIs": [arg], "dst_fields": list(), "dst_IRIs": list()})
        if destination_fields:
            for arg in destination_fields:
                trace_list.append({"src_fields": list(), "src_IRIs": list(), "dst_fields": [arg], "dst_IRIs": list()})
        if destination_iri:
            for arg in destination_iri:
                trace_list.append({"src_fields": list(), "src_IRIs": list(), "dst_fields": list(), "dst_IRIs": [arg]})
        self.trace_list = trace_list

    def AddParser(self, parserName, configFile, sourceFileName = None, destFileName = None):
        warnings.warn('"AddParser()" has been deprecated in favor of "add_parser()"', DeprecationWarning)
        self.logging.warn('"AddParser()" has been deprecated in favor of "add_parser()"')
        return self.add_parser(parserName, configFile)

    def TransformFile(self, sourceFileName, sourceParserName, targetParserName,
                      targetFileName=None, sourceMetaData=None, oracle=None):
        warnings.warn('"TransformFile()" has been deprecated in favor of "transform()"', DeprecationWarning)
        self.logging.warn('"TransformFile()" has been deprecated in favor of "transform()"')
        return self.transform(sourceFileName, sourceParserName, targetParserName, target_file=targetFileName,
                              source_meta_data=sourceMetaData, oracle=oracle)
if __name__ == '__main__':
    raise Exception("Unsupported", "FlexTransform.py should not be called directly, use helper script FlexT.py")

