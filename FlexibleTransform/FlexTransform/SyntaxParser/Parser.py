'''
Created on Jul 28, 2014

@author: ahoying
'''

import inspect
import FlexTransform.SyntaxParser
import logging

class Parser(object):
    '''
    Base class for Syntax Parsers

    Implements class methods for finding and loading the appropriate parser based on the configuration file
    '''

    # Dictionary of loaded Parser classes
    __KnownParsers = {}

    def __init__(self):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.Parser')
        
    @classmethod
    def UpdateKnownParsers(cls, ParserName, ParserClass):
        cls.__KnownParsers[ParserName] = ParserClass;

    @classmethod
    def GetParsers(cls):
        return cls.__KnownParsers

    @classmethod
    def GetParser(cls, ParserName):
        for name, obj in inspect.getmembers(FlexTransform.SyntaxParser, inspect.isclass) :
            if (name == ParserName) :
                return obj();

    # Virtual methods that must be implemented in child classes

    def ValidateConfig(self,config):
        '''
        Base validation method, must be implemented in subclasses
        '''
        raise Exception("MethodNotDefined","ValidateConfig")

    def Read(self,file):
        '''
        Base document read method, must be implemented in subclasses
        '''
        raise Exception("MethodNotDefined","Read")
    
    def Write(self,file):
        '''
        Base document write method, must be implemented in subclasses
        '''
        raise Exception("MethodNotDefined","Write")
    
    def Finalize(self,data):
        '''
        Base document finalize method, must be implemented in subclasses
        '''
        raise Exception("MethodNotDefined","Finalize")