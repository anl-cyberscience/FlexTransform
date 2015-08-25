'''
Created on Jul 28, 2014

@author: ahoying
'''

from lxml import etree
import re
from collections import defaultdict
import inspect
import logging
import os

from FlexTransform.SyntaxParser.Parser import Parser
import FlexTransform.SyntaxParser.XMLParsers
from FlexTransform.SchemaParser import SchemaParser

class XMLParser(Parser):
    '''
    XML Syntax Parsers
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.XMLParser = None
        self.AdvancedParser = None
        self.ParsedData = None
        self.logging = logging.getLogger('FlexTransform.XMLParser')

    def LoadAdvancedParser(self,CustomParser):
        '''
        Returns the Custom Parser Class from the configuration file if it exists
        '''
        for name, obj in inspect.getmembers(FlexTransform.SyntaxParser.XMLParsers, inspect.isclass) :
            if (name == CustomParser) :
                return obj();

    def ValidateConfig(self,config):
        '''
        Validate XML Parser specific configuration options
        '''
        if (config.has_section('XML')) :
            if (config.getboolean('XML', 'ValidateSchema', fallback=False)) :
                if (config.has_option('XML', 'SchemaFile')) :
                    SchemaFile = config['XML']['SchemaFile']
                    if (not SchemaFile.startswith('/')) :
                        # Find path to schema file
                        currentdir = os.path.dirname(__file__)
                        SchemaFile = os.path.join(currentdir, '../', SchemaFile)
                    try :
                        schema_root = etree.parse(SchemaFile)
                        XMLSchema = etree.XMLSchema(schema_root)
                        self.XMLParser = etree.XMLParser(schema = XMLSchema)
                    except OSError :
                        raise Exception('XMLSchemaError', 'Error opening ' + SchemaFile)
                    except etree.XMLSyntaxError as e:
                        raise Exception('XMLSchemaError', e.msg)

                else :
                    raise Exception('RequiredOptionNotFound', 'XML: SchemaFile')

            if (config.has_option('XML', 'CustomParser')) :
                CustomParser = config['XML']['CustomParser']
                self.AdvancedParser = self.LoadAdvancedParser(CustomParser)
                if (self.AdvancedParser == None) :
                    raise Exception('CustomParserNotDefined', 'XML: ' + CustomParser)
                
                if (config.has_section(CustomParser)) :
                    self.AdvancedParser.ValidateConfig(config)
                
    def Read(self, file):
        '''
        Read file and parse into Transform object
        '''
        
        self.ParsedData = None
               
        if (self.AdvancedParser) :
            self.ParsedData = self.AdvancedParser.Read(file, self.XMLParser)
        else :
            self.ParsedData = self._ParseXMLData(file)
            
        return self.ParsedData

    def _ParseXMLData(self, file):
        # TODO: Create a generic XML parser
        raise Exception('GenericXMLParser', 'XML Parser does not exist')
    
    def Write(self, file, FinalizedData):
        '''
        Write the file out using either an advanced XML parser or the generic parser.
        '''
        
        if (self.AdvancedParser) :
            self.AdvancedParser.Write(file, FinalizedData)
        else :
            self._WriteXMLData(file, FinalizedData)
            
        if (self.XMLParser) :
            # Validate the created file against the XML schema
            xmlfile = open(file.name, mode='r')
            etree.parse(xmlfile, self.XMLParser)
            
    def Finalize(self, MappedData):
        '''
        Finalize the formatting of the data before being sent to the Write object or returned to the caller
        '''
        
        if ('IndicatorData' not in MappedData or MappedData['IndicatorData'].__len__() == 0) :
            raise Exception('NoIndicatorData', 'Transformed data has no indicators, nothing to write')
        
        return self._MappedDataToXMLDict(MappedData)
            
    def _WriteXMLData(self, file, MappedData):
        # TODO: Create a generic XML parser
        raise Exception('GenericXMLParser', 'XML Writer does not exist')
    
    def _MappedDataToXMLDict(self, MappedData):
        '''
        Take the Transformed data object, and rebuild the dictionary for the XML parser from the schema data
        '''
        ParsedData = {}
        
        for rowType in MappedData :
            if (isinstance(MappedData[rowType],list)) :
                ParsedData[rowType] = []
                for row in MappedData[rowType] :
                    if (isinstance(row,dict)) :
                        DataRow = self._BuildXMLDictRow(row)
                        ParsedData[rowType].append(DataRow)
                    else :
                        raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            elif (isinstance(MappedData[rowType],dict)) :
                DataRow = self._BuildXMLDictRow(MappedData[rowType])
                ParsedData[rowType] = DataRow
            else :
                raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            
        return ParsedData

    def _BuildXMLDictRow(self, row, parentValueMap=None):
        '''
        Take a row from the MappedData object and return an unflattened dictionary for passing to dict_to_etree
        '''
        DataRow = {}
        
        for k, v in row.items() :
            if (parentValueMap is not None and 'valuemap' in v) :
                v['valuemap'] = v['valuemap'].replace(parentValueMap,'')
            else :
                parentValueMap = ''
            
            if (k == 'IndicatorType') :
                # Keep passing the IndicatorType forward with the data. This is somewhat messy, but that way we can use it on write
                DataRow[k] = v
            elif ('groupedFields' in v) :
                if ('valuemap' in v) :
                    DataRow[v['valuemap']] = []
                    for group in v['groupedFields'] :
                        DataRow[v['valuemap']].append(self._BuildXMLDictRow(group, parentValueMap=parentValueMap+v['valuemap']+';'))
            elif ('Value' in v) :
                if ('valuemap' in v) :
                    if (v['valuemap'] != '') :
                        DataRow[v['valuemap']] = v['Value']
                    else :
                        return v['Value']
            else :
                self.logging.warning("Field %s does not contain a Value entry", k)
        
        try :
            return SchemaParser.UnflattenDict(DataRow)
        except Exception as e:
            self.logging.error('Could not processes %s', DataRow)
            raise e 

    @classmethod
    def etree_to_dict(cls, t):
        '''
        Based on code from http://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
        '''
        t.tag = re.sub('^\{[^\}]+\}','',t.tag) # Strip name spaces from tags
        
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(XMLParser.etree_to_dict, children):
                for k, v in iter(dc.items()):
                    dd[k].append(v)
            d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in iter(dd.items())}}
        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d
    
    @classmethod
    def dict_to_etree(csl, d):
        '''
        Based on code from http://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
        '''
        basestring = str
        def _to_etree(d, root):
            if not d:
                pass
            elif isinstance(d, basestring):
                root.text = d
            elif isinstance(d, list):
                for i in d :
                    _to_etree(i, node)
            elif isinstance(d, dict):
                for k,v in d.items():
                    assert isinstance(k, basestring)
                    if k.startswith('#'):
                        assert k == '#text' and isinstance(v, basestring)
                        root.text = v
                    elif k.startswith('@'):
                        assert isinstance(v, basestring)
                        root.set(k[1:], v)
                    elif isinstance(v, list):
                        n = etree.SubElement(root, k)
                        for e in v:
                            _to_etree(e, n)
                    else:
                        _to_etree(v, etree.SubElement(root, k))
            else: assert d == 'invalid type'
        assert isinstance(d, dict) and len(d) == 1
        tag, body = next(iter(d.items()))
        node = etree.Element(tag)
        _to_etree(body, node)
        return node
    
    @classmethod
    def AttributeToKey(cls, AttributeName, ValueName, Data):
        '''
        Convert array of xml entries from the etree_to_dict function where the key name is the value of an attribute,
        and the real value is the value of another attribute or #text
        '''
        results = {}
        
        if (isinstance(Data,dict)) :
            # Data is expected to be a list
            Data = [Data]
        
        for row in iter(Data) :
            if (AttributeName in row and ValueName in row) :
                results[row[AttributeName]] = row[ValueName]
            
        return results
    
    @classmethod
    def KeyToAttribute(cls, AttributeName, ValueName, Data):
        '''
        Reverse the changes made by AttributeToKey method
        '''
        results = []
        
        for key, value in Data.items() :
                row = {}
                row[AttributeName] = key
                row[ValueName] = value
                results.append(row)
            
        return results
    
    
