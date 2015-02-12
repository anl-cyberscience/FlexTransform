'''
Created on Nov 3, 2014

@author: ahoying
'''

import logging
import sys
import os
import re
import copy

currentdir = os.path.dirname(__file__)
            
# Import custom versions of the cybox, stix and ramrod python modules for use with FlexTransform
# These versions have been updated to work with Python 3 and have a bug fixes for specific issues that were uncovered during testing
sys.path.insert(0,os.path.join(currentdir,"../../resources/cybox.zip"))
sys.path.insert(1,os.path.join(currentdir,"../../resources/stix.zip"))
sys.path.insert(2,os.path.join(currentdir,"../../resources/ramrod.zip"))

import ramrod  # @UnresolvedImport
from stix.core import STIXPackage  # @UnresolvedImport
from stix.utils import set_id_namespace # @UnresolvedImport
from stix.utils.parser import UnsupportedVersionError  # @UnresolvedImport
from stix.utils.idgen import IDGenerator # @UnresolvedImport

class STIX(object):
    '''
    Parser for STIX XML documents
    
    Upgrades STIX documents version 1.0 through 1.1 to the latest version, 1.1.1, using the ramrod module before parsing
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.logging = logging.getLogger('FlexTransform/XMLParser/STIX')
        self.STIXNamespace = "http://www.example.com"
        self.STIXAlias = "example"
        self.STIXReplaceNamespace = False
        
    def ValidateConfig(self,config):
        '''
        Load custom configuration
        '''
        
        if (config.has_section('STIX')) :
            if (config.has_option('STIX', 'STIXNamespace')) :
                self.STIXNamespace = config['STIX']['STIXNamespace']
            if (config.has_option('STIX', 'STIXAlias')) :
                self.STIXAlias = config['STIX']['STIXAlias']
            if (config.has_option('STIX', 'STIXReplaceNamespace')) :
                self.STIXReplaceNamespace = config.getboolean('STIX', 'STIXReplaceNamespace', fallback=False)
        
    def Read(self, stixfile, xmlparser = None):
        '''
        Parse STIX XML document. Return a dictionary object with the data from the document.
        '''
        
        # FIXME: Handle composite indicators and related indicators hierarchically
        
        # FIXME: Handle STIX indicators with multiple possible values where the apply_condition is ANY
        
        
        # Upgrade old versions of STIX documents to the latest supported release (currently 1.1.1)
        try:
            stix_package = STIXPackage.from_xml(stixfile)
        except UnsupportedVersionError:
            updated = None
            self.logging.warning("Updating stix document to version 1.1.1")
            if (not isinstance(stixfile, str)) :
                stixfile.close()
                updated  = ramrod.update(stixfile.name, force=True)
            else :
                updated  = ramrod.update(stixfile, force=True)
            document = updated.document.as_stringio()
            stix_package  = STIXPackage.from_xml(document)
            
        stix_dict = stix_package.to_dict() # parse to dictionary
                        
        ParsedData = {};
        
        if ('stix_header' in stix_dict) :
            ParsedData['DocumentHeaderData'] = copy.deepcopy(stix_dict['stix_header'])
        else :
            ParsedData['DocumentHeaderData'] = {}
            
        if ('id' in stix_dict) :
            ParsedData['DocumentHeaderData']['id'] = stix_dict['id']
            
        if  ('version' in stix_dict) :
            ParsedData['DocumentHeaderData']['version'] = stix_dict['version']
            
        if ('indicators' in stix_dict) :
            ParsedData['IndicatorData'] = []
            
            for row in stix_dict['indicators'] :
                # Transform lists in indicators into usable data
                if ('observable' not in row) :
                    self.logging.info('Indicator has no observable, skipping: %s', row)
                    continue
                
                newrow = copy.deepcopy(row)
                
                self._ValidateURIType(newrow)
                newrows = self._ExtractRelatedObjects(newrow)
                
                ParsedData['IndicatorData'].append(newrow)
                
                if (newrows.__len__() > 0) :
                    stix_dict['indicators'].extend(newrows)

        return ParsedData
    
    def Write(self, stixfile, ParsedData):
        '''
        Take the transformed data and write it out to a new STIX XML file
        '''
        
        NAMESPACE = {self.STIXNamespace : self.STIXAlias}
        set_id_namespace(NAMESPACE) # new ids will be prefixed by STIXAlias + ":"
        
        self._AddObjectIDs(ParsedData)
        
        stix_package = STIXPackage.from_dict({'id': ParsedData['DocumentHeaderData'].pop('id'),
                                              'version': ParsedData['DocumentHeaderData'].pop('version'),
                                              'timestamp': ParsedData['DocumentHeaderData'].pop('timestamp'),
                                              'stix_header': ParsedData['DocumentHeaderData'],
                                              'indicators': ParsedData['IndicatorData']})
        
        
        stixfile.write(stix_package.to_xml())
        stixfile.close()

    def _ValidateURIType(self, row):
        '''
        Validate that the object type for a URL block is really a URL or a domain name
        
        A lot of data is reported as a URL that is really a domain which messes up the Indicator Type detection and the transformation
        '''
        
        if ('observable' in row and 'object' in row['observable'] and 'properties' in row['observable']['object'] and 'type' in row['observable']['object']['properties']) :
            if (row['observable']['object']['properties']['type'] == "URL") :
                if ('value' in row['observable']['object']['properties'] and 'value' in row['observable']['object']['properties']['value']) :
                    urlvalue = row['observable']['object']['properties']['value']['value']
                    
                    # very simple match to see if there are any /'s in the value. If not it is assumed to be a domain
                    # TODO: use a better regular express here to match a URL or a domain
                    if (re.match(r'.*/', urlvalue) is None) :
                        self.logging.warning('Indicator type changed from URL to Domain Name for indicator %s', urlvalue)
                        row['observable']['object']['properties']['type'] = "Domain Name"
    
    def _ExtractRelatedObjects(self, row):
        '''
        Takes a collection of related objects and creates new top level indicators for each of them
        '''
        
        newrows = []
        
        if ('observable' in row and 'object' in row['observable'] and 'related_objects' in row['observable']['object']) :
            
            # Remove the related_objects list from the original row
            related_objects = row['observable']['object'].pop('related_objects')
                      
            for related in related_objects :
                if ('relationship' in related and ( related['relationship'] == 'Contains' or related['relationship'] == 'Connected_To' ) ) :
                    
                    if ('properties' in related and 'xsi:type' in related['properties'] and related['properties']['xsi:type'] == 'HTTPSessionObjectType') :
                        # TODO: This should be handled by an AND relationship at the hierarchical level once that is implemented
                        if ('http_request_response' in related['properties']) :
                            row['observable']['object']['properties']['http_request_response'] = related['properties']['http_request_response']
                            continue
                    
                    newrow = copy.deepcopy(row)
                    
                    # Get rid of the original object
                    del newrow['observable']['object']                   
                    newrow['observable']['object'] = related
                    
                    newrows.append(newrow)
                    
                else :
                    self.logging.warning('Unknown relationship type: %s', related)
                    
        return newrows
    
    
    def _AddObjectIDs(self, ParsedData):
        '''
        Add STIX unique identifiers to objects in ParsedData
        '''
        
        if ('DocumentHeaderData' in ParsedData) :
            objid = None
            if ('id' in ParsedData['DocumentHeaderData']) :
                objid = ParsedData['DocumentHeaderData'].pop('id')

            ParsedData['DocumentHeaderData']['id'] = self._AddObjectID(objid, 'STIXPackage')
                        
        if ('IndicatorData' in ParsedData) :
            for indicator in ParsedData['IndicatorData'] :
                objid = None
                if ('id' in indicator) :
                    objid = indicator.pop('id')
    
                indicator['id'] = self._AddObjectID(objid, 'indicator')
                
                if ('observable' in indicator) :
                    objid = None
                    if ('id' in indicator['observable']) :
                        objid = indicator['observable'].pop('id')
        
                    indicator['observable']['id'] = self._AddObjectID(objid, 'observable')
                    
                    if ('object' in indicator['observable']) :
                        objid = None
                        if ('id' in indicator['observable']['object']) :
                            objid = indicator['observable']['object'].pop('id')
            
                        indicator['observable']['object']['id'] = self._AddObjectID(objid, 'object')
                        
                        if ('related_objects' in indicator['observable']['object']) :
                            for related_object in indicator['observable']['object']['related_objects'] :
                                objid = None
                                if ('id' in related_object) :
                                    objid = related_object.pop('id')
                    
                                related_object['id'] = self._AddObjectID(objid, 'object')
            
    def _AddObjectID(self, data = None, prefix = 'guid'):
        '''
        Generate a new object ID or modify an existing one
        '''
        
        idgen = IDGenerator(namespace={self.STIXNamespace: self.STIXAlias})
        objid = data
        
        if (data) :
            match = re.match(r'^([^:]+):(.*)', data)
            if (match) :
                if (match.group(1) != self.STIXAlias) :
                    objid = "%s:%s" % (self.STIXAlias, match.group(2))
            else :
                objid = "%s:%s-%s" % (self.STIXAlias, prefix, data)
        else :
            objid = idgen.create_id(prefix)
            
        return objid
                