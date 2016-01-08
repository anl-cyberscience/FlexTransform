'''
Created on Mar 13, 2015

@author: ahoying
'''

from collections import defaultdict
import logging
import inspect

import FlexTransform.SchemaParser.TransformFunctions

class TransformFunctionManager(object):
    '''
    classdocs
    '''

    __KnownFunctions = defaultdict(dict)

    def __init__(self):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.SchemaParser.TransformFunctionManager')
        
        self._FunctionClasses = {}
                
    @classmethod
    def RegisterFunction(cls, Scope, FunctionName, RequiredArgs, FunctionClass):
        '''
        '''
        cls.__KnownFunctions[Scope][FunctionName] = {
                                                     'class': FunctionClass,
                                                     'RequiredArgs': RequiredArgs
                                                    }
        
    @classmethod
    def GetFunctionClass(cls, Scope, FunctionName):
        '''
        '''
        if (Scope in cls.__KnownFunctions and FunctionName in cls.__KnownFunctions[Scope]) :
            ClassName = cls.__KnownFunctions[Scope][FunctionName]['class']
        else :
            raise Exception('FunctionNotRegistered', "The function %s is not registered with the TransformFunctionManager for scope %s" % (FunctionName, Scope))
        
        for name, obj in inspect.getmembers(FlexTransform.SchemaParser.TransformFunctions, inspect.isclass) :
            if (name == ClassName) :
                return obj();
            
        raise Exception('FunctionClassNotFound', "The Class %s for function %s was not found by the TransformFunctionManager" % (ClassName, FunctionName))
    
    def GetFunctionScope(self, Scope, FunctionName):
        '''
        '''
        if (Scope in self.__KnownFunctions and FunctionName in self.__KnownFunctions[Scope]):
            return True
        else :
            return False
    
    def ExecuteTransformFunction(self, Scope, FunctionName, args):
        '''
        '''
        
        FunctionClass = None
        if (FunctionName in self._FunctionClasses) :
            FunctionClass = self._FunctionClasses[FunctionName]
        else :
            FunctionClass = TransformFunctionManager.GetFunctionClass(Scope, FunctionName)
            self._FunctionClasses[FunctionName] = FunctionClass
            
        self._ValidateArgs(Scope, FunctionName, args)
        return FunctionClass.Execute(Scope, FunctionName, args)
    
    def _ValidateArgs(self, Scope, FunctionName, args):
        '''
        Allowed fields for the Args dictionary:
        
        functionArg     - Optional - Any arguments passed to the function when it is called from SchemaParser. 
                          This is the value of the string between the () in the function name in the .json schema configuration files
                        
        fieldName       - Required - The name of the current field
        
        fieldDict       - Required - The field dictionary for the current field getting transformed
        
        currentRow      - Optional - The transformed data and associated field dictionaries for the currently processed row
    
        indicatorType   - Optional - The indicator type for the current row
            
        transformedData - Optional - The dictionary of all current transformed data
    
        '''
        AllowedFields = set(['functionArg', 'fieldName', 'fieldDict', 'currentRow', 'indicatorType', 'transformedData'])
        RequiredFields = set(['fieldName', 'fieldDict'])
        
        if (isinstance(args, dict)) :
            for arg in args :
                if (arg not in AllowedFields) :
                    self.logging.warning('A argument passed to function %s is not allowed: %s' % (FunctionName, arg))
        else :
            raise Exception('InvalidArgs','The arguments passed to function %s are not defined or not in dictionary format' % FunctionName)
                    
        
        if (self.__KnownFunctions[Scope][FunctionName]['RequiredArgs'] is not None) :
            RequiredFields.update(self.__KnownFunctions[Scope][FunctionName]['RequiredArgs'])
        
        for arg in RequiredFields :
            if (arg not in args or args[arg] is None) :
                raise Exception('InvalidArgs', 'Function %s args did not include the required %s field, could not process' % (FunctionName, arg))
