'''
Created on Mar 13, 2015

@author: ahoying
'''

import inspect
import logging
from collections import defaultdict

import FlexTransform.SchemaParser.TransformFunctions


class TransformFunctionManager(object):

    __KnownFunctions = defaultdict(dict)

    def __init__(self, trace, trace_list=[]):
        self.logging = logging.getLogger('FlexTransform.SchemaParser.TransformFunctionManager')
        self.trace = trace
        self.trace_list = trace_list
        if self.trace:
            self.logging.debug("Initialized DictionaryParser with tracelist of {} elements.".format(len(trace_list)))
        
        self._FunctionClasses = {}
                
    @classmethod
    def register_function(cls, scope, function_name, required_args, function_class):
        cls.__KnownFunctions[scope][function_name] = {'class': function_class, 'RequiredArgs': required_args}
        
    @classmethod
    def get_function_class(cls, scope, function_name):
        if scope in cls.__KnownFunctions and function_name in cls.__KnownFunctions[scope]:
            class_name = cls.__KnownFunctions[scope][function_name]['class']
        else:
            raise Exception(
                'FunctionNotRegistered',
                "The function %s is not registered with the TransformFunctionManager for scope %s" % (function_name,
                                                                                                      scope))
        
        for name, obj in inspect.getmembers(FlexTransform.SchemaParser.TransformFunctions, inspect.isclass):
            if name == class_name:
                return obj();
            
        raise Exception(
            'FunctionClassNotFound',
            "The Class %s for function %s was not found by the TransformFunctionManager" % (class_name, function_name))
    
    def get_function_scope(self, scope, function_name):
        if scope in self.__KnownFunctions and function_name in self.__KnownFunctions[scope]:
            return True
        else:
            return False
    
    def execute_transform_function(self, scope, function_name, args):
        if function_name in self._FunctionClasses:
            function_class = self._FunctionClasses[function_name]
        else:
            function_class = TransformFunctionManager.get_function_class(scope, function_name)
            self._FunctionClasses[function_name] = function_class
            
        self._validate_args(scope, function_name, args)
        return function_class.Execute(scope, function_name, args)
    
    def _validate_args(self, scope, function_name, args):
        '''
        Allowed fields for the Args dictionary:
        
        functionArg     - Optional - Any arguments passed to the function when it is called from SchemaParser. 
                          This is the value of the string between the () in the function name in the
                          .json schema configuration files
                        
        fieldName       - Required - The name of the current field
        
        fieldDict       - Required - The field dictionary for the current field getting transformed
        
        currentRow      - Optional - The transformed data and associated field dictionaries for the currently processed row
    
        indicatorType   - Optional - The indicator type for the current row
            
        transformedData - Optional - The dictionary of all current transformed data
        
        '''
        allowed_fields =set(['functionArg', 'fieldName', 'fieldDict', 'currentRow', 'indicatorType', 'transformedData'])
        required_fields =set(['fieldName', 'fieldDict'])
        
        if isinstance(args, dict):
            for arg in args:
                if arg not in allowed_fields:
                    self.logging.warning('A argument passed to function %s is not allowed: %s' % (function_name, arg))
        else:
            raise Exception(
                'InvalidArgs',
                'The arguments passed to function %s are not defined or not in dictionary format' % function_name)

        if self.__KnownFunctions[scope][function_name]['RequiredArgs'] is not None:
            required_fields.update(self.__KnownFunctions[scope][function_name]['RequiredArgs'])
        
        for arg in required_fields:
            if arg not in args or args[arg] is None:
                raise Exception(
                    'InvalidArgs',
                    'Function %s args did not include the required %s field, could not process' % (function_name, arg))
