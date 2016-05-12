'''
Created on Oct 15, 2014

@author: ahoying
'''

import re
import logging
import os

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
        
        self.logging = logging.getLogger('FlexTransform.KVParser')
        
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
                if isinstance(line, bytes):
                    line = line.decode('UTF-8')
                    
                match = KVRegex.findall(line)
                DataRow = dict(match)
                
                if (self.QuoteChar) :
                    for k,v in DataRow.items() :
                        DataRow[k] = v.strip(self.QuoteChar.strip("[]"))
                        
                self.ParsedData['IndicatorData'].append(DataRow)
            except : 
                self.logging.warning("Line could not be parsed: %s", line)
            
        return self.ParsedData

    def Finalize(self, MappedData):
        '''
        Finalize the formatting of the data before being returned to the caller
        '''

        if ('IndicatorData' not in MappedData or MappedData['IndicatorData'].__len__() == 0) :
            raise Exception('NoIndicatorData', 'Transformed data has no indicators, nothing to write')

        FinalizedData = []
        for row in MappedData['IndicatorData'] :

            indicatorRow = []
            # Keep passing the IndicatorType forward with the data. This is somewhat messy, but that way we can use it on write
            # DataRow['IndicatorType'] = indicator['IndicatorType']

            for field in row:
                DataRow = {}
                if ('Value' in row[field]) :
                    if 'datatype' in row[field]:
                        if (row[field]['datatype'] == 'enum' or row[field]['datatype'] == 'string'):
                            DataRow[field] = self.QuoteChar.strip("[]") + row[field]['Value'] + self.QuoteChar.strip("[]")
                        else:
                            DataRow[field] = row[field]['Value']
                    else:
                        DataRow[field] = row[field]['Value']
                    indicatorRow.append(DataRow)
                else :
                    self.logging.warning("Field %s does not contain a Value entry", field)

            FinalizedData.append(indicatorRow)
        return FinalizedData

    def Write(self, file, FinalizedData):
        '''
        Write the data as csv to the file.
        '''
        if isinstance(file, str):
            if os.path.exists(file):
                file = open(file, "w")
            else:
                self.logging.error("%s is not a valid filepath", file)

        if self.SeparatorChar == r"\s":
            separator = " "
        else:
            separator = self.SeparatorChar

        toWrite = ""
        for indicator in FinalizedData:
            for row in indicator:
                for key, value in row.items():
                    if value:
                        toWrite += key + self.KVSeparator.strip("[]") + value + separator
            toWrite = toWrite[:-1]
            toWrite += '\n'
        file.write(toWrite)