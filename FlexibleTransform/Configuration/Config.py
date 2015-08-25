'''
Created on Jul 27, 2014

@author: ahoying
'''

import configparser
from FlexTransform.SyntaxParser import Parser
from FlexTransform.SchemaParser import SchemaParser
import json
import os
import logging

class Config(object):
    '''
    Parser for configuration documents that describe the syntax and schema of
    a source or destination file
    '''

    def __init__(self, config_file):
        '''
        Constructor
        '''

        self.SchemaConfig = None
        self.MetadataSchemaConfig = None

        self.config_file = config_file
        self._ReadConfig()
        
        self.logging = logging.getLogger('FlexTransform.Config')

    def _ReadConfig(self):
        '''
        Load the configuration file and pass it to the validator
        '''

        self.config = configparser.ConfigParser(allow_no_value=False)
        self.config.read_file(self.config_file)

        self._ValidateConfig()
        

    def _ValidateConfig(self):
        '''
        Validate all required sections of the configuration exist and are correct
        '''

        # Test if required sections exists.
        required_sections = ['SYNTAX','SCHEMA']
        for section in required_sections :
            if (not self.config.has_section(section)) :
                raise Exception('RequiredConfigurationSectionNotFound', section)

        # Get FileParser option, throw exception if it doesn't exist or is not valid
        if (self.config.has_option('SYNTAX', 'FileParser')) :
            FileParser = self.config['SYNTAX']['FileParser']
            
            # Load the appropriate parser for the file type and 
            # validate parser specific configuration
            Parsers = Parser.GetParsers()
            if (FileParser in Parsers) :  # @UndefinedVariable
                ParserName = Parsers[FileParser]
                self.Parser = Parser.GetParser(ParserName)  # @UndefinedVariable
                self.Parser.ValidateConfig(self.config)
            else :
                raise Exception('UndefinedParserType', FileParser)
        else :
            raise Exception('RequiredOptionNotFound', 'Syntax: FileParser')
        
        # Load primary schema definition
        if (self.config.has_option('SCHEMA', 'PrimarySchemaConfiguration')) :
            self.SchemaConfig = self._ReadSchemaConfig(self.config['SCHEMA']['PrimarySchemaConfiguration'])
        else :
            raise Exception('RequiredOptionNotFound', 'Schema: PrimarySchemaConfiguration')

        if (self.config.has_option('SCHEMA', 'SiteSchemaConfiguration')) :
            NewSchemaConfig = self._ReadSchemaConfig(self.config['SCHEMA']['SiteSchemaConfiguration'])
            self._MergeDictionaries(self.SchemaConfig, NewSchemaConfig)
            
        if (self.config.has_option('SCHEMA', 'MetadataSchemaConfiguration')) :
            MetadataSchemaConfig = self._ReadSchemaConfig(self.config['SCHEMA']['MetadataSchemaConfiguration'])
            self._MergeDictionaries(self.SchemaConfig, MetadataSchemaConfig)
        
        self.SchemaParser = SchemaParser(self.SchemaConfig)
        
        # TODO: Validate that the syntax and schema is read only, write only or read/write and throw an error if necessary

    def _ReadSchemaConfig(self, jsonFile):
        '''
        Read the Schema configuration file in JSON format
        '''
        if (not jsonFile.startswith('/')) :
            # Find path to json file
            currentdir = os.path.dirname(__file__)
            jsonFile = os.path.join(currentdir, '../', jsonFile)
        
        f = open(jsonFile, 'r')
        SchemaConfig = json.load(f)
        f.close()
        
        return SchemaConfig
        
    def _MergeDictionaries(self, originalDict, SourceDataRow):
        '''
        Deep recursive merge of values in SourceDataRow into originalDict
        '''
        
        # FIXME: This will break if originalDict has a nested dict that is overwritten by a string object in SourceDataRow. This should throw an error.
        for k, v in SourceDataRow.items():
            if (k in originalDict) :
                if (isinstance(v,dict)) :
                    self._MergeDictionaries(originalDict[k],SourceDataRow[k])
                elif (isinstance(v,list)) :
                    originalDict.append(v)
                else :
                    originalDict[k] = v
            else :
                originalDict[k] = v
                
        
        