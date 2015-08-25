'''
Created on Jul 31, 2014

@author: ahoying
'''

from lxml import etree
import FlexTransform.SyntaxParser
import logging
from FlexTransform.SchemaParser.TransformFunctions import CFM13Functions

class CFM13(object):
    '''
    Parser for CFM version 1.3 XML documents
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.AdditionalDataTypes = {
                                        'report start time': 'date-time',
                                        'report type': 'string',
                                        'report schedule': 'string',
                                        'number of alerts in this report': 'integer',
                                        'prior offenses': 'integer',
                                        'alert threshold': 'integer',
                                        'duration': 'integer',
                                        'recon': 'integer',
                                        'restriction': 'string',
                                        'OUO': 'integer',
                                        'top level domain owner': 'string',
                                        'alert provenance': 'string'
                                    }
        
        self.logging = logging.getLogger('FlexTransform.XMLParser.CFM13')
        
        CFM13Functions.RegisterFunctions()
    
    def Read(self, cfm13file, xmlparser = None):
        '''
        Parse CFM13 XML document. Return a dictionary object with the data from the document.
        '''
        
        root = None
        if (xmlparser is not None) :
            # Validate file against the schema when it is loaded
            tree = etree.parse(cfm13file, xmlparser)
            root = tree.getroot()
        else :
            tree = etree.parse(cfm13file)
            root = tree.getroot()
        
        ParsedData = {};
        
        ParsedData['IndicatorData'] = [];
        
        AlertNode = '{http://www.anl.gov/cfm/1.3/IDMEF-Message}Alert'
        AnalyzerNode = '{http://www.anl.gov/cfm/1.3/IDMEF-Message}Analyzer'
        
        # Check if document has the name space configured, if not remove the NS from the tag names before parsing the tree
        if (root.find(AlertNode) is None) :
            AlertNode = 'Alert'
            AnalyzerNode = 'Analyzer'
            
        for element in root.iterchildren(AlertNode) :
            if (element.find(AnalyzerNode) is not None) :
                # CFM 1.3 Header data
                DocumentHeaderData = FlexTransform.SyntaxParser.XMLParser.etree_to_dict(element)
                if ('AdditionalData' in DocumentHeaderData['Alert']):
                    DocumentHeaderData['Alert']['AdditionalData'] = FlexTransform.SyntaxParser.XMLParser.AttributeToKey('@meaning','#text',DocumentHeaderData['Alert']['AdditionalData'])
                
                ParsedData['DocumentHeaderData'] = DocumentHeaderData['Alert']
            else :
                # CFM 1.3 Indicator data
                IndicatorData = FlexTransform.SyntaxParser.XMLParser.etree_to_dict(element)
                if ('AdditionalData' in IndicatorData['Alert']):
                    IndicatorData['Alert']['AdditionalData'] = FlexTransform.SyntaxParser.XMLParser.AttributeToKey('@meaning','#text',IndicatorData['Alert']['AdditionalData'])
                    
                if ('Target' in IndicatorData['Alert'] and 'Service' in IndicatorData['Alert']['Target'] and 'portlist' in IndicatorData['Alert']['Target']['Service']) :
                    portlist = IndicatorData['Alert']['Target']['Service'].pop('portlist')
                    IndicatorData['Alert']['Target']['Service']['port'] = portlist.split(',')
                    
                    if ('protocol' in IndicatorData['Alert']['Target']['Service']) :
                        protocol = IndicatorData['Alert']['Target']['Service'].pop('protocol')
                        IndicatorData['Alert']['Target']['Service']['protocol'] = []
                        for port in IndicatorData['Alert']['Target']['Service']['port'] :
                            IndicatorData['Alert']['Target']['Service']['protocol'].append(protocol)
                
                ParsedData['IndicatorData'].append(IndicatorData['Alert'])
                
        return ParsedData
    
    def Write(self, cfm13file, ParsedData):
        '''
        Take the transformed data and write it out to a new CFM version 1.3 XML file
        '''        
        Alerts = []
        
        # OrderedLists and SubLists are used to force dictionary data into the correct output order for CFM Message 1.3 Schema validation
        
        if ('AdditionalData' in ParsedData['DocumentHeaderData']):
            ParsedData['DocumentHeaderData']['AdditionalData'] = FlexTransform.SyntaxParser.XMLParser.KeyToAttribute('@meaning','#text',ParsedData['DocumentHeaderData']['AdditionalData'])
            ParsedData['DocumentHeaderData']['AdditionalData'] = self._AddAdditionalDataType(ParsedData['DocumentHeaderData']['AdditionalData'])
            
            # This reformats AdditionalData so that dict_to_xml outputs multiple rows with the same element name
            SubList = []
            for ad in ParsedData['DocumentHeaderData']['AdditionalData'] :
                SubList.append({'AdditionalData': ad})
                
            ParsedData['DocumentHeaderData']['AdditionalData'] = SubList
            
        OrderedList = [];
        
        if ('Node' in ParsedData['DocumentHeaderData']['Analyzer']) :
            SubList = []
            SubList.append({'location': ParsedData['DocumentHeaderData']['Analyzer']['Node']['location']})
            SubList.append({'name': ParsedData['DocumentHeaderData']['Analyzer']['Node']['name']})
            ParsedData['DocumentHeaderData']['Analyzer']['Node'] = SubList
        
        OrderedList.append({'Analyzer': ParsedData['DocumentHeaderData']['Analyzer']})
        OrderedList.append({'AnalyzerTime': ParsedData['DocumentHeaderData']['AnalyzerTime']})
        OrderedList.extend(ParsedData['DocumentHeaderData']['AdditionalData'])
        
        Alerts.append(OrderedList)
        
        for row in ParsedData['IndicatorData'] :
            if ('IndicatorType' in row) :
                # Add special text indicator to DNS block classification per CFM 1.3 schema
                if (row['IndicatorType'] == 'DNS-Hostname-Block') :
                    if ('@text' in row['Classification'] and not row['Classification']['@text'].startswith('Domain Block:')) :
                        row['Classification']['@text'] = "Domain Block: %s" % row['Classification']['@text']
                    elif ('@text' not in row['Classification']) :
                        row['Classification']['@text'] = "Domain Block: blocked"
                elif (row['IndicatorType'] == 'URL-Block') :
                    if ('@text' in row['Classification'] and not row['Classification']['@text'].startswith('URL Block:')) :
                        row['Classification']['@text'] = "URL Block: %s" % row['Classification']['@text']
                    elif ('@text' not in row['Classification']) :
                        row['Classification']['@text'] = "URL Block: blocked"

            if ('AdditionalData' in row):
                row['AdditionalData'] = FlexTransform.SyntaxParser.XMLParser.KeyToAttribute('@meaning','#text',row['AdditionalData'])
                row['AdditionalData'] = self._AddAdditionalDataType(row['AdditionalData'])
                
                # This reformats AdditionalData so that dict_to_xml outputs multiple rows with the same element name
                SubList = []
                for ad in row['AdditionalData'] :
                    SubList.append({'AdditionalData': ad})
                    
                row['AdditionalData'] = SubList
                
            OrderedList = [];
            
            if ('CreateTime' not in row) :
                row['CreateTime'] = ParsedData['DocumentHeaderData']['AnalyzerTime']
                
            OrderedList.append({'CreateTime': row['CreateTime']})
            
            if ('name' in row['Source']['Node']) :
                SubList = []
                # Always add attribute category = dns to the Node if there is a dns name entry
                SubList.append({'name': row['Source']['Node']['name'], '@category' : 'dns'})
                if ('Address' in row['Source']['Node']) :
                    SubList.append({'Address': row['Source']['Node']['Address']})
                row['Source']['Node'] = SubList
            OrderedList.append({'Source': row['Source']})
            
            if ('Target' in row) :
                SubList = []
                if ('port' in row['Target']['Service']) :
                    SubList.append({'port': row['Target']['Service']['port']})
                elif ('Portlist' in row['Target']['Service']) :
                    SubList.append({'Portlist': row['Target']['Service']['Portlist']})
                if ('protocol' in row['Target']['Service']) :
                    SubList.append({'protocol': row['Target']['Service']['protocol']})
                row['Target']['Service'] = SubList
                OrderedList.append({'Target': row['Target']})
                
            if ('Reference' in row['Classification']) :
                # TODO: Technically multiple references can exist for a single Indicator, this code only supports a single reference
                SubList = []
                SubList.append({'@meaning': row['Classification']['Reference']['@meaning']})
                SubList.append({'@origin': row['Classification']['Reference']['@origin']})
                SubList.append({'name': row['Classification']['Reference']['name']})
                SubList.append({'url': row['Classification']['Reference']['url']})
                row['Classification']['Reference'] = SubList
                
            OrderedList.append({'Classification': row['Classification']})
            OrderedList.append({'Assessment': row['Assessment']})
            
            OrderedList.extend(row['AdditionalData'])
                            
            Alerts.append(OrderedList)
        
        # Name space mapping for CFM 1.3 XML documents
        CFM13_URI = "http://www.anl.gov/cfm/1.3/IDMEF-Message"
        CFM13_NS = '{%s}' % CFM13_URI
        
        XSI_URI = "http://www.w3.org/2001/XMLSchema-instance"
        XSI_NS = '{%s}' % XSI_URI
        
        NS_MAP = {None: CFM13_URI,'xsi': XSI_URI}
        
        CFM13Root = etree.Element(CFM13_NS+'IDMEF-Message', nsmap=NS_MAP)
        CFM13Root.set(XSI_NS+'schemaLocation', "http://www.anl.gov/cfm/1.3/IDMEF-Message/../../../resources/schemas/CFMMessage13.xsd")
        
        # Parse the alert dictionaries back into XML Element trees and append to the root element
        for alert in Alerts :
            CFM13Alert = FlexTransform.SyntaxParser.XMLParser.dict_to_etree({'Alert': alert})
            CFM13Root.append(CFM13Alert)
                
        cfm13file.write(etree.tostring(CFM13Root, 
                                       pretty_print=True, 
                                       xml_declaration=True, 
                                       encoding='UTF-8', 
                                       doctype='<!DOCTYPE IDMEF-Message PUBLIC "-//IETF//DTD RFC XXXX IDMEF v1.0//EN" "idmef-message.dtd">'
                                       ).decode(encoding='UTF-8'))
        # cfm13file.close()
        
        
    def _AddAdditionalDataType(self, rows):
        '''
        Add the correct type attribute for AdditionalData rows
        '''
        for row in rows :
            if ('@meaning' in row) :
                if (row['@meaning'] in self.AdditionalDataTypes) :
                    row['@type'] = self.AdditionalDataTypes[row['@meaning']]
                else :
                    self.logging.warning("Unknown AdditionalData Meaning, no type mapping exists: %s", row['@meaning'])
                    
        return rows