'''
Created on Mar 13, 2015

@author: ahoying
'''

import pytz
import time
import datetime
import logging
import uuid

from FlexTransform.SchemaParser.TransformFunctions import TransformFunctionManager

class GlobalFunctions(object):
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
                                              'countOfIndicators': ['transformedData'],
                                              'now': ['fieldDict'],
                                             },
                       'IndicatorData':      {
                                              'now': ['fieldDict'],
                                              'generate_uuid': None
                                             }
                      }

    def __init__(self):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.SchemaParser.GlobalFunctions')
        
    @classmethod
    def RegisterFunctions(cls):
        for Scope, Functions in cls.__FunctionNames.items() :
            for FunctionName, RequiredArgs in Functions.items() :
                TransformFunctionManager.RegisterFunction(Scope, FunctionName, RequiredArgs, 'GlobalFunctions')
        
    def Execute(self, Scope, FunctionName, args):
        '''
        Execute the specific called function with the supplied args
        '''
        
        Value = None
         
        if (FunctionName not in self.__FunctionNames[Scope]) :
            raise Exception('FunctionNotDefined','Function %s is not defined in GlobalFunctions for document scope %s' % (FunctionName, Scope))
        
        if (FunctionName == 'now'):
            if ('dateTimeFormat' in args['fieldDict']) :
                if (args['fieldDict']['dateTimeFormat'] == 'unixtime') :
                    Value = '%i' % time.mktime(datetime.datetime.now(tz=pytz.utc).timetuple())
                else :
                    Value = datetime.datetime.now(tz=pytz.utc).strftime(args['fieldDict']['dateTimeFormat'])

            
        elif (FunctionName == 'countOfIndicators') :
            if ('IndicatorData' in args['transformedData']):
                Value = str(len(args['transformedData']['IndicatorData']))
            else :
                Value = '0'
            
        elif (FunctionName == 'generate_uuid') :
            Value = str(uuid.uuid4())
            
        return Value
        