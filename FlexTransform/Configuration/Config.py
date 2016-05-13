'''
Created on Jul 27, 2014

@author: ahoying
'''
import ast
import json
import os
import logging
import configparser
from FlexTransform.SyntaxParser import Parser
from FlexTransform.SchemaParser import SchemaParser

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
        self.config.optionxform = str 
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
        
        if (self.config.has_option('SCHEMA', 'SchemaConfigurationType') and self.config['SCHEMA']['SchemaConfigurationType'] == 'Inline') :
            # Build schema from configuration file
            schemaConfiguration = {}
            
            for key in self.config['SCHEMA'] :
                if (key == 'SchemaConfigurationType') :
                    continue
                
                if (key == 'TypeMappings') :
                    schemaConfiguration['TypeMapping'] = self.config['SCHEMA'][key]
                    continue
                
                if (key == 'SupportedIndicatorTypes') :
                    schemaConfiguration['SupportedIndicatorTypes'] = self.config['SCHEMA'][key]
                    continue
                
                keyparts = key.split('_', maxsplit=1)
                if (len(keyparts) != 2) :
                    raise Exception('InlineSchemaError','Key ' + key + ' could not be parsed into a field name and directive split by _')
                else :
                    if (keyparts[0] not in schemaConfiguration) :
                        schemaConfiguration[keyparts[0]] = {}
                    
                schemaConfiguration[keyparts[0]][keyparts[1]] = self.config['SCHEMA'][key]
                
            if (schemaConfiguration) :
                self.SchemaConfig = self._BuildSchemaConfig(schemaConfiguration)
            else :
                raise Exception('RequiredOptionNotFound', 'Schema: no inline schema fields defined')
                
        else :
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
                
    def _BuildSchemaConfig(self, schemaConfiguration):
        '''
        Create a schema configuration dictionary from inline configuration data in the source document
        
        The supported indicator types must be defined in the SupportedIndicatorTypes key
        
        Example:
        
        SupportedIndicatorTypes = IPv4-Address-Block,DNS-Hostname-Block
        
        Fields and directives are defined using a field_directive format. Field names and directives are case sensitive. 
        
        Current accepted directives:
            OntologyMapping
            OntologyMappingMultiple
            OntologyMappingEnum
            DefaultValue
            DataType
            DateTimeFormat
            
        To map to a single simple ontology, use OntologyMapping.
        
        Example:
        IPv4Address_OntologyMapping = IPv4AddressIndicatorValueSemanticComponent
        
        maps to:
        
        "IPv4Address": {
                            "datatype": "string",
                            "required": true,
                            "ontologyMappingType": "simple",
                            "ontologyMapping": "http://www.anl.gov/cfm/transform.owl#IPv4AddressIndicatorValueSemanticComponent"
                       }
                       
        To map to multiple ontologies, use OntologyMappingMultiple, each separated by a |
        
        Example:
        Indicator_OntologyMappingMultiple = IPv4AddressIndicatorValueSemanticComponent|IPv6AddressIndicatorValueSemanticComponent|DNSIndicatorValueSemanticComponent
        
        maps to:
        
        "Indicator": {
                            "datatype": "string",
                            "required": true,
                            "ontologyMappingType": "multiple",
                            "ontologyMappings": [ 
                                                    "http://www.anl.gov/cfm/transform.owl#IPv4AddressIndicatorValueSemanticComponent",
                                                    "http://www.anl.gov/cfm/transform.owl#IPv6AddressIndicatorValueSemanticComponent",
                                                    "http://www.anl.gov/cfm/transform.owl#DNSIndicatorValueSemanticComponent"
                                                ]
                       }
                       
        To map to multiple ontologies with a defined value, use OntologyMappingEnum, in the format of value:ontologymapping|value:ontologymapping
        
        Example:
        restriction_OntologyMappingEnum = public:PublicCFM13SharingRestrictionSemanticConcept|need-to-know:NeedToKnowCFM13SharingRestrictionSemanticConcept|private:PrivateCFM13SharingRestrictionSemanticConcept
        
        maps to:
        
        "restriction": {
                "datatype": "enum",
                "required": true,
                "ontologyMappingType": "enum",
                "enumValues": {
                    "public": {
                        "ontologyMapping": "http://www.anl.gov/cfm/transform.owl#PublicCFM13SharingRestrictionSemanticConcept"
                    },
                    "need-to-know": {
                        "ontologyMapping": "http://www.anl.gov/cfm/transform.owl#NeedToKnowCFM13SharingRestrictionSemanticConcept"
                    },
                    "private": {
                        "ontologyMapping": "http://www.anl.gov/cfm/transform.owl#PrivateCFM13SharingRestrictionSemanticConcept"
                    }
                }
            }
        
        Additional configuration items, like default value, can be included as well, with or without an OntologyMapping.
        
        Example:
        Origin_DefaultValue = Federated
        
        maps to:
        
        "Origin": {
                        "datatype": "string",
                        "required": true,
                        "defaultValue": "Federated",
                        "ontologyMappingType": "none"
                  }
        '''
        
        SchemaConfig = {}
        SchemaConfig['IndicatorData'] = {}
        
        if ('SupportedIndicatorTypes' in schemaConfiguration) :
            SchemaConfig['IndicatorData']['types'] = {}
            Types = schemaConfiguration.pop('SupportedIndicatorTypes')
            for indicatorType in Types.split(",") :
                SchemaConfig['IndicatorData']['types'][indicatorType] = []
        else :
            raise Exception('RequiredOptionNotFound', 'Schema: SupportedIndicatorTypes is not defined')
        
        if ('TypeMapping' in schemaConfiguration) :
            TypeMapping = ast.literal_eval(schemaConfiguration.pop("TypeMapping"))
            SchemaConfig['IndicatorData']['types'] = (TypeMapping)
        
        fields = {}
        
        # TODO: add additional schema configuration directives
        # TODO: integrate with Ontology to get default schema configurations for specific ontology objects
        
        for field in schemaConfiguration :
            fields[field] = {}
            fields[field]["datatype"] = "string"
            fields[field]["required"] = True
                
            if ("OntologyMapping" in schemaConfiguration[field]) :
                OntologyMapping = schemaConfiguration[field].pop("OntologyMapping")
                fields[field]["ontologyMappingType"] = "simple"
                fields[field]["ontologyMapping"] = "http://www.anl.gov/cfm/transform.owl#" + OntologyMapping
                
            elif ("OntologyMappingMultiple" in schemaConfiguration[field]) :
                OntologyMappings = schemaConfiguration[field].pop("OntologyMappingMultiple")
                fields[field]["ontologyMappingType"] = "multiple"
                fields[field]["ontologyMappings"] = []
                for mapping in OntologyMappings.split("|") :
                    fields[field]["ontologyMappings"].append("http://www.anl.gov/cfm/transform.owl#" + mapping)
                    
            elif ("OntologyMappingEnum" in schemaConfiguration[field]) :
                OntologyMappings = schemaConfiguration[field].pop("OntologyMappingEnum")
                fields[field]["datatype"] = "enum"
                fields[field]["ontologyMappingType"] = "enum"
                fields[field]["enumValues"] = {}
                for mapping in OntologyMappings.split("|") :
                    kv = mapping.split(":")
                    fields[field]["enumValues"][kv[0]] = {}
                    fields[field]["enumValues"][kv[0]]["ontologyMapping"] = "http://www.anl.gov/cfm/transform.owl#" + kv[1]
                    
            else :
                fields[field]["ontologyMappingType"] = "none"
            
            for Directive in schemaConfiguration[field] :
                if (Directive == "DefaultValue") :
                    fields[field]["defaultValue"] = schemaConfiguration[field][Directive]
                elif (Directive == "DataType") :
                    fields[field]["datatype"] = schemaConfiguration[field][Directive]
                elif (Directive == "DateTimeFormat") :
                    fields[field]["dateTimeFormat"] = schemaConfiguration[field][Directive]
                else :
                    raise Exception("UnknownDirective", Directive + " on field " + field + " is not defined")    
                    
        SchemaConfig['IndicatorData']['fields'] = fields
        
        return SchemaConfig
        
        
