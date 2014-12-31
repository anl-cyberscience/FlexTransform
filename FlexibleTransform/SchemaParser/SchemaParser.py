'''
Created on Oct 13, 2014

@author: ahoying
'''

import collections
import re
import time
import datetime
import socket
import pytz
import logging
import uuid

class SchemaParser(object):
    '''
    Base class for the Schema Parser logic
    '''
    
    def __init__(self, config):
        '''
        Constructor
        '''
        self.SchemaConfig = config
        
        # TODO: ValueMap is only need for source configs, OntologyMapping is only needed for target configs
        self.ValueMap = self._ValuemapToField(config)
        self.OntologyMapping = self._OntologyMappingToField(config)
        
        # Regex used to parse the outputFormat field
        # Example outputFormat: "[comment], direction:[direction], confidence:[confidence], severity:[severity]"
        self._outputFormatRE = re.compile(r"([^\[]+)?(?:\[([^\]]+)\])?")
        
        # TODO: Create a JSON schema document and validate the config against the schema. Worst case, define accepted tags and validate there are no unknown tags.
        
        self.logging = logging.getLogger('FlexTransform/SchemaParser')
   
    def MapDataToSchema(self, SourceData):
        '''
        Maps the values in SourceData to the underlying schema from the config
        TODO: Create an ABOX (using the Ontology Oracle) to represent the source file; this will also inform the
              target production, as data will be requested from the ABOX.
              
              Essentially this will consist of creating instances of the appropriate subclasses in an ABOX.
        '''
        MappedData = {}
                
        for rowType in SourceData :
            if (rowType in self.SchemaConfig) :
                if (isinstance(SourceData[rowType],list)) :
                    MappedData[rowType] = []
                    for row in SourceData[rowType] :
                        if (isinstance(row,dict)) :
                            try :
                                DataRow = self._MapRowToSchema(SchemaParser.FlattenDict(row),rowType)
                                MappedData[rowType].append(self._GetDefaultValuesFromSchema(rowType, DataRow))
                            except Exception as inst :
                                self.logging.exception(inst)
                                self.logging.debug(str(SchemaParser.FlattenDict(row)))
                        else :
                            raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
                elif (isinstance(SourceData[rowType],dict)) :
                    DataRow = self._MapRowToSchema(SchemaParser.FlattenDict(SourceData[rowType]),rowType)
                    MappedData[rowType] = self._GetDefaultValuesFromSchema(rowType, DataRow)
                else :
                    raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            else :
                raise Exception('SchemaConfigNotFound', 'Data Type: ' + rowType)
    
        return MappedData
    
    def MapMetadataToSchema(self, MappedData, sourceMetaData):
        '''
        Add meta data to the MappedData
        '''
        
        if ('DocumentMetaData' in self.SchemaConfig) :
            if (isinstance(sourceMetaData,dict)) :
                DataRow = self._MapRowToSchema(SchemaParser.FlattenDict(sourceMetaData),'DocumentMetaData')
                MappedData['DocumentMetaData'] = self._GetDefaultValuesFromSchema('DocumentMetaData', DataRow)
            else :
                raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
        else :
            raise Exception('SchemaConfigNotFound', 'Data Type: DocumentMetaData')
    
    def TransformData(self, MappedData):
        '''
        Takes the data that was mapped to the source schema and transform it using the target schema
        '''
        TransformedData = {}
               
        # Parse indicators before headers
        rowTypes = []
        
        DocumentHeaderData = None
        DocumentMetaData = None
        
        if ('IndicatorData' in self.SchemaConfig.keys()) :
            rowTypes.append('IndicatorData')
        if ('DocumentHeaderData' in self.SchemaConfig.keys()) :
            rowTypes.append('DocumentHeaderData')
            
        if ('DocumentHeaderData' in MappedData) :
            DocumentHeaderData = MappedData['DocumentHeaderData']

        if ('DocumentMetaData' in MappedData) :
            DocumentMetaData = MappedData['DocumentMetaData']
        
        for rowType in rowTypes :
            if (rowType in MappedData) :
                if (isinstance(MappedData[rowType],list)) :
                    TransformedData[rowType] = []
                    for row in MappedData[rowType] :
                        if (isinstance(row,dict)) :
                            try :
                                DataRow = self._TransformDataToNewSchema(rowType, row, DocumentHeaderData, DocumentMetaData)
                                TransformedData[rowType].append(self._GetDefaultValuesFromSchema(rowType, DataRow))
                            except Exception as inst :
                                self.logging.exception(inst)
                        else :
                            raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
                        
                elif (isinstance(MappedData[rowType],dict)) :
                    DataRow = self._TransformDataToNewSchema(rowType, MappedData[rowType], DocumentHeaderData, DocumentMetaData)
                    TransformedData[rowType] = self._GetDefaultValuesFromSchema(rowType, DataRow)
                else :
                    raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            else :
                TransformedData[rowType] = self._GetDefaultValuesFromSchema(rowType, None)

        return self._CalculateFunctionValues(TransformedData)
            
    def _ValuemapToField(self, config):
        '''
        Create a fast lookup dictionary for mapping values from flattened dictionaries back to the schema field
        '''
        
        ValueMap = {}
        
        for rowType in config :
            ValueMap[rowType] = {}
            if ('fields' in config[rowType] and isinstance(config[rowType]['fields'],dict)) :
                for fieldName, fieldDict in config[rowType]['fields'].items() :
                    if ('valuemap' in fieldDict) :
                        ValueMap[rowType][fieldDict['valuemap']] = fieldName
                    if ('additionalValuemaps' in fieldDict) :
                        for valuemap in fieldDict['additionalValuemaps'] :
                            ValueMap[rowType][valuemap] = fieldName
                        
        return ValueMap
    
    def _OntologyMappingToField(self, config):
        '''
        Create a fast lookup dictionary for mapping ontology mappings back to the schema field
        TODO: Update to query ontology directly
        '''

        # TODO: This whole concept may work for now, but I worry that more complex ontologies will make this difficult to work with
        
        # TODO: Multiple fields having the same Ontology Mapping blows up the dict
        
        OntologyMapping = {}
        
        for rowType in config :
            OntologyMapping[rowType] = {}
            if ('fields' in config[rowType] and isinstance(config[rowType]['fields'],dict)) :
                for fieldName, fieldDict in config[rowType]['fields'].items() :
                    if ('ontologyMappingType' in fieldDict) :
                        if (fieldDict['ontologyMappingType'] == 'none') :
                            pass
                        
                        elif (fieldDict['ontologyMappingType'] == 'simple') :
                            if (fieldDict['ontologyMapping'] != '') :
                                OntologyMapping[rowType][fieldDict['ontologyMapping']] = fieldName
                                
                        elif (fieldDict['ontologyMappingType'] == 'multiple') :
                            if ('ontologyMappings' in fieldDict) :
                                for mapping in fieldDict['ontologyMappings'] :
                                    if (mapping != '') :
                                        OntologyMapping[rowType][mapping] = fieldName
                        elif (fieldDict['ontologyMappingType'] == 'enum') :
                            if ('enumValues' in fieldDict) :
                                for k,v in fieldDict['enumValues'].items() :
                                    if ('ontologyMapping' in v) :
                                        if (v['ontologyMapping'] != '') :
                                            OntologyMapping[rowType][v['ontologyMapping']] = "%s::%s" % (fieldName, k)
                            else :
                                raise Exception('MissingEnumValues', 'enumValues missing from field %s' % fieldName)
                            
                        elif (fieldDict['ontologyMappingType'] == 'referencedEnum') :
                            # TODO: This logic doesn't seem right, I need to tie the meaning back to the value of the referenced field, this could be a mess
                            if ('ontologyMappingEnumValues' in fieldDict) :
                                for k,v in fieldDict['ontologyMappingEnumValues'].items() :
                                    if ('ontologyMapping' in v) :
                                        if (v['ontologyMapping'] != '') :
                                            OntologyMapping[rowType][v['ontologyMapping']] = "%s" % fieldName
                            else :
                                raise Exception('MissingOntologyMappingEnumValues', 'ontologyMappingEnumValues missing from field %s' % fieldName)
                        else :
                            raise Exception('UnknownOntologyMappingType', 'The OntologyMappingType %s in field %s is undefined' % (fieldDict['ontologyMappingType'], fieldName))
                        
                    else :
                        raise Exception('MissingOntologyMappingType', 'The OntologyMappingType is missing from field %s' % fieldName)
                        
        return OntologyMapping

    def _MapRowToSchema(self, DataRow, rowType, skipTypeCheck=False):
        '''
        Create a new dictionary with the mapping between the data row and the schema field definition
        '''
        
        newDict = {}
        
        ValueMap = self.ValueMap[rowType]
        
        # FIXME: It is wasteful to copy the whole schema field definition into each newly mapped field, it would be better to have a pointer back to the schema definition for the field
        
        for k,v in DataRow.items() :
            fieldName = None
            
            if (k == 'IndicatorType') :
                # Just copy the special field IndicatorType which maps this row to a specific indicator type
                newDict[k] = DataRow[k]
                continue
                       
            if (k in ValueMap) :
                fieldName = ValueMap[k]
            elif (k in self.SchemaConfig[rowType]['fields']) :
                fieldName = k
            else :
                self.logging.warning('%s not found in ValueMap for row type %s in schema config. Value: %s', k, rowType, v)
                continue
                
            if (fieldName is not None) :
                if ('error' in self.SchemaConfig[rowType]['fields'][fieldName] ) :
                    raise Exception("InvalidSchemaMapping", self.SchemaConfig[rowType]['fields'][fieldName]['error'])

                if ('ignore' in self.SchemaConfig[rowType]['fields'][fieldName] ) :
                    continue    
                              
                newDict[fieldName] = self.SchemaConfig[rowType]['fields'][fieldName].copy()
                
                if (isinstance(v,list) and 
                    'multiple' in self.SchemaConfig[rowType]['fields'][fieldName] and 
                    self.SchemaConfig[rowType]['fields'][fieldName]['multiple'] == True) :
                    
                    if (self.SchemaConfig[rowType]['fields'][fieldName]['datatype'] == 'group') :
                        
                        # This processes instances where the same field grouping may exist multiple times in a single indicator
                        
                        newDataRow = {}
                        
                        subfields = self.SchemaConfig[rowType]['fields'][fieldName]['subfields']
                        x = 0
                        
                        for row in v :
                            if (isinstance(row,dict)) :
                                subRow = SchemaParser.FlattenDict(row, ParentKey=k)
                                
                                for (subkey, subvalue) in subRow.items() :
                                    if (subkey in ValueMap and ValueMap[subkey] not in subfields) :
                                        raise Exception('FieldNotAllowed','Field %s is not an allowed subfield of %s' % (ValueMap[subkey], fieldName))
                                    
                                    newDataRow[subkey] = subvalue
                                        
                                subDict = self._MapRowToSchema(newDataRow, rowType, skipTypeCheck=True)
                                newDict.update(self._UpdateFieldReferences(subDict, x, subfields))
                                x = x + 1
                                
                            else :
                                raise Exception('DataError', 'Data type of sub row for %s is not dict: %s' % (k, row))
                            
                        # Value could be set to any string, it isn't used for field groups except to indicate that the group has been parsed
                        newDict[fieldName]['Value'] = 'True'
                    else :
                        if (v.__len__() > 1) :
                            newDict[fieldName]['AdditionalValues'] = []
                        for d in v :
                            if (isinstance(d,(list,dict))) :
                                self.logging.warning('%s subvalue in the list is another list or dictionary, not currently supported: %s', k, v)
                                continue
                            
                            if ('Value' not in newDict[fieldName]) :
                                # Put the first value in Value and the rest into AdditionalValues
                                newDict[fieldName]['Value'] = str(d)
                            else :
                                newDict[fieldName]['AdditionalValues'].append(str(d))
                        
                elif (isinstance(v,(list,dict))) :
                    self.logging.warning('%s value is a list or dictionary, not currently supported: %s', k, v)
                    continue
                elif (isinstance(v,str)) :
                    # The rstrip is to get rid of rogue tabs and white space at the end of a value, a frequent problem with STIX formated documents in testing
                    newDict[fieldName]['Value'] = str.rstrip(v)
                else :
                    newDict[fieldName]['Value'] = str(v)
                
                newDict.update(self._ValidateField(newDict[fieldName], fieldName, rowType))
                
        for fieldName,v in self.SchemaConfig[rowType]['fields'].items() :
            if (v['datatype'] == 'complex') :
                fields = v['fields']
                allFields = True
                
                # TODO: Is there ever an instance of a complex type where all fields don't exist that should still be included in the data row?
                for field in fields :
                    if (not field in newDict) :
                        allFields = False
                        break
                    
                if (allFields) :              
                    newDict[fieldName] = v.copy()
                    
                    # Build a new value based on the output format, if it exists
                    if ('outputFormat' in v) :
                        # Regex match returns two values into a set. [0] is anything that isn't a field name and [1] is a field name
                        # New value replaces [field] with the value of that field and just outputs everything out directly
                        match = self._outputFormatRE.findall(v['outputFormat'])
                        if (match) :
                            Value = ''
                            for m in match :
                                if (m[0] != '') :
                                    Value += m[0]
                                if (m[1] != '') :
                                    Value += newDict[m[1]]['Value']
                            newDict[fieldName]['Value'] = Value

        if (not skipTypeCheck and rowType == "IndicatorData") :
            self._AddIndicatorType(newDict)

        return newDict

    def _UpdateFieldReferences(self, subDict, x, subfields):
        '''
        Update any key or value that equals one of the subfields with the name subfield_x
        '''
        
        if (x) :
            # Only rename entries if x is > 0
            for (k,v) in subDict.items() :
                if (isinstance(v,dict)) :
                    self._UpdateFieldReferences(v, x, subfields)
                elif (isinstance(v,str)) :
                    if (v in subfields) :
                        subDict[k] = "%s_%i" % (v, x)
                        
        for k in subfields :
            if (k in subDict) :
                if (x) :
                    # Only rename entries if x is > 0
                    v = subDict.pop(k)
                    k = "%s_%i" % (k, x)
                    subDict[k] = v
                subDict[k]['groupID'] = x
                
        return subDict

    def _AddIndicatorType(self, newDict):
        '''
        Determine the indicator type from the data and add a new field IndicatorType to the data row
        '''
        if ("types" not in self.SchemaConfig["IndicatorData"]) :
            raise Exception("NoIndicatorTypes", "Indicator Types not defined in schema")
    
        '''
        The layout of the indicator types in the schema is a dictionary of indicator Types, which have a list of possible indicator matches, 
        which have one or more required fields and values in a dictionary. The best match (based on weight, more exact matches have a higher weight) wins.
        In the case of a tie, the first match wins. Running through every possible type is a little slower, but it makes sure the best possible indicator types are chosen
                        
        Example: "DNS-Hostname-Block": [ { "classification_text": "Domain Block:*" } ],
                If the classification_text field has a value of Domain Blocks:<anything> then the indicator type is determined to be a DNS-Hostname-Block.
                Multiple fields can be required for a single match, and multiple possible matches can be tried for a single indicator type
        '''
       
        bestMatch = None
        bestWeight = 0
               
        for indicatorType, indicatorMatches in self.SchemaConfig["IndicatorData"]["types"].items() :
            for indicatorMatch in indicatorMatches :
                match = False
                Weight = 0
                for k,v in indicatorMatch.items() :
                    matchKeys = []
                    if (k in newDict) :
                        matchKeys.append(k)
                        prefix = "%s_" % k
                        for key in newDict :
                            if key.startswith(prefix) :
                                matchKeys.append(key)
                                
                    if (matchKeys.__len__() > 0) :
                        submatch = False
                        for key in matchKeys :
                            if (key in newDict and "Value" in newDict[key]) :
                                if (v == "*" and newDict[key]['Value'] != "") :
                                    Weight += 1
                                    submatch = True
                                elif (v.endswith("*") and newDict[k]["Value"].startswith(v.strip("*"))) :
                                    Weight += 5
                                    submatch = True
                                elif (newDict[k]["Value"] == v) :
                                    Weight += 10
                                    submatch = True
                                
                        if (submatch) :
                            match = True
                        else :
                            match = False
                            Weight = 0
                            break
                        
                    elif (v == "") :
                        Weight += 5
                        match = True
                    else :
                        match = False
                        Weight = 0
                        break
                        
                if (match and Weight > bestWeight) :
                    bestMatch = indicatorType
                    bestWeight = Weight
                
        if (bestMatch is not None) :
            newDict["IndicatorType"] = bestMatch
        else :
            raise Exception ("NoMatchingIndicatorType", "This indicator data row does not match any defined indicator types")

    def _ValidateField(self, fieldDict, fieldName, rowType):
        '''
        Validate the schema configuration for the field passes
        '''
        
        # Regexes used for validation
        
        # This is a pretty simple regex, but it should work in most cases. Might need to be replaced with something more sophisticated
        EMAIL_REGEX = re.compile("^[^@]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}$")
        
        newDict = {}
               
        # Validate the dataType matches the value
        dataType = fieldDict['datatype']
        
        values = []
        if ('Value' in fieldDict) :
            values.append(fieldDict['Value'])
        
        if ('AdditionalValues' in fieldDict) :
            values.extend(fieldDict['AdditionalValues'])
            
        if (values.__len__() == 0) :
            raise Exception('NoValue', 'Field %s has no value' % fieldName)
        
        # TODO: ParsedValue only contains the last tested value if there are multiple values for the field. This might be a problem for some data types.
        
        for value in values :
            if (dataType == 'string') :
                # String data type is always valid, pass
                pass
            elif (dataType == 'complex') :
                # Complex data type is always valid, pass
                pass
            elif (dataType == 'group') :
                # Group data type is always valid, pass
                pass
            elif (dataType == 'int') :
                fieldDict['ParsedValue'] = int(value)
                if (str(fieldDict['ParsedValue']) != value) :
                    raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not an int: ' + value)
                if ('dataRange' in fieldDict) :
                    datarange = fieldDict['dataRange'].split('-')
                    if (fieldDict['ParsedValue'] < int(datarange[0]) or fieldDict['ParsedValue'] > int(datarange[1])) :
                        raise Exception('DataOutOfRange','The value for field ' + fieldName + ' is outside of the allowed range('+fieldDict['dataRange']+'): ' + value)
            elif (dataType == 'datetime') :
                # TODO: Support multiple date time formats
                if ('dateTimeFormat' not in fieldDict) :
                    raise Exception('SchemaConfigMissing', 'The dateTimeFormat configuration is missing for field ' + fieldName)
                try :
                    if (fieldDict['dateTimeFormat'] == "unixtime") :
                        fieldDict['ParsedValue'] = pytz.utc.localize(datetime.datetime.utcfromtimestamp(int(value)))
                    else :
                        # This is a very poor hack to force the weird STIX time format from the CISCP reports with timezone as [+-]xx:yy to the standard [+-]xxyy format.
                        # TODO: Have something in the json config that forces this conversion, and can undo it on write if needed. Possibly use pytz to fix the issue 
                        match = re.match(r"(.*)([+-]\d\d):(\d\d)$", value)
                        if (match) :
                            value = match.group(1) + match.group(2) + match.group(3)
                        fieldDict['ParsedValue'] = datetime.datetime.strptime(value, fieldDict['dateTimeFormat'])
                except Exception as inst :
                    self.logging.exception(inst)
                    raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not a valid date time value: ' + value)
            elif (dataType == 'enum') :
                if (value not in fieldDict['enumValues']) :
                    # Check if there is a case mismatch, update the value to the correct case if there is.
                    caseUpdated = False
                    for k in fieldDict['enumValues'] :
                        if (value.lower() == k.lower()) :
                            fieldDict['Value'] = k
                            caseUpdated = True
                            break
                        
                    if (not caseUpdated) :
                        raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not listed in the enum values: ' + value)
            elif (dataType == 'emailAddress') :
                if (EMAIL_REGEX.match(value) is None) :
                    raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not a valid email address: ' + value)
            elif (dataType == 'ipv4') :
                try :
                    fieldDict['ParsedValue'] = socket.inet_aton(value)
                except :
                    raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not a valid ipv4 address: ' + value)
            elif (dataType == 'ipv6') :
                try :
                    fieldDict['ParsedValue'] = socket.inet_pton(socket.AF_INET6, value)
                except :
                    raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not a valid ipv6 address: ' + value)
            else :
                self.logging.error("No validation written for dataType: %s", dataType)
            
        
        # Process the regexSplit directive
        if ('regexSplit' in fieldDict) :
            match = re.match(fieldDict['regexSplit'], value)
            if match:
                regexFields = re.split(',\s+', fieldDict['regexFields'])
                i = 0
                while (i < regexFields.__len__()) :
                    if (match.group(i+1)) :
                        newFieldName = regexFields[i]
                        newFieldValue = match.group(i+1)
                        newDict[newFieldName] = self.SchemaConfig[rowType]['fields'][newFieldName].copy()
                        newDict[newFieldName]['Value'] = newFieldValue
                        
                        newDict.update(self._ValidateField(newDict[newFieldName], newFieldName, rowType))
                    
                    i+=1
        
        return newDict
    
    def _TransformDataToNewSchema(self, rowType, DataRow, DocumentHeaderData, DocumentMetaData):
        '''
        Transform the data row using the underlying ontology mappings to the new schema
        TODO: Update to query ontology directly
        '''
        
        # TODO: This function is far too large and complicated, it should be broken up into smaller functions
        
        newDict = {}
        
        OntologyMap = self.OntologyMapping[rowType]
        
        DataRows = {}
        
        GroupRows = {}
        
        if (rowType == 'IndicatorData') :
            # Determine if the target schema accepts Indicators of type IndicatorType
            if ('IndicatorType' in DataRow) :
                IndicatorType = DataRow.pop('IndicatorType')
                if (IndicatorType not in self.SchemaConfig["IndicatorData"]["types"]) :
                    raise Exception("UnknownIndicatorType", "The Indicator Type %s is not known by the target schema" % IndicatorType)
                else :
                    newDict['IndicatorType'] = IndicatorType
                    
            if (DocumentHeaderData is not None) :
                for k, v in DocumentHeaderData.items() :
                    if (k in DataRows) :
                        self.logging.warning('Key %s already exists in data row, value %s, overwritten by DocumentHeaderData key with value %s', k, DataRows[k], v)
                        
                DataRows.update(DocumentHeaderData)

            if (DocumentMetaData is not None) :
                for k, v in DocumentMetaData.items() :
                    if (k in DataRows) :
                        self.logging.warning('Key %s already exists in data row, value %s, overwritten by DocumentMetaData key with value %s', k, DataRows[k], v)
                        
                DataRows.update(DocumentMetaData)
                
                
        for k, v in DataRow.items() :
            if (k in DataRows) :
                self.logging.warning('Key %s already exists in data row, value %s, overwritten by DataRow key with value %s', k, DataRows[k], v)
                
        DataRows.update(DataRow)
        
        # TODO: Handle fields with AdditionalValues
        
        for field, fieldDict in DataRows.items() :
            if ('Value' not in fieldDict) :
                self.logging.warning("Field %s has no value", field)
                continue
            
            if (field == 'id') :
                pass
            
            fieldName = None
            OntologyReference = None
            Value = fieldDict['Value']
    
            referencedField = None
            referencedValue = None
                
            if ('ontologyMappingType' in fieldDict) :
                if (fieldDict['ontologyMappingType'] == 'none') :
                    continue
                
                elif (fieldDict['ontologyMappingType'] == 'simple') :
                    if (fieldDict['ontologyMapping'] != '') :
                        OntologyReference = fieldDict['ontologyMapping']
                        
                elif (fieldDict['ontologyMappingType'] == 'multiple') :
                    if ('ontologyMappings' in fieldDict) :
                        for mapping in fieldDict['ontologyMappings'] :
                            if (mapping != '' and mapping in OntologyMap) :
                                OntologyReference = mapping
                                break
                        
                elif (fieldDict['ontologyMappingType'] == 'enum') :
                    if ('enumValues' in fieldDict) :
                        if (Value in fieldDict['enumValues']) :
                            if (fieldDict['enumValues'][Value]['ontologyMapping'] != '') :
                                OntologyReference = fieldDict['enumValues'][Value]['ontologyMapping']

                        else :
                            for eValue in fieldDict['enumValues'] :
                                if ('*' in eValue and eValue != '*' and fieldDict['enumValues'][eValue]['ontologyMapping'] != '') :
                                    if (eValue.startswith('*')) :
                                        if (Value.endswith(eValue.strip('*'))) :
                                            OntologyReference = fieldDict['enumValues'][eValue]['ontologyMapping']
                                            break
                                    elif (eValue.endswith('*')) :
                                        if (Value.startswith(eValue.strip('*'))) :
                                            OntologyReference = fieldDict['enumValues'][eValue]['ontologyMapping']
                                            break
                                        
                        if (OntologyReference is None and "*" in fieldDict['enumValues']) :
                            if (fieldDict['enumValues']['*']['ontologyMapping'] != '') :
                                OntologyReference = fieldDict['enumValues']['*']['ontologyMapping']

                    else :
                        raise Exception('MissingEnumValues', 'enumValues missing from field %s' % fieldName)
                    
                elif (fieldDict['ontologyMappingType'] == 'referencedEnum') :
                    referencedField = fieldDict['ontologyEnumField']
                    if (referencedField in DataRow and 'Value' in DataRow[referencedField]) :
                        # TODO: Will this ever need to use ParsedValue?
                        referencedValue = DataRow[referencedField]['Value']
                    if ('ontologyMappingEnumValues' in fieldDict) :
                        if (referencedValue in fieldDict['ontologyMappingEnumValues']) :
                            if (fieldDict['ontologyMappingEnumValues'][referencedValue]['ontologyMapping'] != '') :
                                OntologyReference = fieldDict['ontologyMappingEnumValues'][referencedValue]['ontologyMapping']

                        else :
                            for eValue in fieldDict['ontologyMappingEnumValues'] :
                                if ('*' in eValue and eValue != '*' and fieldDict['ontologyMappingEnumValues'][eValue]['ontologyMapping'] != '') :
                                    if (eValue.startswith('*')) :
                                        if (referencedValue.endswith(eValue.strip('*'))) :
                                            OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue]['ontologyMapping']
                                            break
                                    elif (eValue.endswith('*')) :
                                        if (referencedValue.startswith(eValue.strip('*'))) :
                                            OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue]['ontologyMapping']
                                            break
                                        
                        if (OntologyReference is None and "*" in fieldDict['ontologyMappingEnumValues']) :
                            if (fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping'] != '') :
                                OntologyReference = fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping']
                    else :
                        raise Exception('ontologyMappingEnumValues', 'ontologyMappingEnumValues missing from field %s' % fieldName)
                else :
                    raise Exception('UnknownOntologyMappingType', 'The OntologyMappingType %s in field %s is undefined' % (fieldDict['ontologyMappingType'], fieldName))
                
            else :
                raise Exception('MissingOntologyMappingType', 'The OntologyMappingType is missing from field %s' % fieldName)
            
            if (OntologyReference is not None) :
                if (OntologyReference in OntologyMap) :
                    fieldName = OntologyMap[OntologyReference]
                    
                    if (re.search("::", fieldName)) :
                        match = re.split("::", fieldName)
                        fieldName = match[0]
                        if (not match[1].endswith('*')) :
                            Value = match[1]
                else :
                    self.logging.debug("Field %s does not map to target schema ontology", field)
                    continue
                
            if (fieldName is None) :
                self.logging.debug("Field %s does not have an Ontology reference value defined", field)
                continue
            
            if ('memberof' in self.SchemaConfig[rowType]['fields'][fieldName]) :
                # Field is part of a group, handle separately after the rest of the fields are processed
                memberof = self.SchemaConfig[rowType]['fields'][fieldName]['memberof']
                
                if (memberof not in GroupRows) :
                    GroupRows[memberof] = {'fields': {}}
                if (fieldName not in GroupRows[memberof]['fields']) :
                    GroupRows[memberof]['fields'][fieldName] = []
                                    
                fieldDict['matchedOntology'] = OntologyReference
                fieldDict['ReferencedField'] = referencedField
                fieldDict['ReferencedValue'] = referencedValue
                fieldDict['NewValue'] = Value
                
                GroupRows[memberof]['fields'][fieldName].append(fieldDict)
                continue
                
            if (fieldName in newDict) :
                self.logging.error('Field %s already exists in target row mapping, the field will be overwritten with a new value', fieldName)
            
            if (self.SchemaConfig[rowType]['fields'][fieldName]['ontologyMappingType'] == 'multiple') :
                # Fields with multiple ontology mappings are listed in best first order
                # This finds the best possible match and uses that in the translation
                # TODO: Can this be done better with the ontology oracle?
                Ord = None
                
                for i, mapping in enumerate(self.SchemaConfig[rowType]['fields'][fieldName]['ontologyMappings']) :
                    if (mapping == OntologyReference) :
                        Ord = i
                        break
                        
                if (fieldName in newDict) :
                    if (Ord < newDict[fieldName]['matchedOntologyOrd']) :
                        # Better match found
                        del(newDict[fieldName])
                        
                        newDict[fieldName] = self.SchemaConfig[rowType]['fields'][fieldName].copy()
                        newDict[fieldName]['matchedOntology'] = OntologyReference
                        newDict[fieldName]['matchedOntologyOrd'] = Ord
                else :
                    # No current match exists
                    newDict[fieldName] = self.SchemaConfig[rowType]['fields'][fieldName].copy()
                    newDict[fieldName]['matchedOntology'] = OntologyReference
                    newDict[fieldName]['matchedOntologyOrd'] = Ord
            else :
                newDict[fieldName] = self.SchemaConfig[rowType]['fields'][fieldName].copy()
                newDict[fieldName]['matchedOntology'] = OntologyReference
            
            if (newDict[fieldName]['datatype'] == 'datetime') :
                if ('ParsedValue' in fieldDict) :
                    if (newDict[fieldName]['dateTimeFormat'] == 'unixtime') :
                        newDict[fieldName]['Value'] = '%i' % time.mktime(fieldDict['ParsedValue'].timetuple())
                    else :
                        newDict[fieldName]['Value'] = fieldDict['ParsedValue'].strftime(newDict[fieldName]['dateTimeFormat'])
                else :
                    # TODO: ParsedValue should always exist, but I got errors when testing some CISCP STIX documents, need to test further
                    self.logging.error('DateTime data type did not have a ParsedValue defined for field %s (%s)', fieldName, fieldDict)
                
            elif (fieldDict['datatype'] != newDict[fieldName]['datatype']) :
                if (fieldDict['datatype'] == 'complex' or newDict[fieldName]['datatype'] == 'complex' or newDict[fieldName]['datatype'] == 'string' or newDict[fieldName]['datatype'] == 'enum') :
                    newDict[fieldName]['Value'] = Value
                else :
                    if (newDict[fieldName]['datatype'] == 'ipv4' and re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', Value)) :
                        newDict[fieldName]['Value'] = Value
                    else :
                        # FIXME: Process value to appropriate type for target schema
                        self.logging.warning("Cannot convert between data types for fields %s, %s", field, fieldName)
                
            else :
                newDict[fieldName]['Value'] = Value
                
            newDict[fieldName]['ReferencedField'] = referencedField
            newDict[fieldName]['ReferencedValue'] = referencedValue
            
            newDict.update(self._ValidateField(newDict[fieldName], fieldName, rowType))
                
        # Populate GroupRows with all required groups
        for k, v in self.SchemaConfig[rowType]['fields'].items() :              
            if ('required' in v and v['required'] == True) :
                if ('datatype' in v and v['datatype'] == 'group') :
                    if (k not in GroupRows) :
                        GroupRows[k] = { 'fields': {} }
                
        if (GroupRows.__len__()) :
            for group in GroupRows :
                if (group not in newDict) :
                    newDict[group] = self.SchemaConfig[rowType]['fields'][group].copy()
                    newDict[group]['Value'] = 'True'
                    newDict[group]['ParsedValue'] = True
                    newDict[group]['groupedFields'] = []
                
                subfields = self.SchemaConfig[rowType]['fields'][group]['subfields']
                
                # Build the list of required fields for this group
                
                '''
                subfields should be a dictionary like the following:
                
                "subfields": { 
                                "reasonList_reasonCategory": {"required":true, "primaryKey":true}, 
                                "reasonList_reasonDescription": {"required":false}
                }
                '''
                
                requiredFields = []
                otherFields = []
                primaryKey = None
                for k,v in subfields.items() :
                    if ('primaryKey' in v and v['primaryKey'] == True) :
                        if (primaryKey is None) :
                            primaryKey = k
                        else :
                            raise Exception('MultiplePrimaryKeys', 'Group %s has multiple primaryKeys defined, that is not supported' % group)
                        
                    elif ('required' in v and v['required'] == True) :
                        requiredFields.append(k)
                        
                    else :
                        otherFields.append(k)
                        
                if (primaryKey is None) :
                    raise Exception('primaryKeyNotDefined', 'primaryKey not defined for group %s' % group)
                
                if (primaryKey not in GroupRows[group]['fields']) :
                    self.logging.debug('primaryKey field, %s, is missing from group %s', primaryKey, group)
                    if ('defaultValue' in self.SchemaConfig[rowType]['fields'][primaryKey]) :
                        fieldDict = {}
                        fieldDict['ReferencedField'] = None
                        fieldDict['ReferencedValue'] = None
                        fieldDict['matchedOntology'] = None
                        fieldDict['NewValue'] = self.SchemaConfig[rowType]['fields'][primaryKey]['defaultValue']
                        GroupRows[group]['fields'][primaryKey] = [ fieldDict ]
                    else :
                        raise Exception('primaryKeyNotFound', 'primaryKey not found for group %s and no defaultValue defined' % group)

                for fieldDict in GroupRows[group]['fields'][primaryKey] :
                    # Create one group for each unique primary key
                    fieldGroup = {}
                    fieldGroup[primaryKey] = self.SchemaConfig[rowType]['fields'][primaryKey].copy()
                    fieldGroup[primaryKey]['Value'] = fieldDict['NewValue']
                    fieldGroup[primaryKey]['ReferencedField'] = fieldDict['ReferencedField']
                    fieldGroup[primaryKey]['ReferencedValue'] = fieldDict['ReferencedValue']
                    fieldGroup[primaryKey]['matchedOntology'] = fieldDict['matchedOntology']
                    
                    fieldGroup.update(self._ValidateField(fieldGroup[primaryKey], primaryKey, rowType))
                    
                    groupID = None
                    if ('groupID' in fieldDict) :
                        groupID = fieldDict['groupID']
                    
                    for requiredField in requiredFields :
                        if (requiredField in GroupRows[group]['fields']) :
                            if (groupID is not None) :
                                for k in GroupRows[group]['fields'][requiredField] :
                                    if ('groupID' in k and k['groupID'] == groupID) :
                                        fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()
                                        fieldGroup[requiredField]['Value'] = k['NewValue']
                                        fieldGroup[requiredField]['ReferencedField'] = k['ReferencedField']
                                        fieldGroup[requiredField]['ReferencedValue'] = k['ReferencedValue']
                                        fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']
                            
                            # Determine if any of the defined fields match this primary key
                            elif (len(GroupRows[group]['fields'][primaryKey]) == 1 and len(GroupRows[group]['fields'][requiredField]) == 1) :
                                # If there is only one group, assume required fields belong to the same group.
                                k = GroupRows[group]['fields'][requiredField][0]
                                fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()
                                fieldGroup[requiredField]['Value'] = k['NewValue']
                                fieldGroup[requiredField]['ReferencedField'] = k['ReferencedField']
                                fieldGroup[requiredField]['ReferencedValue'] = k['ReferencedValue']
                                fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']
                            else :
                                self.logging.warning('Required field %s could not be matched to the appropriate group', requiredField)
                        
                        if (requiredField not in fieldGroup) :
                            # Create a new entry for this field
                            fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()
                            
                            if ('defaultValue' in fieldGroup[requiredField]) :
                                fieldGroup[requiredField]['Value'] = fieldGroup[requiredField]['defaultValue']
                                
                            # Don't validate fields that are set to function names until after the function is processed 
                            if (not (isinstance(fieldGroup[requiredField]['Value'], str) and fieldGroup[requiredField]['Value'].startswith('&'))) :
                                fieldGroup.update(self._ValidateField(fieldGroup[requiredField], requiredField, rowType))
                                
                    for otherField in otherFields :
                        if (otherField in GroupRows[group]['fields']) :
                            # Determine if any of the defined fields match this primary key
                            if (groupID is not None) :
                                for k in GroupRows[group]['fields'][otherField] :
                                    if ('groupID' in k and k['groupID'] == groupID) :
                                        fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                                        fieldGroup[otherField]['Value'] = k['Value']
                                        fieldGroup[otherField]['ReferencedField'] = k['ReferencedField']
                                        fieldGroup[otherField]['ReferencedValue'] = k['ReferencedValue']
                                        fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']
                            
                            elif (len(GroupRows[group]['fields'][primaryKey]) == 1 and len(GroupRows[group]['fields'][otherField]) == 1) :
                                # If there is only one group, assume required fields belong to the same group.
                                k = GroupRows[group]['fields'][otherField][0]
                                fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                                fieldGroup[otherField]['Value'] = k['Value']
                                fieldGroup[otherField]['ReferencedField'] = k['ReferencedField']
                                fieldGroup[otherField]['ReferencedValue'] = k['ReferencedValue']
                                fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']
                            else :
                                self.logging.warning('Field %s could not be matched to the appropriate group', otherField)
                                
                    newDict[group]['groupedFields'].append(fieldGroup)
        
        return newDict
    
    def _GetDefaultValuesFromSchema(self, rowType, SourceDataRow):
        '''
        Find all required fields in the target schema that do not exists in the source data row and add them with their default value
        '''    
        
        # Note: This function has been updated to use pass by reference instead of pass by value to improve performance
        
        OutputFormattedFields = []
        
        if (SourceDataRow is None) :
            SourceDataRow = {}
        
        # TODO: Lots of copy/paste code here, it should be refactored if possible
               
        for k,v in self.SchemaConfig[rowType]['fields'].items() :
            if (SourceDataRow and k in SourceDataRow) :
                continue
                
            elif ('required' in v and v['required'] == True) :
                if ('defaultValue' in v) :
                    SourceDataRow[k] = v.copy()
                    SourceDataRow[k]['Value'] = v['defaultValue']
                    
                    if (not (isinstance(v['defaultValue'], str) and v['defaultValue'].startswith('&'))) :
                        SourceDataRow.update(self._ValidateField(SourceDataRow[k], k, rowType))
                elif ('outputFormat' in v) :
                    SourceDataRow[k] = v.copy()
                    OutputFormattedFields.append(k)
                elif ('datatype' in v and v['datatype'] == 'group') :
                    raise Exception('GroupMissing', 'The group %s is required, but none of its fields exist' % k)
                else :
                    raise Exception('NoDefaultValue', 'Default Value or outputFormat not defined for required field %s' % k)
            elif ('outputFormat' in v) :
                SourceDataRow[k] = v.copy()
                OutputFormattedFields.append(k)
                
        for k,v in self.SchemaConfig[rowType]['fields'].items() :
            if (k in SourceDataRow and 'Value' in SourceDataRow[k]) :
                continue
                
            if ('requiredIfReferenceField' in v) :
                ReferenceField = v['requiredIfReferenceField']
                if ('requiredIfReferenceValues' in v) :
                    ReferenceValues = v['requiredIfReferenceValues']
                    for val in ReferenceValues :
                        if ( (ReferenceField in SourceDataRow and val == SourceDataRow[ReferenceField]['Value']) or ( val == '' and (not ReferenceField in SourceDataRow or not SourceDataRow[ReferenceField]['Value']) ) ) :
                            if ('defaultValue' in v) :
                                SourceDataRow[k] = v.copy()
                                SourceDataRow[k]['Value'] = v['defaultValue']
                                
                                if (not (isinstance(v['defaultValue'], str) and v['defaultValue'].startswith('&'))) :
                                    SourceDataRow.update(self._ValidateField(SourceDataRow[k], k, rowType))
                            elif ('outputFormat' in v) :
                                SourceDataRow[k] = v.copy()
                                OutputFormattedFields.append(k)
                            else :
                                raise Exception('NoDefaultValue', 'Default Value or outputFormat not defined for required field %s' % k)
                                
                elif ('requiredIfReferenceValuesMatch' in v) :
                    if (ReferenceField in SourceDataRow) :
                        ReferenceValuesMatch = v['requiredIfReferenceValuesMatch']
                        match = False
                        for val in ReferenceValuesMatch :
                            if (val == '*') :
                                if ('Value' in SourceDataRow[ReferenceField] ) :
                                    match = True
                                    break
                            elif (val.endswith('*')) :
                                if ('Value' in SourceDataRow[ReferenceField] and SourceDataRow[ReferenceField]['Value'].startswith(val.strip('*'))) :
                                    match = True
                                    break
                                
                        if (match) :
                            if ('defaultValue' in v) :
                                SourceDataRow[k] = v.copy()
                                SourceDataRow[k]['Value'] = v['defaultValue']
                                
                                if (not (isinstance(v['defaultValue'], str) and v['defaultValue'].startswith('&'))) :
                                    SourceDataRow.update(self._ValidateField(SourceDataRow[k], k, rowType))
                            elif ('outputFormat' in v) :
                                SourceDataRow[k] = v.copy()
                                OutputFormattedFields.append(k)
                            else :
                                raise Exception('NoDefaultValue', 'Default Value or outputFormat not defined for required field %s' % k)
                                
        for k in OutputFormattedFields :
            v = self.SchemaConfig[rowType]['fields'][k]
            # Build a new value based on the output format, if it exists
            # Regex match returns two values into a set. [0] is anything that isn't a field name and [1] is a field name
            # New value replaces [field] with the value of that field and outputs everything else out directly
            match = self._outputFormatRE.findall(v['outputFormat'])
            if (match) :
                Value = ''
                AllFields = True
                for m in match :
                    if (m[0] != '') :
                        Value += m[0]
                    if (m[1] != '') :
                        if (m[1] in SourceDataRow and 'Value' in SourceDataRow[m[1]]) :
                            Value += SourceDataRow[m[1]]['Value']
                        elif ('required' in v and v['required'] == True) :
                            raise Exception('NoDefaultValue', 'Default Value not defined for required field %s' % m[1])
                        else :
                            AllFields = False
                        
                # Check that all fields required for the output formated text exist, or delete the field from the results
                if (AllFields) :
                    SourceDataRow[k]['Value'] = Value
                else :
                    del SourceDataRow[k]
                    
        return SourceDataRow
    
    def _CalculateFunctionValues(self, TransformedData):
        '''
        Find any references to functions in the data and calculates the actual values.
        '''
        
        rowTypes = []
        if ('IndicatorData' in TransformedData) :
            rowTypes.append('IndicatorData')
        if ('DocumentHeaderData' in TransformedData) :
            rowTypes.append('DocumentHeaderData')
        
        for rowType in rowTypes :
            if (rowType in TransformedData) :
                if (isinstance(TransformedData[rowType],list)) :
                    for row in TransformedData[rowType] :
                        if (isinstance(row,dict)) :
                            self._CalculateFunctionValue(row, TransformedData)
                        
                elif (isinstance(TransformedData[rowType],dict)) :
                    self._CalculateFunctionValue(TransformedData[rowType], TransformedData)
                    
        return TransformedData
                    
    def _CalculateFunctionValue(self, row, TransformedData) :
        
        for k, v in row.items() :
            if (isinstance(v,dict) and 'groupedFields' in v) :
                for group in v['groupedFields'] :
                    self._CalculateFunctionValue(group, TransformedData)
            
            if (isinstance(v,dict) and 'Value' in v) :
                value = v['Value']
                if (value.startswith('&')) :
                    match = re.match(r'&([^\(]+)\(([^\)]*)\)', value)
                    if (match) :
                        function = match.group(1)
                        args = match.group(2)
                        
                        if (function == 'now') :
                            if (row[k]['dateTimeFormat'] == 'unixtime') :
                                v['Value'] = '%i' % time.mktime(datetime.datetime.now(tz=pytz.utc).timetuple())
                            else :
                                v['Value'] = datetime.datetime.now(tz=pytz.utc).strftime(row[k]['dateTimeFormat'])
                                
                        elif (function == 'countOfIndicators') :
                            v['Value'] = str(TransformedData['IndicatorData'].__len__())
                            
                        elif (function == 'LQMT_determineIndicatorType') :
                            
                            # TODO: It would be great if somehow we could query the ontology to get this.
                            
                            v['Value'] = None
                            
                            if (args == 'indicator') :
                                indicatorType = row['IndicatorType']
                                
                                if (indicatorType == 'IPv4-Address-Block') :
                                    v['Value'] = 'IPv4Address'
                                elif (indicatorType == 'IPv6-Address-Block') :
                                    v['Value'] = 'IPv6Address'
                                elif (indicatorType == 'DNS-Hostname-Block') :
                                    v['Value'] = 'DNSDomainName'
                                elif (indicatorType == 'URL-Block') :
                                    v['Value'] = 'URL'
                                elif (indicatorType == 'Malicious-Email-Block') :
                                    pass
                                elif (indicatorType == 'Malicious-File-IOC') :
                                    pass
                                elif (indicatorType == 'Registry-Key-IOC') :
                                    pass
                                elif (indicatorType == 'Mutex-IOC') :
                                    pass
                            
                            if (v['Value'] is None) :
                                # Indicator type not found, try additional matches
                                indicatorDataType = row[args]['datatype']
                                
                                if (indicatorDataType == 'ipv4') :
                                    v['Value'] = 'IPv4Address'
                                elif (indicatorDataType == 'ipv6') :
                                    v['Value'] = 'IPv6Address'
                                elif (indicatorDataType == 'emailAddress') :
                                    v['Value'] = 'EmailAddress'
                                elif (indicatorDataType == 'string') :
                                    indicatorValue = row[args]['Value']
                                    if (re.match(r'^((\d){1,3}\.){3}(\d){1,3}$', indicatorValue)) :
                                        v['Value'] = 'IPv4Address'
                                    elif (re.match(r'^[a-fA-F0-9]+:+[a-fA-F0-9:]+$', indicatorValue)) :
                                        v['Value'] = 'IPv6Address'
                                    elif (re.match(r'^([a-z0-9][^./]+\.)+[a-z]+$', indicatorValue)) :
                                        v['Value'] = 'DNSDomainName'
                                    elif (re.match(r'^((ft|htt)ps?://)?([a-z][^./]+\.)+[a-z]+/.*$', indicatorValue)) :
                                        v['Value'] = 'URL'
                                    
                            if (v['Value'] is None) :
                                # Still didn't find an indicator type, throw exception
                                raise Exception('unknownIndicatorType', 'Indicator type could not be determined for data: %s' % row[args]['Value'])
                            
                        elif (function == 'CFM13_earliestIndicatorTime') :
                            # For now this function is specific to CFM13, it could be made generic if needed in other Schemas
                            mintime = None
                            for subrow in TransformedData['IndicatorData'] :
                                if ('create_time' in subrow) :
                                    indicatorTime = datetime.datetime.strptime(subrow['create_time']['Value'], '%Y-%m-%dT%H:%M:%S%z')
                                    if (mintime is None or mintime > indicatorTime) :
                                        mintime = indicatorTime
                
                            if (mintime is not None) :            
                                v['Value'] = mintime.strftime('%Y-%m-%dT%H:%M:%S%z')
                            else :
                                v['Value'] = TransformedData['DocumentHeaderData']['analyzer_time']['Value']
                                
                                
                        elif (function == 'CFM20_determineIndicatorConstraint') :
                            # TODO: It would be great if somehow we could query the ontology to get this.
                            
                            v['Value'] = None
                            
                            if (args in row and 'Value' in row[args]) :
                                indicatorValue = row[args]['Value']
                                indicatorOntology = row[args]['matchedOntology']
                                
                                if (indicatorOntology == 'http://www.anl.gov/cfm/transform.owl#FilenameIndicatorValueSemanticConcept') :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#StringValueMatch'
                                elif (re.match(r'^((\d){1,3}\.){3}(\d){1,3}$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#IPv4DottedDecimalEquality'
                                elif (re.match(r'^[a-fA-F0-9]+:+[a-fA-F0-9:]+$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#IPv6ColonHexEquality'
                                elif (re.match(r'^([a-z0-9][^./]+\.)+[a-z]+$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#DNSDomainNameMatch'
                                elif (re.match(r'^((ft|htt)ps?://)?([a-z][^./]+\.)+[a-z]+/.*$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#URLMatch'
                                elif (re.match(r'^[a-fA-F0-9]{32}$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#MD5Equality'
                                elif (re.match(r'^\d+$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#IntegerEquality'

                                    
                                    
                                    
                            if (v['Value'] is None) :
                                # Still didn't find an indicator type, throw exception
                                raise Exception('unknownIndicatorConstraint', 'CFM 2.0 Indicator constraint could not be determined for data: %s' % row[args]['Value'])
                                
                        elif (function == 'CFM20_determineIndicatorType') :
                            # TODO: It would be great if somehow we could query the ontology to get this.
                            
                            v['Value'] = None
                            
                            if (args in row and 'Value' in row[args]) :
                                indicatorValue = row[args]['Value']
                                indicatorOntology = row[args]['matchedOntology']
                                
                                if (indicatorOntology == 'http://www.anl.gov/cfm/transform.owl#FilenameIndicatorValueSemanticConcept') :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#FileName'
                                elif (re.match(r'^((\d){1,3}\.){3}(\d){1,3}$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#IPv4Address'
                                elif (re.match(r'^[a-fA-F0-9]+:+[a-fA-F0-9:]+$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#IPv6Address'
                                elif (re.match(r'^([a-z0-9][^./]+\.)+[a-z]+$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#DNSDomainName'
                                elif (re.match(r'^((ft|htt)ps?://)?([a-z][^./]+\.)+[a-z]+/.*$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#URL'
                                elif (re.match(r'^[a-fA-F0-9]{32}$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#FileMD5Hash'
                                elif (re.match(r'^\d+$', indicatorValue)) :
                                    v['Value'] = 'http://www.anl.gov/cfm/2.0/current/#FileSizeBytes'
                                
                            if (v['Value'] is None) :
                                # Still didn't find an indicator type, throw exception
                                raise Exception('unknownIndicatorType', 'CFM 2.0 Indicator type could not be determined for data: %s' % row[args]['Value'])
                                
                        elif (function == 'generate_uuid') :
                            v['Value'] = str(uuid.uuid4())
                        
                        else :
                            raise Exception('undefinedFunction', 'The function %s is not defined in the code' % function)
    
    @classmethod
    def FlattenDict(cls, NestedDict, ParentKey='', Sep=';'):
        '''
        Takes a nested dictionary, and rewrites it to a flat dictionary, where each nested key is appended to the
        top level key name, separated with Sep
        '''
        
        items = []
        for k, v in NestedDict.items():
            new_key = ParentKey + Sep + k if ParentKey else k
            if (isinstance(v, collections.MutableMapping)) :
                items.extend(SchemaParser.FlattenDict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @classmethod
    def UnflattenDict(cls, FlatDict, Sep=';'):
        '''
        Reverse the FlattenDict action and expand the dictionary back out
        '''
        
        ud = {}
        for k, v in FlatDict.items():
            context = ud
            for sub_key in k.split(Sep)[:-1]:
                if sub_key not in context:
                    context[sub_key] = {}
                context = context[sub_key]
            context[k.split(Sep)[-1]] = v
        return ud