'''
Created on Oct 15, 2014

@author: ahoying
'''

import re
import sys

class KVParser(object):
    '''
    Key/Value Syntax Parser
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.SeparatorChar = r"\s"
        self.QuoteChar = r"[']"
        self.KVSeparator = r"[=]"
        
        self.ParsedData = {}
        
    def ValidateConfig(self,config):
        '''
        Validate KV Parser specific configuration options
        '''
        if (config.has_section('KEYVALUE')) :
            if (config.has_option('KEYVALUE', 'SeparatorChar')) :
                self.SeparatorChar = config['KEYVALUE']['SeparatorChar']
            if (config.has_option('KEYVALUE', 'QuoteChar')) :
                self.QuoteChar = config['KEYVALUE']['QuoteChar']
            if (config.has_option('KEYVALUE', 'KVSeparator')) :
                self.KVSeparator = config['KEYVALUE']['KVSeparator']
                
    def Read(self,file):
        '''
        Read file and parse into Transform object
        '''
        
        self.ParsedData = {}
        
        # TODO: Make it clearer what I'm doing here
        KVRegex = re.compile("([^"+self.KVSeparator.strip("[]")+"]+)"+ \
                                self.KVSeparator+"("+self.QuoteChar+"[^"+self.QuoteChar.strip("[]")+"]+"+self.QuoteChar+ \
                                "|[^"+self.SeparatorChar.strip("[]")+"]+)(?:"+self.SeparatorChar+"|$)")
        
        self.ParsedData['IndicatorData'] = []
        
        for line in file :
            try :
                match = KVRegex.findall(line)
                DataRow = dict(match)
                
                if (self.QuoteChar) :
                    for k,v in DataRow.items() :
                        DataRow[k] = v.strip(self.QuoteChar.strip("[]"))
                        
                self.ParsedData['IndicatorData'].append(DataRow)
            except : 
                print("Line could not be parsed: " + line, file=sys.stderr)
            
        return self.ParsedData
