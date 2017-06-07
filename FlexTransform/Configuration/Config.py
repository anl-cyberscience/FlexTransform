'''
Created on Jul 27, 2014

@author: ahoying
'''
import ast
import configparser
import json
import logging
import os
import re

from FlexTransform.Configuration.ConfigFunctions.ConfigFunctionManager import ConfigFunctionManager
from FlexTransform.SchemaParser import SchemaParser
from FlexTransform.SyntaxParser import Parser


class Config(object):
    '''
    Parser for configuration documents that describe the syntax and schema of
    a source or destination file
    '''

    def __init__(self, config_file, parser_name, trace, trace_list=[]):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.Config')

        self.name = parser_name

        self.trace = trace
        self.trace_index = {}
        self.trace_list = trace_list
        if self.trace:
            for x in self.trace_list:
                for v in x["src_fields"]:
                    self.trace_index[v] = x
                for y in x["dst_fields"]:
                    self.trace_index[y] = x
                for w in x["src_IRIs"]:
                    self.trace_index[w] = x
                for z in x["dst_IRIs"]:
                    self.trace_index[z] = x
            self.logging.debug("Initializing Config with trace_list of {} elements".format(len(trace_list)))

        self.SchemaConfig = None
        self.MetadataSchemaConfig = None
        self.ConfigFunctionManager = ConfigFunctionManager(self.trace, trace_list=trace_list)

        self.config_file = config_file
        self._read_config()

    def _read_config(self):
        '''
        Load the configuration file and pass it to the validator
        '''

        self.config = configparser.ConfigParser(allow_no_value=False)
        self.config.optionxform = str 
        self.config.read_file(self.config_file)

        self._validate_config()

    def _validate_config(self):
        '''
        Validate all required sections of the configuration exist and are correct
        '''

        # Test if required sections exists.
        required_sections = ['SYNTAX', 'SCHEMA']
        for section in required_sections:
            if not self.config.has_section(section):
                raise Exception('RequiredConfigurationSectionNotFound', section)

        # Get FileParser option, throw exception if it doesn't exist or is not valid
        if self.config.has_option('SYNTAX', 'FileParser'):
            file_parser = self.config['SYNTAX']['FileParser']
            
            # Load the appropriate parser for the file type and 
            # validate parser specific configuration
            Parsers = Parser.GetParsers()
            if file_parser in Parsers:
                ParserName = Parsers[file_parser]
                self.Parser = Parser.GetParser(ParserName, self.trace, tracelist=self.trace_list)
                self.Parser.ValidateConfig(self.config)
            else:
                raise Exception('UndefinedParserType', file_parser)
        else:
            raise Exception('RequiredOptionNotFound', 'Syntax: FileParser')
        
        if self.config.has_option('SCHEMA', 'SchemaConfigurationType') \
                and self.config['SCHEMA']['SchemaConfigurationType'] == 'Inline':
            # Build schema from configuration file
            schema_configuration = {}
            
            for key in self.config['SCHEMA']:
                if key == 'SchemaConfigurationType':
                    continue
                
                if key == 'TypeMappings':
                    schema_configuration['TypeMapping'] = self.config['SCHEMA'][key]
                    continue
                
                if key == 'SupportedIndicatorTypes':
                    schema_configuration['SupportedIndicatorTypes'] = self.config['SCHEMA'][key]
                    continue
                
                keyparts = key.split('_', maxsplit=1)
                if len(keyparts) != 2:
                    raise Exception('InlineSchemaError','Key ' + key +
                                    ' could not be parsed into a field name and directive split by _')
                else:
                    if keyparts[0] not in schema_configuration:
                        schema_configuration[keyparts[0]] = {}
                    
                schema_configuration[keyparts[0]][keyparts[1]] = self.config['SCHEMA'][key]
                
            if schema_configuration:
                self.SchemaConfig = self._BuildSchemaConfig(schema_configuration)
            else:
                raise Exception('RequiredOptionNotFound', 'Schema: no inline schema fields defined')
                
        else:
            # Load primary schema definition
            if self.config.has_option('SCHEMA', 'PrimarySchemaConfiguration'):
                self.SchemaConfig = self._ReadSchemaConfig(self.config['SCHEMA']['PrimarySchemaConfiguration'])
            else:
                raise Exception('RequiredOptionNotFound', 'Schema: PrimarySchemaConfiguration')
    
            if self.config.has_option('SCHEMA', 'SiteSchemaConfiguration'):
                site_configs = self.config['SCHEMA']['SiteSchemaConfiguration'].split(";")
                for config in site_configs:
                    new_schema_config = self._ReadSchemaConfig(config)
                    self._MergeDictionaries(self.SchemaConfig, new_schema_config)
                
            if self.config.has_option('SCHEMA', 'MetadataSchemaConfiguration'):
                metadata_schema_config = self._ReadSchemaConfig(self.config['SCHEMA']['MetadataSchemaConfiguration'])
                self._MergeDictionaries(self.SchemaConfig, metadata_schema_config)

        self._validate_schema()
        self.SchemaParser = SchemaParser(self.SchemaConfig, self.trace, tracelist=self.trace_list)
        
        # TODO: Validate that the syntax and schema is read only, write only or read/write and throw an error if necessary
    def _validate_schema(self):
        for outer_key, outer_value in self.SchemaConfig.items():
            for inner_key, inner_value in outer_value['fields'].items():
                if 'datatype' not in inner_value or not inner_value['datatype']:
                    raise Exception('RequiredSchemaOptionNotFound', "{}:{}:{}: 'datatype' not found / invalid".format(self.name, outer_key, inner_key))
                if inner_value['datatype'] == 'datetime' and not ('dateTimeFormat' in inner_value and inner_value['dateTimeFormat']):
                    raise Exception('RequiredSchemaOptionNotFound', "{}:{}:{}: 'dateTimeFormat' element not present / malformed".format(self.name, outer_key, inner_key))

    def calculate_derived_data(self, source_file=None, dest_file=None):
        if hasattr(source_file, "name") and source_file is not None:
            source_file_name = source_file.name
        else:
            source_file_name = ""
        if hasattr(dest_file, "name") and dest_file is not None:
            dest_file_name = dest_file.name
        else:
            dest_file_name = ""

        # TODO - Check that SchemaParser has been set
        if "DerivedData" in self.SchemaParser.SchemaConfig:
            for field in self.SchemaParser.SchemaConfig["DerivedData"]["fields"]:
                # Call the appropriate function, assuming the required data is available:
                if field in self.trace_index.keys():
                    if "ontologyMapping" in self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field] and \
                            not self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field]["ontologyMapping"] is None:
                        self.logging.debug("[TRACE {}]: Found source IRI: {}".format(
                            field, self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field]["ontologyMapping"]))
                        self.trace_index[field]["src_IRIs"].append(
                            self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field]["ontologyMapping"])
                    else:
                        self.logging.debug("[TRACE {}]: No ontologyMapping found".format(field))
                if "valueFunction" in self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field]:
                    value = self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field]["valueFunction"]
                    if field in self.trace_index.keys():
                        self.logging.debug("[TRACE {}]: Calculating function value {}...".format(field, value))
                    field_name = field
                    field_dict = self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field]
                    schema_config_data = self.SchemaParser.SchemaConfig

                    value = self._calculate_function_value(value, field_name, field_dict,
                                                           schema_config=schema_config_data,
                                                           file_name=source_file_name)
                    if value:
                        self.SchemaParser.SchemaConfig["DerivedData"]["fields"][field]["value"] = value
                    if field in self.trace_index.keys():
                        self.logging.debug("[TRACE {}]: Calculated function value = {}".format(field, value))

    def _calculate_function_value(self, value, field_name, field_dict, schema_config=None, file_name=None):
        if value.startswith('&'):
            match = re.match(r'&([^\(]+)\((.*)\)$', value)
            if match:
                function = match.group(1)
                functionarg = match.group(2)

                FunctionValid = self.ConfigFunctionManager.get_function(function)

                if FunctionValid:

                    args = {
                        'fieldName': field_name,
                        'fieldDict': field_dict,
                        'functionArg': functionarg,
                        'fileName': file_name
                    }

                    value = self.ConfigFunctionManager.execute_config_function(function, args)

                else:
                    self.logging.warning('Function %s in field %s is not valid', function,
                                         field_name)
            else:
                raise Exception('InvalidFunctionFormat',
                                'The function reference for field %s, %s, is not valid' % (field_name, value))
        else:
            self.logging.warning('Value %s is not a function reference', value)

        return value

    def _ReadSchemaConfig(self, jsonFile, fileName = None):
        '''
        Read the Schema configuration file in JSON format
        '''
        if not jsonFile.startswith('/'):
            # Find path to json file
            currentdir = os.path.dirname(__file__)
            jsonFile = os.path.join(currentdir, '../', jsonFile)
        
        with open(jsonFile, 'r') as schema_config_file:
            schema_config = json.load(schema_config_file)

        # TODO: Add schema validation call here (remember to create function)
        
        return schema_config
        
    def _MergeDictionaries(self, originalDict, SourceDataRow):
        '''
        Deep recursive merge of values in SourceDataRow into originalDict
        '''
        
        # FIXME: This will break if originalDict has a nested dict that is overwritten by a string object in SourceDataRow. This should throw an error.
        for k, v in SourceDataRow.items():
            if k in originalDict:
                if isinstance(v,dict):
                    self._MergeDictionaries(originalDict[k],SourceDataRow[k])
                elif (isinstance(v,list)):
                    originalDict.append(v)
                elif v is None:
                    del originalDict[k]
                else:
                    originalDict[k] = v
            else:
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
        
        schema_config = {}
        schema_config['IndicatorData'] = {}
        
        if 'SupportedIndicatorTypes' in schemaConfiguration:
            schema_config['IndicatorData']['types'] = {}
            Types = schemaConfiguration.pop('SupportedIndicatorTypes')
            for indicatorType in Types.split(","):
                schema_config['IndicatorData']['types'][indicatorType] = []
        else :
            raise Exception('RequiredOptionNotFound', 'Schema: SupportedIndicatorTypes is not defined')
        
        if 'TypeMapping' in schemaConfiguration:
            type_mapping = ast.literal_eval(schemaConfiguration.pop("TypeMapping"))
            schema_config['IndicatorData']['types'] = type_mapping
        
        fields = {}
        
        # TODO: add additional schema configuration directives
        # TODO: integrate with Ontology to get default schema configurations for specific ontology objects
        
        for field in schemaConfiguration :
            fieldtrace = (field in self.trace_index.keys())
            fields[field] = {}
            fields[field]["datatype"] = "string"
            fields[field]["required"] = True
                
            if "OntologyMapping" in schemaConfiguration[field]:
                OntologyMapping = schemaConfiguration[field].pop("OntologyMapping")
                fields[field]["ontologyMappingType"] = "simple"
                fields[field]["ontologyMapping"] = "http://www.anl.gov/cfm/transform.owl#" + OntologyMapping
                if fieldtrace:
                    self.logging.debug("[TRACE {}]: Found simple ontology mapping: {}".format(
                                                 field,
                                                 fields[field]["ontologyMapping"]))

            elif "OntologyMappingMultiple" in schemaConfiguration[field]:
                OntologyMappings = schemaConfiguration[field].pop("OntologyMappingMultiple")
                fields[field]["ontologyMappingType"] = "multiple"
                fields[field]["ontologyMappings"] = []
                for mapping in OntologyMappings.split("|"):
                    fields[field]["ontologyMappings"].append("http://www.anl.gov/cfm/transform.owl#" + mapping)
                    if fieldtrace:
                        self.logging.debug("[TRACE {}]: Adding multiple ontology mappings: {}".format(
                                                 field,
                                                 fields[field]["ontologyMappings"][-1]))
                        self.trace_index[field]["dst_IRIs"].append(fields[field]["ontologyMappings"][-1])

            elif "OntologyMappingEnum" in schemaConfiguration[field]:
                OntologyMappings = schemaConfiguration[field].pop("OntologyMappingEnum")
                fields[field]["datatype"] = "enum"
                fields[field]["ontologyMappingType"] = "enum"
                fields[field]["enumValues"] = {}
                for mapping in OntologyMappings.split("|"):
                    kv = mapping.split(":")
                    fields[field]["enumValues"][kv[0]] = {}
                    fields[field]["enumValues"][kv[0]]["ontologyMapping"] = "http://www.anl.gov/cfm/transform.owl#" + kv[1]
                    if fieldtrace:
                        self.logging.debug("[TRACE {}]: Adding enumerated ontology mappings: {}".format(
                                                 field,
                                                 fields[field]["enumValues"][kv[0]]["ontologyMappings"]))
                        self.trace_index[field]["dst_IRIs"].append(fields[field]["enumValues"][kv[0]]["ontologyMappings"])

            else:
                fields[field]["ontologyMappingType"] = "none"
                if fieldtrace:
                    self.logging.debug("[TRACE {}]: Found no ontology mapping".format(field))

            for Directive in schemaConfiguration[field] :
                if fieldtrace:
                    self.logging.debug("[TRACE {}]: Setting special directive {}".format(field, Directive))
                if Directive == "DefaultValue":
                    fields[field]["defaultValue"] = schemaConfiguration[field][Directive]
                elif Directive == "DataType":
                    fields[field]["datatype"] = schemaConfiguration[field][Directive]
                elif Directive == "DateTimeFormat":
                    fields[field]["dateTimeFormat"] = schemaConfiguration[field][Directive]
                else:
                    raise Exception("UnknownDirective", Directive + " on field " + field + " is not defined")    
                    
        schema_config['IndicatorData']['fields'] = fields
        
        return schema_config
