'''
Created on Jul 27, 2014

@author: ahoying
'''

from SyntaxParser.Parser import Parser
from SyntaxParser.XMLParser import XMLParser
from SyntaxParser.KVParser import KVParser
from SyntaxParser.DictionaryParser import DictionaryParser    

# Map Parser types to Parser class names
Parser.UpdateKnownParsers('XML', 'XMLParser')
Parser.UpdateKnownParsers('KEYVALUE', 'KVParser')
Parser.UpdateKnownParsers('DICT', 'DictionaryParser')