'''
Created on Mar 13, 2015

@author: ahoying
'''

import logging

import arrow

from FlexTransform.SchemaParser.TransformFunctions import TransformFunctionManager


class STIXFunctions(object):
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
        'DocumentHeaderData': {
            'stix_now': ['fieldDict']
        },
        'IndicatorData': {
            'stix_now': ['fieldDict']
        }
    }

    def __init__(self):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.SchemaParser.STIXFunctions')
        
    @classmethod
    def RegisterFunctions(cls):
        for Scope, Functions in cls.__FunctionNames.items() :
            for FunctionName, RequiredArgs in Functions.items() :
                TransformFunctionManager.RegisterFunction(Scope, FunctionName, RequiredArgs, 'STIXFunctions')
        
    def Execute(self, Scope, function_name, args):
        '''
        Execute the specific called function with the supplied args
        '''
        
        value = None
         
        if function_name not in self.__FunctionNames[Scope] :
            raise Exception('FunctionNotDefined',
                            'Function %s is not defined in STIXFunctions for document scope %s' % (function_name, Scope))
        if function_name == 'stix_now':
            if 'dateTimeFormat' in args['fieldDict']:
                value = arrow.utcnow().format(args['fieldDict']['dateTimeFormat'])
                # self.logging.info("Called stix now")
                # match = re.match(r"(.*)([+-]\d\d)(\d\d)$", value)
                # if match:
                #     value = match.group(1) + match.group(2) + ":" + match.group(3)
        return value
