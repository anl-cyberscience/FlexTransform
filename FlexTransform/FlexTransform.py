'''
Created on Jul 27, 2014

@author: ahoying
'''

import logging

from .Configuration import Config
from .OntologyOracle import OntologyOracle

# TODO: Document in Sphinx compatible format
# TODO: Optimization - Too much pass by value for large dictionary objects currently, need to move to more pass by reference to minimize cpu and memory resource usage

class FlexTransform(object):
    '''
    API for accessing performing Flexible Transform of source documents to target documents based on syntax and schema mappings against the ontology
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.Parsers = {}
        self.logging = logging.getLogger('FlexTransform')
        
    def AddParser(self, parserName, configFile) :
        '''
        Add parsers to the FlexTransform object
        '''
        
        parserConfig = Config(configFile)
        
        if (parserName in self.Parsers) :
            self.logging.warn('Parser %s already configured, configuration will be overwritten', parserName)
        
        if (parserConfig) :
            self.Parsers[parserName] = parserConfig
        
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
        '''
        
        if (sourceFileName is None or sourceParserName is None or targetParserName is None) :
            raise Exception('MissingParameter', 'Required parameter is not defined')
        
        if (sourceParserName not in self.Parsers) :
            raise Exception('ParserNotFound', 'Source parser %s has not been configured' % sourceParserName)

        if (targetParserName not in self.Parsers) :
            raise Exception('ParserNotFound', 'Target parser %s has not been configured' % targetParserName)
        
        if (sourceMetaData is not None and not isinstance(sourceMetaData,dict)) :
            raise Exception('IncorrectFormat', 'sourceMetaData must be in dictionary format')
        
        # Parse and validate configurations
        SourceConfig = self.Parsers[sourceParserName]
        DestinationConfig = self.Parsers[targetParserName]
    
        # Parse source file into dictionary object
        SourceData = SourceConfig.Parser.Read(sourceFileName)
        
        if (SourceData is None) :
            raise Exception('NoSourceData', 'Source data file could not be parsed, no data')
        
        # Map source file data to source schema
        MappedData = SourceConfig.SchemaParser.MapDataToSchema(SourceData, oracle)
        
        if (sourceMetaData is not None) :
            SourceConfig.SchemaParser.MapMetadataToSchema(sourceMetaData)
        
        # Map source data to destination schema
        TransformedData = DestinationConfig.SchemaParser.TransformData(MappedData, oracle)
        
        # Finalize data to be written
        FinalizedData = DestinationConfig.Parser.Finalize(TransformedData)
        
        if (targetFileName is not None) :
            DestinationConfig.Parser.Write(targetFileName, FinalizedData)
        
        return FinalizedData


def main():
    import argparse
    import os
    import json
    
    logging.basicConfig(format='%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s', level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description="Transform a source file's syntax and schema to the target file document type")
    parser.add_argument('--src-config',
                        type=argparse.FileType('r'),
                        help='Source file parser configuration',
                        metavar='CONFIG',
                        required=True)
    parser.add_argument('--src',
                        type=argparse.FileType('r'),
                        help='Source file',
                        required=True)
    parser.add_argument('--src-metadata',
                        type=argparse.FileType('r'),
                        help='Source Metadata file',
                        required=False)
    parser.add_argument('--dst-config',
                        type=argparse.FileType('r'),
                        help='Destination file parser configuration',
                        metavar='CONFIG',
                        required=True)
    parser.add_argument('--dst',
                        type=argparse.FileType('w'),
                        help='Destination file',
                        required=True)

    parser.add_argument('--tbox-uri',
                        type=argparse.FileType('r'),
                        help='The uri location of the tbox file to load',
                        required=False)


    args = parser.parse_args()

    try:       
        Transform = FlexTransform()
        Transform.AddParser('src', args.src_config)
        Transform.AddParser('dst', args.dst_config)

        metadata = None
                
        if (args.src_metadata) :
            metadata = json.load(args.src_metadata)
        
        kb = None

        if (args.tbox_uri) :
            kb = OntologyOracle.Oracle(args.tbox_uri)

        FinalizedData = Transform.TransformFile(sourceFileName=args.src, targetFileName=args.dst, sourceParserName='src', targetParserName='dst', sourceMetaData=metadata, oracle=kb)
        args.dst.close()
        
    except Exception as inst :
        logging.exception(inst)
        args.dst.close()
        os.remove(args.dst.name)

    else :
        logging.info("Success")

if __name__ == '__main__':
    main()
