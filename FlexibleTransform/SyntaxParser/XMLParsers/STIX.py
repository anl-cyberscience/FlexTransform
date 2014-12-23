'''
Created on Nov 3, 2014

@author: ahoying
'''

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

# from pprint import pprint
import ramrod  # @UnresolvedImport
from stix.core import STIXPackage  # @UnresolvedImport
from stix.utils.parser import UnsupportedVersionError  # @UnresolvedImport

class STIX(object):
    '''
    Parser for STIX XML documents
    
    Upgrades STIX documents version 1.0 through 1.1 to the latest version, 1.1.1, using the ramrod module before parsing
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
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
            if (not isinstance(stixfile, str)) :
                stixfile.close()
                updated  = ramrod.update(stixfile.name, force=True)
            else :
                updated  = ramrod.update(stixfile, force=True)
            document = updated.document.as_stringio()
            stix_package  = STIXPackage.from_xml(document)
            
        stix_dict = stix_package.to_dict() # parse to dictionary
        # pprint(stix_dict)
                        
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
                    continue
                
                newrow = copy.deepcopy(row)
                
                self._ValidateURIType(newrow)
                newrows = self._ExtractRelatedObjects(newrow)
                
                ParsedData['IndicatorData'].append(newrow)
                
                if (newrows.__len__() > 0) :
                    stix_dict['indicators'].extend(newrows)

        return ParsedData

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
                        # TODO: Throw a warning when value is changed
                        row['observable']['object']['properties']['type'] = "Domain Name"
    
    def _ExtractRelatedObjects(self, row):
        '''
        Takes a collection of related objects and creates new top level indicators for each of them
        
        Adds the original object ID to a new field called related id and then sets the object id to originalid:<related indicator number>
        '''
        
        newrows = []
        
        if ('observable' in row and 'object' in row['observable'] and 'related_objects' in row['observable']['object']) :
            
            # Remove the related_objects list from the original row
            related_objects = row['observable']['object'].pop('related_objects')
            
            # x = 1            
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
                    
                    # Rename id to relatedid
                    # oldid = newrow.pop('id')
                    # newrow['relatedid'] = oldid
                    # newrow['id'] = oldid + ":" + str(x)
                    # x+=1
                    
                    newrow['observable']['object'] = related
                    
                    newrows.append(newrow)
                    
                else :
                    print('Unknown relationship type: ' + str(related), file=sys.stderr)
                    
        return newrows
        