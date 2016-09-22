'''
Created on Mar 13, 2015

@author: ahoying
'''

from collections import defaultdict
import logging
import inspect
import pprint

import FlexTransform.Configuration.ConfigFunctions

class ConfigFunctionManager(object):
    '''
    classdocs
    '''

    __KnownFunctions = defaultdict(dict)

    def __init__(self, tracelist=[]):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.Configuration.ConfigFunctions.ConfigFunctionManager')
        
        self._FunctionClasses = {}
        self.pprint = pprint.PrettyPrinter()
        self.tracelist = tracelist
        self.traceindex = {}
        for x in self.tracelist:
            for v in x["src_fields"]:
                self.traceindex[v] = x
            for y in x["dst_fields"]:
                self.traceindex[y] = x
            for w in x["src_IRIs"]:
                self.traceindex[w] = x
            for z in x["dst_IRIs"]:
                self.traceindex[z] = x

        self.logging.debug("Initialized ConfigFunctionManager with tracelist of {} elements".format(len(tracelist)))
                
    @classmethod
    def RegisterFunction(cls, FunctionName, RequiredArgs, FunctionClass):
        '''
        '''
        cls.__KnownFunctions[FunctionName] = {
                                                     'class': FunctionClass,
                                                     'RequiredArgs': RequiredArgs
                                                    }
        
    @classmethod
    def GetFunctionClass(cls, FunctionName):
        '''
        '''
        if (FunctionName in cls.__KnownFunctions) :
            ClassName = cls.__KnownFunctions[FunctionName]['class']
        else :
            raise Exception('FunctionNotRegistered', "The function %s is not registered with the ConfigFunctionManager" % (FunctionName))
        
        for name, obj in inspect.getmembers(FlexTransform.Configuration.ConfigFunctions, inspect.isclass) :
            if (name == ClassName) :
                return obj();
            
        raise Exception('FunctionClassNotFound', "The Class %s for function %s was not found by the ConfigFunctionManager" % (ClassName, FunctionName))
       
    def GetFunction(self, FunctionName):
        '''
        '''
        if FunctionName in self.__KnownFunctions:
            return True
        else :
            return False

    def ExecuteConfigFunction(self, FunctionName, args):
        '''
        '''
        
        FunctionClass = None
        if (FunctionName in self._FunctionClasses) :
            FunctionClass = self._FunctionClasses[FunctionName]
        else :
            FunctionClass = ConfigFunctionManager.GetFunctionClass(FunctionName)
            self._FunctionClasses[FunctionName] = FunctionClass
            
        self._ValidateArgs(FunctionName, args)
        return FunctionClass.Execute(FunctionName, args)
    
    def _ValidateArgs(self, FunctionName, args):
        '''
        Allowed fields for the Args dictionary:
        
        functionArg     - Optional - Any arguments passed to the function when it is called from SchemaParser. 
                          This is the value of the string between the () in the function name in the .json schema configuration files
                        
        fieldName       - Optional - The name of the field being processed

        fileName        - Optional - The full path of the source file

        fieldDict       - Optional - The dictionary associated with this field
    
        '''
        AllowedFields = set(['functionArg', 'fileName', 'fieldName', 'fieldDict'])
        RequiredFields = set([])
        
        if (isinstance(args, dict)) :
            for arg in args :
                if (arg not in AllowedFields) :
                    self.logging.warning('A argument passed to function %s is not allowed: %s' % (FunctionName, arg))
        else :
            raise Exception('InvalidArgs','The arguments passed to function %s are not defined or not in dictionary format' % FunctionName)
                    
        
        if (self.__KnownFunctions[FunctionName]['RequiredArgs'] is not None) :
            RequiredFields.update(self.__KnownFunctions[FunctionName]['RequiredArgs'])
        
        for arg in RequiredFields :
            if (arg not in args or args[arg] is None) :
                raise Exception('InvalidArgs', 'Function %s args did not include the required %s field, could not process' % (FunctionName, arg))
