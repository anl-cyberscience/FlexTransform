'''
Created on Jul 28, 2014

@author: ahoying
'''

import inspect
import FlexTransform.SyntaxParser
import logging

''' Debugging only '''
import pprint

class Parser(object):
    '''
    Base class for Syntax Parsers

    Implements class methods for finding and loading the appropriate parser based on the configuration file
    '''

    # Dictionary of loaded Parser classes
    __KnownParsers = {}

    def __init__(self, tracelist=[]):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.Parser')
        self.pprint = pprint.PrettyPrinter(indent=2)
        self.tracelist = tracelist
        self.traceindex = {}
        for x in self.tracelist:
            self.traceindex[x["src_field"]] = x
            for y in x["dst_fields"]:
                self.traceindex[y] = x
            for w in x["src_IRIs"]:
                self.traceindex[w] = x
            for z in x["dst_IRIs"]:
                self.traceindex[z] = x
        self.logging.debug("Initialized Parser with tracelist of {} elements.".format(len(tracelist)))
        
    @classmethod
    def UpdateKnownParsers(cls, ParserName, ParserClass):
        cls.__KnownParsers[ParserName] = ParserClass;

    @classmethod
    def GetParsers(cls):
        return cls.__KnownParsers

    @classmethod
    def GetParser(cls, ParserName, tracelist=[]):
        for name, obj in inspect.getmembers(FlexTransform.SyntaxParser, inspect.isclass) :
            if (name == ParserName) :
                return obj(tracelist=tracelist);

    # Virtual methods that must be implemented in child classes

    def ValidateConfig(self,config):
        '''
        Base validation method, must be implemented in subclasses
        '''
        raise Exception("MethodNotDefined","ValidateConfig")

    def Read(self,file,configurationfile):
        '''
        Base document read method, must be implemented in subclasses
        TODO: need proper subclassing: All subclasses should call this Read method as well, as it contains 
        code common to all parsers.
        '''
        
        ''' Ensure the derived data is available to all parsers, e.g. to extract information from the file
            name or metadata 
        '''
        self.ParsedData = {}
        if 'DerivedData' in configurationfile.SchemaConfig:
            self.ParsedData['DerivedData'] = {}
            for field in configurationfile.SchemaConfig['DerivedData']['fields']:
                self.ParsedData['DerivedData'][field] = configurationfile.SchemaConfig['DerivedData']['fields'][field]['value']
                if field in self.traceindex:
                    self.logging.debug("[TRACE {}]: Read: value {} copied to ParsedData['DerivedData'] from SchemaConfig".format(field, self.ParsedData['DerivedData'][field]))
    
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