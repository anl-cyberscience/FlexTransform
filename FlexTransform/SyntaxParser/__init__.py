'''
Created on Jul 27, 2014

@author: ahoying
'''

from .CSVParser import CSVParser
from .DictionaryParser import DictionaryParser
from .KVParser import KVParser
from .Parser import Parser
from .XMLParser import XMLParser

# Map Parser types to Parser class names
Parser.UpdateKnownParsers('XML', 'XMLParser')
Parser.UpdateKnownParsers('KEYVALUE', 'KVParser')
Parser.UpdateKnownParsers('DICT', 'DictionaryParser')
Parser.UpdateKnownParsers('CSV', 'CSVParser')
