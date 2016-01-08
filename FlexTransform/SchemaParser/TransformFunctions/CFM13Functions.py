'''
Created on Mar 13, 2015

@author: ahoying
'''

import datetime
import logging

from FlexTransform.SchemaParser.TransformFunctions import TransformFunctionManager

class CFM13Functions(object):
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
                                              
                                              'CFM13_determineTLP': ['transformedData'],
                                              'CFM13_earliestIndicatorTime': ['transformedData']
                                             },
                       'IndicatorData':      {
                                              'CFM13_GenerateRestrictionsDescription': ['currentRow'],
                                              'CFM13_SightingsCount': ['functionArg', 'currentRow']
                                             }
                      }

    def __init__(self):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.SchemaParser.CFM13Functions')
        
    @classmethod
    def RegisterFunctions(cls):
        for Scope, Functions in cls.__FunctionNames.items() :
            for FunctionName, RequiredArgs in Functions.items() :
                TransformFunctionManager.RegisterFunction(Scope, FunctionName, RequiredArgs, 'CFM13Functions')
        
    def Execute(self, Scope, FunctionName, args):
        '''
        Execute the specific called function with the supplied args
        '''
        
        Value = None
         
        if (FunctionName not in self.__FunctionNames[Scope]) :
            raise Exception('FunctionNotDefined','Function %s is not defined in CFM13Functions for document scope %s' % (FunctionName, Scope))
                   
        if (FunctionName == 'CFM13_GenerateRestrictionsDescription') :
            Value = ''
            if ('ouo' in args['currentRow'] and 'Value' in args['currentRow'] ['ouo']) :
                Value += "OUO="
                if (args['currentRow'] ['ouo']['Value'] == '1') :
                    Value += "True"
                else :
                    Value += "False"
            if ('recon' in args['currentRow'] and 'Value' in args['currentRow']['recon']) :
                if (Value != '') :
                    Value += ", "
                Value += "ReconAllowed="
                if (args['currentRow']['recon']['Value'] == '0') :
                    Value += "True"
                else :
                    Value += "False"
            if ('restriction' in args['currentRow'] and 'Value' in args['currentRow']['restriction']) :
                if (Value != '') :
                    Value += ", "
                Value += "SharingRestrictions=%s" % args['currentRow']['restriction']['Value']

        elif (FunctionName == 'CFM13_determineTLP') :
            Value = 'GREEN'
            for subrow in args['transformedData']['IndicatorData'] :
                if ('ouo' in subrow) :
                    if (subrow['ouo']['Value'] == 1) :
                        Value = 'AMBER'
                        break
                if ('restriction' in subrow) :
                    if (subrow['restriction']['Value'] == 'private') :
                        Value = 'AMBER'
                        break
            
        elif (FunctionName == 'CFM13_earliestIndicatorTime') :
            # For now this function is specific to CFM13, it could be made generic if needed in other Schemas
            mintime = None
            for subrow in args['transformedData']['IndicatorData'] :
                if ('create_time' in subrow) :
                    indicatorTime = datetime.datetime.strptime(subrow['create_time']['Value'], '%Y-%m-%dT%H:%M:%S%z')
                    if (mintime is None or mintime > indicatorTime) :
                        mintime = indicatorTime

            if (mintime is not None) :            
                Value = mintime.strftime('%Y-%m-%dT%H:%M:%S%z')
            else :
                Value = args['currentRow']['analyzer_time']['Value']
                
        elif (FunctionName == 'CFM13_SightingsCount') :
            sightings = 1
            if (args['functionArg'] in args['currentRow'] and 'Value' in args['currentRow'][args['functionArg']]) :
                sightings += int(args['currentRow'][args['functionArg']]['Value'])
                
            Value = str(sightings)
            
        return Value