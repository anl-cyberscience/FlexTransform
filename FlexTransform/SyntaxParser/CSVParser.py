'''
Created on Aug 13, 2015

@author: ahoying
'''

import logging
import csv
import os
from builtins import str

class CSVParser(object):
    '''
    Key/Value Syntax Parser
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.ParsedData = {}
        self.logging = logging.getLogger('FlexTransform.CSVParser')
        
        self.Fields = [];
        self.Delimiter = ','
        self.QuoteChar = '"'
        self.EscapeChar = None
        self.HeaderLine = False
        self.DoubleQuote = True
        self.QuoteStyle = csv.QUOTE_MINIMAL
        self.LineTerminator = '\r\n'
        
    def ValidateConfig(self, config):
        '''
        Validate Dictionary Parser specific configuration options
        
        The indicatorsKey sets the key in the json document that contains the indicators, or "" if the root of the document contains the indicators
        '''
        if (config.has_section('CSV')) :
            if (config.has_option('CSV', 'Fields')) :
                FieldsList = config['CSV']['Fields']
                self.Fields = FieldsList.split(',')
            else :
                raise Exception("ConfigError", "CSV Configuration does not include the required Fields key")
            
            if (config.has_option('CSV', 'Delimiter')) :
                self.Delimiter = bytes(config['CSV']['Delimiter'], "utf-8").decode("unicode_escape").strip("\"'")
                
            if (config.has_option('CSV', 'QuoteChar')) :
                self.QuoteChar = bytes(config['CSV']['QuoteChar'], "utf-8").decode("unicode_escape")
                
            if (config.has_option('CSV', 'EscapeChar')) :
                self.EscapeChar = bytes(config['CSV']['EscapeChar'], "utf-8").decode("unicode_escape")
                
            if (config.has_option('CSV', 'HeaderLine')) :
                self.HeaderLine = config.getboolean('CSV', 'HeaderLine', fallback=False)
                
            if (config.has_option('CSV', 'DoubleQuote')) :
                self.DoubleQuote = config.getboolean('CSV', 'DoubleQuote', fallback=True)
                
            if (config.has_option('CSV', 'QuoteStyle')) :
                if (config['CSV']['QuoteStyle'].lower() == 'none') :
                    self.QuoteStyle = csv.QUOTE_NONE
                elif (config['CSV']['QuoteStyle'].lower() == 'nonnumeric') :
                    self.QuoteStyle = csv.QUOTE_NONNUMERIC
                elif (config['CSV']['QuoteStyle'].lower() == 'all') :
                    self.QuoteStyle = csv.QUOTE_ALL
                elif (config['CSV']['QuoteStyle'].lower() == 'minimal') :
                    self.QuoteStyle = csv.QUOTE_MINIMAL
                else :
                    raise Exception("ConfigError", "Unknown option for CSV QuoteStyle: " + config['CSV']['QuoteStyle'])
                
            if (config.has_option('CSV', 'LineTerminator')) :
                self.LineTerminator = bytes(config['CSV']['LineTerminator'], "utf-8").decode("unicode_escape")
    

    def Read(self,file):
        '''
        Read file and parse into Transform object
        '''
        
        self.ParsedData = {
                           "IndicatorData": []
                           }
        position = {}
        
        for idx, field in enumerate(self.Fields):
            position[idx] = field
        
        content = file.readlines()
        for line in content:
            records = line.split(self.Delimiter)
            to_add = {}
            for idx, record in enumerate(records): 
                record = record.rstrip(self.LineTerminator)
                to_add.update({position[idx] : record})
            self.ParsedData["IndicatorData"].append(to_add)
 
        return self.ParsedData
                
    def Finalize(self, MappedData):
        '''
        Finalize the formatting of the data before being returned to the caller
        '''
        
        if ('IndicatorData' not in MappedData or MappedData['IndicatorData'].__len__() == 0) :
            raise Exception('NoIndicatorData', 'Transformed data has no indicators, nothing to write')
        
        FinalizedData = []
        for indicator in MappedData['IndicatorData'] :
            DataRow = {}
            # Keep passing the IndicatorType forward with the data. This is somewhat messy, but that way we can use it on write
            # DataRow['IndicatorType'] = indicator['IndicatorType']
            
            for field in self.Fields :
                if (field not in indicator) :
                    self.logging.warning("Field %s does not exist in IndicatorData", field)
                    DataRow[field] = ''
                elif ('Value' in indicator[field]) :
                    DataRow[field] = indicator[field]['Value']
                else :
                    self.logging.warning("Field %s does not contain a Value entry", field)
                    DataRow[field] = ''
                    
            FinalizedData.append(DataRow)
            
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
            
        csv.register_dialect('flext', 
                            delimiter=self.Delimiter, 
                            quotechar=self.QuoteChar, 
                            escapechar=self.EscapeChar, 
                            doublequote=self.DoubleQuote, 
                            lineterminator=self.LineTerminator,
                            quoting=self.QuoteStyle)     

        writer = csv.DictWriter(file, fieldnames=self.Fields, dialect='flext')

        if (self.HeaderLine) :
            writer.writeheader()

        writer.writerows(FinalizedData)
        
