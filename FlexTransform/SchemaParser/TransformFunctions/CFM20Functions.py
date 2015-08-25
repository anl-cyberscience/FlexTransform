'''
Created on Mar 13, 2015

@author: ahoying
'''

import re
import logging

from FlexTransform.SchemaParser.TransformFunctions import TransformFunctionManager

class CFM20Functions(object):
    '''
    Contains Transform functions that multiple schemas utilize
    '''

    '''
    The _FunctionNames dictionary should contain each function name understood by this class for with a scope of indicator data or header data
    mapped to a list with required fields to be passed in the args dictionary, or None if no args are required.
    
    Allowed fields for the Args dictionary:
    
    functionArg     - Optional - Any arguments passed to the function when it is called from SchemaParser. 
                      This is the value of the string between the () in the function name in the .json schema configuration files
                    
    fieldName       - Required - The name of the current field
    
    fieldDict       - Required - The field dictionary for the current field getting transformed
    
    currentRow      - Optional - The transformed data and associated field dictionaries for the currently processed row

    indicatorType   - Optional - The indicator type for the current row
        
    transformedData - Optional - The dictionary of all current transformed data

    '''
    
    __FunctionNames = {
                       'IndicatorData': {
                                         'CFM20_determineIndicatorConstraint': ['functionArg', 'currentRow']
                                        }
                      }

    def __init__(self):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.SchemaParser.CFM20Functions')
        
    @classmethod
    def RegisterFunctions(cls):
        for Scope, Functions in cls.__FunctionNames.items() :
            for FunctionName, RequiredArgs in Functions.items() :
                TransformFunctionManager.RegisterFunction(Scope, FunctionName, RequiredArgs, 'CFM20Functions')
        
    def Execute(self, Scope, FunctionName, args):
        '''
        Execute the specific called function with the supplied args
        '''
        
        Value = None
         
        if (FunctionName not in self.__FunctionNames[Scope]) :
            raise Exception('FunctionNotDefined','Function %s is not defined in CFM20Functions for document scope %s' % (FunctionName, Scope))
        
        if (FunctionName == 'CFM20_determineIndicatorConstraint') :
            # TODO: It would be great if somehow we could query the ontology to get this. Complete for all indicator constraints.
            
            if (args['functionArg'] in args['currentRow'] and 'Value' in args['currentRow'][args['functionArg']]) :
                indicatorValue = args['currentRow'][args['functionArg']]['Value']
                indicatorOntology = args['currentRow'][args['functionArg']]['matchedOntology']
                
                if (indicatorOntology == 'http://www.anl.gov/cfm/transform.owl#FilenameIndicatorValueSemanticConcept') :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#StringValueMatch'
                elif (re.match(r'^((\d){1,3}\.){3}(\d){1,3}$', indicatorValue)) :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#IPv4DottedDecimalEquality'
                elif (re.match(r'^[a-fA-F0-9]+:+[a-fA-F0-9:]+$', indicatorValue)) :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#IPv6ColonHexEquality'
                elif (re.match(r'^([a-z0-9][^./]+\.)+[a-z]+$', indicatorValue)) :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#DNSDomainNameMatch'
                elif (re.match(r'^((ft|htt)ps?://)?([a-z][^./]+\.)+[a-z]+/.*$', indicatorValue)) :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#URLMatch'
                elif (re.match(r'^[a-fA-F0-9]{32}$', indicatorValue)) :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#MD5Equality'
                elif (re.match(r'^[a-fA-F0-9]{40}$', indicatorValue)) :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#SHA1Equality'
                elif (re.match(r'^\d+$', indicatorValue)) :
                    Value = 'http://www.anl.gov/cfm/2.0/current/#IntegerEquality'

            if (Value is None) :
                # Still didn't find an indicator type, throw exception
                raise Exception('unknownIndicatorConstraint', 'CFM 2.0 Indicator constraint could not be determined for data: %s :: field %s' % (args['currentRow'][args['functionArg']]['Value'], indicatorOntology))
            
        return Value