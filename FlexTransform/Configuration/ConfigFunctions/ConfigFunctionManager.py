"""
Created on Jun 13, 2016

@author: cstrastburg
"""

import inspect
import logging
from collections import defaultdict

import FlexTransform.Configuration.ConfigFunctions


class ConfigFunctionManager(object):
    '''
    classdocs
    '''

    __KnownFunctions = defaultdict(dict)

    def __init__(self, trace, trace_list=[]):
        """
        Constructor
        :param trace_list: list of elements to trace
        :return:
        """
        self.logging = logging.getLogger('FlexTransform.Configuration.ConfigFunctions.ConfigFunctionManager')
        
        self._FunctionClasses = {}
        self.trace = trace
        self.trace_list = trace_list
        self.trace_index = {}
        if self.trace:
            for x in self.trace_list:
                for v in x["src_fields"]:
                    self.trace_index[v] = x
                for y in x["dst_fields"]:
                    self.trace_index[y] = x
                for w in x["src_IRIs"]:
                    self.trace_index[w] = x
                for z in x["dst_IRIs"]:
                    self.trace_index[z] = x
            self.logging.debug("Initialized ConfigFunctionManager with trace_list of {} elements".format(len(trace_list)))
                
    @classmethod
    def register_function(cls, function_name, required_args, function_class):
        cls.__KnownFunctions[function_name] = {
            'class': function_class,
            'RequiredArgs': required_args
        }
        
    @classmethod
    def get_function_class(cls, function_name):
        if function_name in cls.__KnownFunctions:
            class_name = cls.__KnownFunctions[function_name]['class']
        else:
            raise Exception('FunctionNotRegistered',
                            "The function %s is not registered with the ConfigFunctionManager" % function_name)
        
        for name, obj in inspect.getmembers(FlexTransform.Configuration.ConfigFunctions, inspect.isclass):
            if name == class_name:
                return obj()
            
        raise Exception('FunctionClassNotFound',
                        "The Class %s for function %s was not found by the ConfigFunctionManager" % (class_name, function_name))
       
    def get_function(self, function_name):
        if function_name in self.__KnownFunctions:
            return True
        else:
            return False

    def execute_config_function(self, function_name, args):
        if function_name in self._FunctionClasses:
            function_class = self._FunctionClasses[function_name]
        else:
            function_class = ConfigFunctionManager.get_function_class(function_name)
            self._FunctionClasses[function_name] = function_class
            
        self._validate_args(function_name, args)
        return function_class.Execute(function_name, args)
    
    def _validate_args(self, function_name, args):
        """
        Allowed fields for the Args dictionary:
        
        functionArg     - Optional - Any arguments passed to the function when it is called from SchemaParser. 
                          This is the value of the string between the () in the function name in the .json schema configuration files
                        
        fieldName       - Optional - The name of the field being processed

        fileName        - Optional - The full path of the source file

        fieldDict       - Optional - The dictionary associated with this field
    
        """
        allowed_fields = set(['functionArg', 'fileName', 'fieldName', 'fieldDict'])
        RequiredFields = set([])
        
        if isinstance(args, dict):
            for arg in args:
                if arg not in allowed_fields:
                    self.logging.warning('A argument passed to function %s is not allowed: %s' % (function_name, arg))
        else:
            raise Exception('InvalidArgs',
                            'The arguments passed to function %s are not defined or not in dictionary format' % function_name)

        if self.__KnownFunctions[function_name]['RequiredArgs'] is not None:
            RequiredFields.update(self.__KnownFunctions[function_name]['RequiredArgs'])
        
        for arg in RequiredFields:
            if arg not in args or args[arg] is None:
                raise Exception('InvalidArgs',
                                'Function %s args did not include the required %s field, could not process' % (function_name, arg))
