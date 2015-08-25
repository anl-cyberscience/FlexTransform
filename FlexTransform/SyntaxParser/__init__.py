'''
Created on Jul 27, 2014

@author: ahoying
'''

from .Parser import Parser
from .XMLParser import XMLParser
from .KVParser import KVParser
from .DictionaryParser import DictionaryParser
from .CSVParser import CSVParser

# Map Parser types to Parser class names
Parser.UpdateKnownParsers('XML', 'XMLParser')
Parser.UpdateKnownParsers('KEYVALUE', 'KVParser')
Parser.UpdateKnownParsers('DICT', 'DictionaryParser')
Parser.UpdateKnownParsers('CSV', 'CSVParser')