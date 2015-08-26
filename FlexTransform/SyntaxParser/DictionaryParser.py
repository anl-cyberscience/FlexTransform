'''
Created on Nov 17, 2014

@author: ahoying
'''

import logging
import json

import inspect
import FlexTransform.SyntaxParser.DICTParsers

class DictionaryParser(object):
    '''
    Key/Value Syntax Parser
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.ParsedData = {}
        self.logging = logging.getLogger('FlexTransform.DictionaryParser')
        
        self.indicatorsKey = ""
        self.AdvancedParser = None
        
    def LoadAdvancedParser(self,CustomParser):
        '''
        Returns the Custom Parser Class from the configuration file if it exists
        '''
        for name, obj in inspect.getmembers(FlexTransform.SyntaxParser.DICTParsers, inspect.isclass) :
            if (name == CustomParser) :
                return obj();
        
    def ValidateConfig(self, config):
        '''
        Validate Dictionary Parser specific configuration options
        
        The indicatorsKey sets the key in the json document that contains the indicators, or "" if the root of the document contains the indicators
        '''
        if (config.has_section('DICT')) :
            if (config.has_option('DICT', 'IndicatorsKey')) :
                self.indicatorsKey = config['DICT']['IndicatorsKey']
                
            if (config.has_option('DICT', 'CustomParser')) :
                CustomParser = config['DICT']['CustomParser']
                self.AdvancedParser = self.LoadAdvancedParser(CustomParser)
                if (self.AdvancedParser == None) :
                    raise Exception('CustomParserNotDefined', 'DICT: ' + CustomParser)
                
                if (config.has_section(CustomParser)) :
                    self.AdvancedParser.ValidateConfig(config)
    
    def Read(self,file):
        '''
        Read file and parse into Transform object
        '''
        
        self.ParsedData = {}
        
        if (self.AdvancedParser) :
            self.ParsedData = self.AdvancedParser.Read(file)
        else :
            jsondoc = json.load(file)
            
            if (self.indicatorsKey != "") :
                if (self.indicatorsKey in jsondoc) :
                    indicators = jsondoc.pop(self.indicatorsKey)
                    self.ParsedData['IndicatorData'] = []
                    
                    if (isinstance(indicators,list)) :
                        for indicator in indicators :
                            if (isinstance(indicator,dict)) :
                                self.ParsedData['IndicatorData'].append(indicator)
                            else :
                                raise Exception('WrongType','Indicator type is not a dictionary: ' + indicator)
                            
                    elif (isinstance(indicators,dict)) :
                        self.ParsedData['IndicatorData'].append(indicators)
                    
                    else :
                        raise Exception('WrongType','Indicator type is not a list or dictionary: ' + indicators)
                    
                    # Everything else in the document is considered to be header data
                    if (len(jsondoc)) :
                        self.ParsedData['DocumentHeaderData'] = jsondoc
                    
                else :
                    raise Exception('NoIndicatorData', 'Defined indicator key, ' + self.indicatorsKey + ', does not exist in source file')
                    
            else :
                raise Exception('NotYetImplemented', 'Paring json dictionaries without an indicatorsKey is not currently supported')
        
        return self.ParsedData
                
    def Finalize(self, MappedData):
        '''
        Finalize the formatting of the data before being returned to the caller
        '''
        
        if ('IndicatorData' not in MappedData or MappedData['IndicatorData'].__len__() == 0) :
            raise Exception('NoIndicatorData', 'Transformed data has no indicators, nothing to write')
        
        return self._MappedDataToDict(MappedData)
    
    def Write(self, file, FinalizedData):
        '''
        Write the data as json to the file.
        '''
        
        if (self.AdvancedParser) :
            self.AdvancedParser.Write(file, FinalizedData)
        else :
            json.dump(FinalizedData, file, sort_keys=True, indent=4)
    
    def _MappedDataToDict(self, MappedData):
        '''
        Take the Transformed data object, and rebuild the dictionary for the XML parser from the schema data
        '''
        ParsedData = []
        
        for rowType in MappedData :
            if (isinstance(MappedData[rowType],list)) :
                for row in MappedData[rowType] :
                    if (isinstance(row,dict)) :
                        DataRow = self._BuildDictRow(row)
                        ParsedData.append(DataRow)
                    else :
                        raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            elif (isinstance(MappedData[rowType],dict)) :
                DataRow = self._BuildDictRow(MappedData[rowType])
                ParsedData.append(DataRow)
            else :
                raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            
        return ParsedData
    
    def _BuildDictRow(self, row):
        '''
        Take a row from the MappedData object and return an unflattened dictionary for passing to dict_to_etree
        '''
        DataRow = {}
        
        for k, v in row.items() :
            if (k == 'IndicatorType') :
                # Keep passing the IndicatorType forward with the data. This is somewhat messy, but that way we can use it on write
                pass
            elif ('Value' in v) :
                if ('valuemap' in v) :
                    DataRow[v['valuemap']] = v['Value']
                else :
                    DataRow[k] = v['Value']
            else :
                self.logging.warning("Field %s does not contain a Value entry", k)
                
        return DataRow
    