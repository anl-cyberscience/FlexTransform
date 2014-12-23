'''
Created on Nov 17, 2014

@author: ahoying
'''

import sys

class DictionaryParser(object):
    '''
    Key/Value Syntax Parser
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.ParsedData = {}
        
    def ValidateConfig(self, config):
        '''
        Validate Dictionary Parser specific configuration options, no options required
        '''
        pass
                
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
        import json
        
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
                print("Field " + k + " does not contain a Value entry", file=sys.stderr)
                
        return DataRow
    