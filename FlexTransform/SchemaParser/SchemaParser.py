'''
Created on Oct 13, 2014

@author: ahoying
'''

import collections
import datetime
import logging
import re
import socket

import pytz
import time
# import dumper
import copy
from builtins import str
from FlexTransform.SchemaParser.TransformFunctions import TransformFunctionManager


# from _sqlite3 import Row

class SchemaParser(object):
    '''
    Base class for the Schema Parser logic.  The following fields are defined for this class:

    * self.SchemaConfig - The schema configuration for the target format
    * self._ValueMap - Mapping from the valuemap specification to the JSON config item that defines
                      it (or items)
    * self._FieldOrder - Ordered list of field names used to process the fields in the schema based on their relationship to each other.
    * self._outputFormatRE -  Regex used to parse the outputFormat field
                              Example outputFormat: "[comment], direction:[direction], 
                                                     confidence:[confidence], severity:[severity]"
    * self.logging - The logging object
    '''

    # Class global variables
    _outputFormatRE = re.compile(r"([^\[]+)?(?:\[([^\]]+)\])?")

    def __init__(self, config):
        '''
        Constructor
        '''
        self.SchemaConfig = config

        self._FieldOrder = self._CalculateSchemaFieldOrder()

        self.FunctionManager = TransformFunctionManager()

        # TODO: Create a JSON schema document and validate the config against the schema. Worst case, define accepted tags and validate there are no unknown tags.

        self.logging = logging.getLogger('FlexTransform.SchemaParser')

    def MapDataToSchema(self, SourceData, oracle=None):
        '''
        Maps the values in SourceData to the underlying schema from the config
        Parameters:
        * SourceData -
        * oracle - An instance of the OntologyOracle to build an ABOX for the source data
                   Assumes the oracle has been initialized with a FlexTransform TBOX

        TODO: Create an ABOX (using the Ontology Oracle) to represent the source file; this will also inform the
              target production, as data will be requested from the ABOX.
              
              Essentially this will consist of creating instances of the appropriate subclasses in an ABOX.
        '''

        # The value map is only used by the _MapRowToSchema function, so it isn't calculated until this method is called and not under __init__()
        self._ValueMap = self._ValuemapToField()

        self.MappedData = {}

        rowTypes = []

        if ('IndicatorData' in SourceData):
            rowTypes.append('IndicatorData')
        if ('DocumentHeaderData' in SourceData):
            rowTypes.append('DocumentHeaderData')

        for rowType in rowTypes:
            if (rowType in self.SchemaConfig):
                if (isinstance(SourceData[rowType], list)):
                    self.MappedData[rowType] = []
                    for row in SourceData[rowType]:
                        if (isinstance(row, dict)):
                            try:
                                DataRow = self._MapRowToSchema(SchemaParser.FlattenDict(row), rowType)
                                self.MappedData[rowType].append(DataRow)
                            except Exception as inst:
                                self.logging.error(inst)
                                # self.logging.debug(str(SchemaParser.FlattenDict(row)))
                        else:
                            raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
                elif (isinstance(SourceData[rowType], dict)):
                    DataRow = self._MapRowToSchema(SchemaParser.FlattenDict(SourceData[rowType]), rowType)
                    self.MappedData[rowType] = DataRow
                else:
                    raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            else:
                raise Exception('SchemaConfigNotFound', 'Data Type: ' + rowType)

        ## Let's start here.  Build an ABOX:
        '''
        if not oracle is None:
            for dataType in self.MappedData:
                for concept in self.MappedData[dataType]:
                    if isinstance(concept,dict) :
                        toProcess = concept
                        keylist = concept.keys()
                    elif isinstance(concept,str) :
                        toProcess = self.MappedData[dataType]
                        keylist = [concept]
                    for key in keylist:
                        if not isinstance(toProcess[key], dict) :
                            logging.warning("Found a MappingData element which is not a dict: {0} :: {1}".format(key, dumper.dump(toProcess[key])))
                            continue
                        if toProcess[key]["ontologyMappingType"] == "enum":
                            # TODO: Deal w/ enum types
                            logging.warning("Found enum ontology mapping: {0}".format(
                                            key))
                            continue
                        if not toProcess[key]["ontologyMappingType"] == "simple":
                            logging.warning("Found non-simple ontology mapping: {0} :: {1}".format(
                                            key, 
                                            dumper.dump(toProcess[key])))
                            continue
                        oracle.addSemanticComponentIndividual(
                                        toProcess[key]["ontologyMapping"],
                                        toProcess[key]["Value"])
            logging.debug(oracle.dumpGraph())
        '''

        return self.MappedData

    def MapMetadataToSchema(self, sourceMetaData):
        '''
        Add meta data to the MappedData
        '''

        if ('DocumentMetaData' in self.SchemaConfig):
            if (isinstance(sourceMetaData, dict)):
                DataRow = self._MapRowToSchema(SchemaParser.FlattenDict(sourceMetaData), 'DocumentMetaData')
                self.MappedData['DocumentMetaData'] = DataRow
            else:
                raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
        else:
            raise Exception('SchemaConfigNotFound', 'Data Type: DocumentMetaData')

    def TransformData(self, MappedData, oracle=None):
        '''
        Takes the data that was mapped to the source schema and transform it using the target schema
        Parameters:
        * MappedData - The data mapped from the source document
        * oracle - An instance of the OntologyOracle class which encapsulates the target schema ontology
                   If 'None', will not be used.
        '''
        self.TransformedData = {}

        # If the oracle is set, initialize it:
        if oracle is not None:
            oracle.buildABOX(MappedData)

        # Parse indicators before headers
        rowTypes = []

        DocumentHeaderData = None
        DocumentMetaData = None

        if ('IndicatorData' in self.SchemaConfig.keys()):
            rowTypes.append('IndicatorData')
        if ('DocumentHeaderData' in self.SchemaConfig.keys()):
            rowTypes.append('DocumentHeaderData')

        if ('DocumentHeaderData' in MappedData):
            DocumentHeaderData = MappedData['DocumentHeaderData']

        if ('DocumentMetaData' in MappedData):
            DocumentMetaData = MappedData['DocumentMetaData']

        for rowType in rowTypes:
            if (rowType in MappedData):
                if (isinstance(MappedData[rowType], list)):
                    self.TransformedData[rowType] = []
                    for row in MappedData[rowType]:
                        if (isinstance(row, dict)):
                            try:
                                self.TransformedData[rowType].append(
                                    self._TransformDataToNewSchema(rowType, row, DocumentHeaderData, DocumentMetaData,
                                                                   oracle))
                            except Exception as inst:
                                self.logging.error(inst)
                        else:
                            raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")

                elif (isinstance(MappedData[rowType], dict)):
                    self.TransformedData[rowType] = self._TransformDataToNewSchema(rowType, MappedData[rowType], None,
                                                                                   DocumentMetaData, oracle)
                else:
                    raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            else:
                self.TransformedData[rowType] = self._TransformDataToNewSchema(rowType, None, None, DocumentMetaData,
                                                                               oracle)

        return self.TransformedData

    def _ValuemapToField(self):
        '''
        Create a fast lookup dictionary for mapping values from flattened dictionaries back to the schema field
        '''

        ValueMap = {}

        for rowType in self.SchemaConfig:
            ValueMap[rowType] = {}
            if ('fields' in self.SchemaConfig[rowType] and isinstance(self.SchemaConfig[rowType]['fields'], dict)):
                for fieldName, fieldDict in self.SchemaConfig[rowType]['fields'].items():
                    if ('valuemap' in fieldDict):
                        ValueMap[rowType][fieldDict['valuemap']] = fieldName
                    if ('additionalValuemaps' in fieldDict):
                        for valuemap in fieldDict['additionalValuemaps']:
                            ValueMap[rowType][valuemap] = fieldName

        return ValueMap

    def _CalculateSchemaFieldOrder(self):
        '''
        Sorts the schema fields from the first fields that must be processed to the last based on the relationships between the fields.
        Caches the data so that this only has to be determined the first time.
        
        Returns a list with the fields in order.
        '''
        # TODO: Can this be cached offline so it is loaded between runs so long as the schema .json files don't change?
        SchemaFieldOrder = {}

        for rowType in self.SchemaConfig:
            SchemaFieldOrder[rowType] = []

            FieldOrder = {}

            for field, fieldDict in self.SchemaConfig[rowType]['fields'].items():
                if ('datatype' in fieldDict and fieldDict['datatype'] == "group"):
                    # Groups need to be processed last by the transform engine
                    if (field not in FieldOrder or FieldOrder[field] < 10):
                        FieldOrder[field] = 10

                    # Handle subgroups, parent group needs to be processed after all child groups
                    if ('memberof' in fieldDict):
                        if (fieldDict['memberof'] not in FieldOrder or FieldOrder[fieldDict['memberof']] <= FieldOrder[
                            field]):
                            FieldOrder[fieldDict['memberof']] = FieldOrder[field] + 1

                elif ('required' in fieldDict and fieldDict['required'] == True):
                    if (field not in FieldOrder or FieldOrder[field] > 1):
                        FieldOrder[field] = 1
                elif ('memberof' in fieldDict):
                    if (field not in FieldOrder or FieldOrder[field] > 5):
                        FieldOrder[field] = 5
                        if (fieldDict['memberof'] not in FieldOrder or FieldOrder[fieldDict['memberof']] <= FieldOrder[
                            field]):
                            FieldOrder[fieldDict['memberof']] = FieldOrder[field] + 1
                elif ('dependsOn' in fieldDict):
                    if (field not in FieldOrder or FieldOrder[field] < 6):
                        FieldOrder[field] = 6
                else:
                    if (field not in FieldOrder or FieldOrder[field] > 4):
                        FieldOrder[field] = 4

            # Run through all the fields again and re-order based on references        
            for field, fieldDict in self.SchemaConfig[rowType]['fields'].items():
                if ('defaultValue' in fieldDict and fieldDict['defaultValue'].startswith('&')):
                    match = re.match(r'&([^\(]+)\(([^\)]*)\)', fieldDict['defaultValue'])
                    if (match):
                        args = match.group(2)
                        if (args and args in self.SchemaConfig[rowType]['fields']):
                            if (field in FieldOrder and (
                                    args not in FieldOrder or FieldOrder[args] >= FieldOrder[field])):
                                FieldOrder[field] = FieldOrder[args] + 1

                elif ('outputFormat' in fieldDict):
                    match = self._outputFormatRE.findall(fieldDict['outputFormat'])
                    if (match):
                        for m in match:
                            if (m[1] != ''):
                                if (m[1] in self.SchemaConfig[rowType]['fields']):
                                    if (field in FieldOrder and (
                                            m[1] not in FieldOrder or FieldOrder[m[1]] >= FieldOrder[field])):
                                        FieldOrder[m[1]] = FieldOrder[field] - 1

                    if ('outputFormatCondition' in fieldDict):
                        match = self._outputFormatRE.findall(fieldDict['outputFormatCondition'])
                        if (match):
                            for m in match:
                                if (m[1] != ''):
                                    if (m[1] in self.SchemaConfig[rowType]['fields']):
                                        if (field in FieldOrder and (
                                                m[1] not in FieldOrder or FieldOrder[m[1]] >= FieldOrder[field])):
                                            FieldOrder[m[1]] = FieldOrder[field] - 1

                if (field in FieldOrder):
                    if ('requiredIfReferenceField' in fieldDict):
                        if (fieldDict['requiredIfReferenceField'] not in FieldOrder):
                            FieldOrder[fieldDict['requiredIfReferenceField']] = FieldOrder[field] - 1
                        elif (FieldOrder[fieldDict['requiredIfReferenceField']] >= FieldOrder[field]):
                            FieldOrder[field] = FieldOrder[fieldDict['requiredIfReferenceField']] + 1

                    if ('ontologyMappingType' in fieldDict and fieldDict['ontologyMappingType'] == 'referencedEnum'):
                        if (fieldDict['ontologyEnumField'] not in FieldOrder):
                            FieldOrder[fieldDict['ontologyEnumField']] = FieldOrder[field] - 1
                        elif (FieldOrder[fieldDict['ontologyEnumField']] >= FieldOrder[field]):
                            FieldOrder[field] = FieldOrder[fieldDict['ontologyEnumField']] + 1

                    if ('dependsOn' in fieldDict):
                        if (fieldDict['dependsOn'] not in FieldOrder):
                            FieldOrder[fieldDict['dependsOn']] = FieldOrder[field] - 1
                        elif (FieldOrder[fieldDict['dependsOn']] >= FieldOrder[field]):
                            FieldOrder[field] = FieldOrder[fieldDict['dependsOn']] + 1

                    if ('fields' in fieldDict):
                        requiredFields = fieldDict['fields']
                        for requiredField in requiredFields:
                            if (requiredField not in FieldOrder):
                                FieldOrder[requiredField] = FieldOrder[field] - 1
                            elif (FieldOrder[requiredField] >= FieldOrder[field]):
                                FieldOrder[field] = FieldOrder[requiredField] + 1

            SchemaFieldOrder[rowType].extend(sorted(FieldOrder, key=FieldOrder.get))

        return SchemaFieldOrder

    def _MapRowToSchema(self, DataRow, rowType, SubGroupedRow=False):
        '''
        Create a new dictionary with the mapping between the data row and the schema field definition
        Parameters:
          * DataRow - The specification of data which will be the source for this mapping
          * rowType - Either DocumentHeaderData, DocumentMetaData or IndicatorData.
          * SubGroupedRow - Set to true if this is processing a subgrouped row and not the primary data row
        '''

        newDict = {}
        processedFields = {}

        if ('IndicatorType' in DataRow):
            newDict['IndicatorType'] = DataRow['IndicatorType']

        ValueMap = self._ValueMap[rowType]

        # Get the field dependency order for processing the source schema
        FieldOrder = self._FieldOrder[rowType]

        for field in FieldOrder:
            fieldDict = self.SchemaConfig[rowType]['fields'][field]
            mappedField = None

            if (field in DataRow):
                mappedField = field

            if (not mappedField and 'valuemap' in fieldDict):
                if (fieldDict['valuemap'] in DataRow):
                    mappedField = fieldDict['valuemap']

            if (not mappedField and 'additionalValuemaps' in fieldDict):
                for valuemap in fieldDict['additionalValuemaps']:
                    if (valuemap in DataRow):
                        mappedField = valuemap
                        break

            if (mappedField is not None):

                processedFields[mappedField] = True

                if ('ignore' in fieldDict and fieldDict['ignore'] == True):
                    continue

                elif ('error' in fieldDict):
                    raise Exception("InvalidSchemaMapping", fieldDict['error'])

                if ('dependsOn' in fieldDict):
                    # If the field this field depends on does not exist, then don't add to new dictionary
                    dependsOn = fieldDict['dependsOn']
                    if (dependsOn not in newDict or 'Value' not in newDict[dependsOn]):
                        continue

                newDict[field] = fieldDict.copy()
                Value = DataRow[mappedField]

                if (isinstance(Value, list) and
                            'multiple' in fieldDict and
                            fieldDict['multiple'] == True):

                    if (fieldDict['datatype'] == 'group'):

                        # This processes instances where the same field grouping may exist multiple times in a single indicator

                        newDataRow = {}

                        subfields = fieldDict['subfields']

                        # GroupID is a reference ID to fields that were grouped together in the source document, so they can be processed together in the target document
                        GroupID = 0

                        for row in Value:
                            if (isinstance(row, dict)):
                                subRow = SchemaParser.FlattenDict(row, ParentKey=mappedField)

                                for (subkey, subvalue) in subRow.items():
                                    if (subkey in ValueMap and ValueMap[subkey] not in subfields):
                                        raise Exception('FieldNotAllowed',
                                                        'Field %s is not an allowed subfield of %s' % (
                                                        ValueMap[subkey], field))

                                    newDataRow[subkey] = subvalue

                                subDict = self._MapRowToSchema(newDataRow, rowType, SubGroupedRow=True)
                                newDict.update(self._UpdateFieldReferences(subDict, GroupID, subfields))
                                GroupID = GroupID + 1

                            else:
                                raise Exception('DataError',
                                                'Data type of sub row for %s is not dict: %s' % (mappedField, row))

                        # Value could be set to any string, it isn't used for field groups except to indicate that the group has been parsed
                        newDict[field]['Value'] = 'True'
                    else:
                        if (Value.__len__() > 1):
                            newDict[field]['AdditionalValues'] = []
                        for d in Value:
                            if (isinstance(d, (list, dict))):
                                self.logging.warning(
                                    '%s subvalue in the list is another list or dictionary, not currently supported: %s',
                                    mappedField, d)
                                continue

                            if ('Value' not in newDict[field]):
                                # Put the first value in Value and the rest into AdditionalValues
                                newDict[field]['Value'] = str(d)
                            else:
                                newDict[field]['AdditionalValues'].append(str(d))

                elif (isinstance(Value, (list, dict))):
                    self.logging.warning('%s value is a list or dictionary, not currently supported: %s', mappedField,
                                         Value)
                    continue
                elif (isinstance(Value, str)):
                    # The rstrip is to get rid of rogue tabs and white space at the end of a value, a frequent problem with STIX formated documents in testing
                    newDict[field]['Value'] = str.rstrip(Value)
                else:
                    newDict[field]['Value'] = str(Value)

                # Process the regexSplit directive
                if ('regexSplit' in fieldDict):
                    match = re.match(fieldDict['regexSplit'], newDict[field]['Value'])
                    if match:
                        regexFields = re.split(',\s+', fieldDict['regexFields'])
                        i = 0
                        while (i < regexFields.__len__()):
                            if (match.group(i + 1)):
                                newFieldName = regexFields[i]
                                newFieldValue = match.group(i + 1)
                                newDict[newFieldName] = self.SchemaConfig[rowType]['fields'][newFieldName].copy()
                                newDict[newFieldName]['Value'] = newFieldValue

                                self._ValidateField(newDict[newFieldName], newFieldName, rowType)
                            i += 1

                self._ValidateField(newDict[field], field, rowType)

            elif (not SubGroupedRow):
                # Check if there is a default value

                # No mapped data found, check if the field is required and if so if there is a default value
                # Raise an exception if a required field has no data
                required = False
                ReferenceField = None

                if ('requiredIfReferenceField' in fieldDict):
                    ReferenceField = fieldDict['requiredIfReferenceField']
                    if ('requiredIfReferenceValues' in fieldDict):
                        ReferenceValues = fieldDict['requiredIfReferenceValues']
                        for val in ReferenceValues:
                            if (
                                        (ReferenceField in newDict and val == newDict[ReferenceField]['Value']) or
                                        (val == '' and (
                                            not ReferenceField in newDict or not newDict[ReferenceField]['Value']))):
                                required = True
                                break

                    elif ('requiredIfReferenceValuesMatch' in fieldDict):
                        if (ReferenceField in newDict):
                            ReferenceValuesMatch = fieldDict['requiredIfReferenceValuesMatch']
                            for val in ReferenceValuesMatch:
                                if (val == '*'):
                                    if ('Value' in newDict[ReferenceField]):
                                        required = True
                                        break
                                elif (val.endswith('*')):
                                    if ('Value' in newDict[ReferenceField] and newDict[ReferenceField][
                                        'Value'].startswith(val.strip('*'))):
                                        required = True
                                        break

                if (required == True or ('required' in fieldDict and fieldDict['required'] == True)):
                    if ('defaultValue' in fieldDict):
                        newDict[field] = fieldDict.copy()
                        newDict[field]['Value'] = fieldDict['defaultValue']

                        if (newDict[field]['Value'].startswith('&')):
                            newDict[field]['Value'] = self._CalculateFunctionValue(newDict[field]['Value'], field,
                                                                                   newDict[field], rowType, newDict,
                                                                                   IndicatorType=None,
                                                                                   TransformedData=self.MappedData)

                        self._ValidateField(newDict[field], field, rowType)

                    elif ('outputFormat' in fieldDict):
                        Value = self._BuildOutputFormatText(fieldDict, newDict)
                        if (Value):
                            newDict[field] = fieldDict.copy()
                            newDict[field]['Value'] = Value

                        self._ValidateField(newDict[field], field, rowType)

                    elif ('datatype' in fieldDict and fieldDict['datatype'] == 'group'):
                        if ('memberof' in fieldDict):
                            self.logging.warning(
                                "Sub-groups should not have 'required' set to true, processing skipped: %s", field)
                        else:
                            groupRow = {'fields': {}}
                            self._BuildFieldGroup(None, newDict, rowType, field, groupRow, None)

                    else:
                        raise Exception('NoDefaultValue',
                                        'Default Value or outputFormat not defined for required field %s' % field)

        if (not SubGroupedRow):
            for field in DataRow:
                if (field not in processedFields):
                    self.logging.warning('%s not processed for row type %s in schema config. Value: %s', field, rowType,
                                         DataRow[field])

            if (rowType == "IndicatorData"):
                self._AddIndicatorType(newDict)

        return newDict

    def _UpdateFieldReferences(self, subDict, GroupID, subfields):
        '''
        Update any key or value that equals one of the subfields with the name subfield_GroupID
        '''

        if (GroupID):
            # Only rename entries if GroupID is > 0
            for (k, v) in subDict.items():
                if (isinstance(v, dict)):
                    self._UpdateFieldReferences(v, GroupID, subfields)
                elif (isinstance(v, str)):
                    if (v in subfields):
                        subDict[k] = "%s_%i" % (v, GroupID)

        for k in subfields:
            if (k in subDict):
                if (GroupID):
                    # Only rename entries if GroupID is > 0
                    v = subDict.pop(k)
                    k = "%s_%i" % (k, GroupID)
                    subDict[k] = v
                subDict[k]['groupID'] = GroupID

        return subDict

    def _AddIndicatorType(self, newDict):
        '''
        Determine the indicator type from the data and add a new field IndicatorType to the data row
        '''
        if ("types" not in self.SchemaConfig["IndicatorData"]):
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

        for indicatorType, indicatorMatches in self.SchemaConfig["IndicatorData"]["types"].items():
            for indicatorMatch in indicatorMatches:
                match = False
                Weight = 0
                for k, v in indicatorMatch.items():
                    matchKeys = {}

                    if (k in newDict and 'Value' in newDict[k]):
                        matchKeys[k] = [newDict[k]['Value']]

                        prefix = "%s_" % k
                        for key in newDict:
                            if key.startswith(prefix):
                                if (k not in matchKeys):
                                    matchKeys[k] = []
                                matchKeys[k].append(newDict[key]['Value'])

                    if (len(matchKeys) > 0):
                        submatch = False
                        for key, values in matchKeys.items():
                            for value in values:
                                if (v == "*" and value != ""):
                                    Weight += 1
                                    submatch = True
                                elif (v.endswith("*") and value.startswith(v.strip("*"))):
                                    Weight += 5
                                    submatch = True
                                elif (value == v):
                                    Weight += 10
                                    submatch = True

                        if (submatch):
                            match = True
                        else:
                            match = False
                            Weight = 0
                            break

                    elif (v == ""):
                        Weight += 5
                        match = True
                    else:
                        match = False
                        Weight = 0
                        break

                if (match and Weight > bestWeight):
                    bestMatch = indicatorType
                    bestWeight = Weight

        if (bestMatch is not None):
            newDict["IndicatorType"] = bestMatch
        else:
            raise Exception("NoMatchingIndicatorType",
                            'This "{}" indicator data row does not match any defined indicator types'.format(key))

    def _ValidateField(self, fieldDict, fieldName, rowType):
        '''
        Validate the schema configuration for the field passes
        '''

        # Regexes used for validation

        # This is a pretty simple regex, but it should work in most cases. Might need to be replaced with something more sophisticated
        EMAIL_REGEX = re.compile("^[^@]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}$")

        # Validate the dataType matches the value
        dataType = fieldDict['datatype']

        values = []
        if ('Value' in fieldDict):
            if (fieldDict['Value'].startswith('&')):
                raise Exception('ValueIsFunction',
                                'Value for field %s maps to a function which should already have been processed: %s' % (
                                fieldName, fieldDict['Value']))

            values.append(fieldDict['Value'])

        if ('AdditionalValues' in fieldDict):
            values.extend(fieldDict['AdditionalValues'])

        if (values.__len__() == 0):
            raise Exception('NoValue', 'Field %s has no value' % fieldName)

        # TODO: ParsedValue only contains the last tested value if there are multiple values for the field. This might be a problem for some data types.

        for value in values:
            if (dataType == 'string'):
                # String data type is always valid, pass
                pass
            elif (dataType == 'group'):
                # Group data type is always valid, pass
                pass
            elif (dataType == 'int'):
                fieldDict['ParsedValue'] = int(value)
                if (str(fieldDict['ParsedValue']) != value):
                    raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not an int: ' + value)
                if ('dataRange' in fieldDict):
                    datarange = fieldDict['dataRange'].split('-')
                    if (fieldDict['ParsedValue'] < int(datarange[0]) or fieldDict['ParsedValue'] > int(datarange[1])):
                        raise Exception('DataOutOfRange',
                                        'The value for field ' + fieldName + ' is outside of the allowed range(' +
                                        fieldDict['dataRange'] + '): ' + value)
            elif (dataType == 'datetime'):
                # TODO: Support multiple date time formats
                if ('dateTimeFormat' not in fieldDict):
                    raise Exception('SchemaConfigMissing',
                                    'The dateTimeFormat configuration is missing for field ' + fieldName)
                try:
                    if (fieldDict['dateTimeFormat'] == "unixtime"):
                        fieldDict['ParsedValue'] = pytz.utc.localize(datetime.datetime.utcfromtimestamp(int(value)))
                    else:
                        # This is a very poor hack to force the weird STIX time format from the CISCP reports with timezone as [+-]xx:yy to the standard [+-]xxyy format.
                        # TODO: Have something in the json config that forces this conversion, and can undo it on write if needed. Possibly use pytz to fix the issue
                        match = re.match(r"(.*)([+-]\d\d):(\d\d)$", value)
                        if (match):
                            value = match.group(1) + match.group(2) + match.group(3)
                        match = re.match(r"(.*)\.\d+([+-]\d\d\d\d)$", value)
                        if (match):
                            value = match.group(1) + match.group(2)
                        fieldDict['ParsedValue'] = datetime.datetime.strptime(value, fieldDict['dateTimeFormat'])

                        # TODO: replace this
                        if fieldDict['ParsedValue'].tzinfo is None:
                            fieldDict['ParsedValue'] = fieldDict['ParsedValue'].replace(tzinfo=pytz.UTC)
                except Exception as inst:
                    self.logging.error(inst)
                    raise Exception('DataTypeInvalid',
                                    'Value for field ' + fieldName + ' is not a valid date time value: ' + value)
            elif (dataType == 'enum'):
                if (value not in fieldDict['enumValues']):
                    # Check if there is a case mismatch, update the value to the correct case if there is.
                    caseUpdated = False
                    for k in fieldDict['enumValues']:
                        if (value.lower() == k.lower()):
                            fieldDict['Value'] = k
                            caseUpdated = True
                            break

                    if (not caseUpdated):
                        raise Exception('DataTypeInvalid',
                                        'Value for field ' + fieldName + ' is not listed in the enum values: ' + value)
            elif (dataType == 'emailAddress'):
                if (EMAIL_REGEX.match(value) is None):
                    raise Exception('DataTypeInvalid',
                                    'Value for field ' + fieldName + ' is not a valid email address: ' + value)
            elif (dataType == 'ipv4'):
                try:
                    fieldDict['ParsedValue'] = socket.inet_aton(value)
                except:
                    raise Exception('DataTypeInvalid',
                                    'Value for field ' + fieldName + ' is not a valid ipv4 address: ' + value)
            elif (dataType == 'ipv6'):
                try:
                    fieldDict['ParsedValue'] = socket.inet_pton(socket.AF_INET6, value)
                except:
                    raise Exception('DataTypeInvalid',
                                    'Value for field ' + fieldName + ' is not a valid ipv6 address: ' + value)
            else:
                self.logging.error("No validation written for dataType: %s", dataType)

        return

    def _TransformDataToNewSchema(self, rowType, DataRow, DocumentHeaderData, DocumentMetaData, oracle=None):
        '''
        Transform the data row using the underlying ontology mappings to the new schema
        Parameters:
        * rowType
        * DataRow
        * DocumentHeader
        * DocumentMetadata
        * oracle - An instance of the OntologyOracle class which encapsulates the target schema ontology
                   If 'None', will not be used.

        TODO: Update to query ontology directly
        '''

        # newDict stores the transformed data mapped into the target schema for this row
        newDict = {}
        IndicatorType = None

        if (rowType == 'IndicatorData'):

            # Determine if the target schema accepts Indicators of type IndicatorType
            if ('IndicatorType' in DataRow):
                IndicatorType = DataRow.pop('IndicatorType')

                # TODO: Update to query the ontology for supported indicator types
                if (IndicatorType not in self.SchemaConfig["IndicatorData"]["types"]):
                    # Determine if the ontology contains a supported concept which is a parent or child of this type.
                    newIndicatorType = None
                    '''
                    if oracle is not None:
                        altResult = oracle.getIndicatorTypeAlternative(IndicatorType)
                        if altResult is not None:
                            newIndicatorType = altResult.getAlternative()
                            logging.warn("No direct mapping from source concept {0} to target schema.  Found a {1} of the concept ({2}).".format(IndicatorType, altResult.getLossType(), newIndicatorType))
                    '''
                    if newIndicatorType is not None:
                        IndicatorType = newIndicatorType
                    else:
                        raise Exception("UnknownIndicatorType",
                                        "The Indicator Type {0} is not known by the target schema".format(
                                            IndicatorType))

                # Carry the indicator type forward to the target schema
                newDict['IndicatorType'] = IndicatorType

        # Build a quick lookup dictionary of Ontology concepts to data from the source document
        DataDictionary = self._MapDataToOntology(DataRow, DocumentHeaderData, DocumentMetaData)

        # Build the dependency order for processing the target schema
        FieldOrder = self._FieldOrder[rowType]

        GroupRows = {}

        for field in FieldOrder:
            # Iterate over each field in the target file schema, copying in data from the source as it is available.
            fieldDict = self.SchemaConfig[rowType]['fields'][field].copy()

            OntologyReferences = collections.defaultdict(list)
            OntologyReference = None

            # TODO: Chris - this is the code that should be replaced or supplemented with the Ontology Oracle
            if ('ontologyMappingType' in fieldDict):
                if (fieldDict['ontologyMappingType'] == 'none'):
                    if ('datatype' in fieldDict and fieldDict['datatype'] == 'group'):
                        if (field in GroupRows):
                            groupRow = GroupRows.pop(field)
                            #  -- Modifies 'newDict'[group] to contain values from source document
                            #     depending on mapping.
                            self._BuildFieldGroup(DataDictionary, newDict, rowType, field, groupRow, IndicatorType)
                            continue

                elif (fieldDict['ontologyMappingType'] == 'simple'):
                    if (fieldDict['ontologyMapping'] != ''):
                        # Get the ontology reference we need in the destination schema:
                        OntologyReference = fieldDict['ontologyMapping']
                        if OntologyReference in DataDictionary:
                            # If the semantic value exists exactly in the data dictionary, we can use it
                            # directly; no oracle call is required.
                            OntologyReferences[OntologyReference].extend(DataDictionary[OntologyReference].keys())
                        elif oracle is not None:
                            # If we have a semantic mismatch, check the DataDictionary for ontology references which are
                            # either specializations (prefered) or generalizations of the concept.
                            # Lookup Ontology reference from the oracle instead:
                            oRefList = oracle.getCompatibleConcepts(OntologyReference)
                            for altOntologyReference in oRefList:
                                # For each possible value returned in oRefList, see if we have it in the data dictionary:
                                if altOntologyReference.IRI.__str__() in DataDictionary:
                                    OntologyReferences[OntologyReference].extend(
                                        DataDictionary[altOntologyReference.IRI.__str__()].keys())
                                    # TODO: Re-enable this when we start checking supported vs. required
                                    # else:
                                    # logging.warn("Semantic match attempt found an ontology reference not in Data Dictionary (%s)"%altOntologyReference.IRI)

                elif (fieldDict['ontologyMappingType'] == 'multiple'):
                    # In the case of multiple possible fields, look up which one(s) are present:
                    if ('ontologyMappings' in fieldDict):
                        for OntologyReference in fieldDict['ontologyMappings']:
                            # Lookup Ontology reference from the oracle instead:
                            if (OntologyReference != ''):
                                if (OntologyReference in DataDictionary):
                                    # If the semantic value exists exactly in the data dictionary, we can use it 
                                    # directly; no oracle call is required.
                                    OntologyReferences[OntologyReference].extend(
                                        DataDictionary[OntologyReference].keys())
                                else:
                                    # If we have a semantic mismatch, check the DataDictionary for ontology references which are
                                    # either specializations (prefered) or generalizations of the concept.
                                    if oracle is not None:
                                        oRefList = oracle.getCompatibleConcepts(OntologyReference)
                                        for altOntologyReference in oRefList:
                                            if altOntologyReference.IRI.__str__() in DataDictionary:
                                                logging.warn(
                                                    "Semantic mismatch detected (Type/Distance: %s/%d ; Source: %s ; Target: %s )" % (
                                                    altOntologyReference.stype, altOntologyReference.distance,
                                                    altOntologyReference.IRI, OntologyReference))
                                                OntologyReferences[OntologyReference].extend(
                                                    DataDictionary[altOntologyReference.IRI.__str__()].keys())

                elif (fieldDict['ontologyMappingType'] == 'enum'):
                    # If the destination field type is an enum, we need to determine what value to use for it
                    # based on the source's data values.  An enum ontology mapping type indicates that the value
                    # of the field carries a semantic significance, not just the field itself.                    
                    if ('enumValues' in fieldDict):
                        for k, v in fieldDict['enumValues'].items():
                            if (v['ontologyMapping'] != ''):
                                OntologyReference = v['ontologyMapping']
                                # if oracle is not None:
                                # oRefList = oracle.getCompatibleConcepts(OntologyReference)
                                # if len(oRefList) > 0 and OntologyReference in DataDictionary:
                                # OntologyReferences[OntologyReference].extend(DataDictionary[oRefList[0].IRI].keys())
                                # else:
                                if not OntologyReference in DataDictionary:
                                    # We don't have an exact match, so check the ontology for one:
                                    if oracle is not None and False:
                                        oRefList = oracle.getCompatibleConcepts(OntologyReference)
                                        for altOntologyReference in oRefList:
                                            if altOntologyReference.IRI.__str__() in DataDictionary:
                                                logging.warn(
                                                    "Semantic mismatch detected (Type/Distance: %s/%d ; Source: %s ; Target: %s )" % (
                                                    altOntologyReference.stype, altOntologyReference.distance,
                                                    altOntologyReference.IRI, OntologyReference))
                                                OntologyReference = altOntologyReference.IRI.__str__()
                                if (OntologyReference in DataDictionary):
                                    # If the ontology reference is in the DataDictionary, then it is something that is
                                    # provided by the source file
                                    if (fieldDict['datatype'] == 'enum'):
                                        # If the target file also represents this concept as an enum:
                                        OntologyReferences[OntologyReference].append(k)
                                    else:
                                        # If the target file represents this concept as direct value:
                                        OntologyReferences[OntologyReference].extend(
                                            DataDictionary[OntologyReference].keys())
                                    continue

                                if ('reverseOntologyMappings' in v and isinstance(v['reverseOntologyMappings'], list)):
                                    # If the source only has a single concept, but the target requires several other 
                                    # schema elements to represent the concept:
                                    # Builds out a larger ontology on the target side; accommodate one-to-many
                                    for reverseMapping in v['reverseOntologyMappings']:
                                        if (reverseMapping in DataDictionary):
                                            if (fieldDict['datatype'] == 'enum'):
                                                OntologyReferences[OntologyReference].append(k)
                                            else:
                                                self.logging.warning(
                                                    'reverseOntologyMappings in field %s not supported because datatype is not enum',
                                                    k)
                                            break

                elif (fieldDict['ontologyMappingType'] == 'referencedEnum'):
                    referencedField = fieldDict['ontologyEnumField']
                    referencedValue = None

                    if ('memberof' in fieldDict):
                        # TODO: This needs to be expanded to support adding GroupIDs and mapping each referenced value if multiples exist
                        memberof = fieldDict['memberof']
                        if (memberof in GroupRows and 'fields' in GroupRows[memberof] and referencedField in
                            GroupRows[memberof]['fields']):
                            referencedValue = GroupRows[memberof]['fields'][referencedField][0]['NewValue']

                    elif (referencedField in newDict and 'Value' in newDict[referencedField]):
                        referencedValue = newDict[referencedField]['Value']

                    if (referencedValue):
                        if ('ontologyMappingEnumValues' in fieldDict):
                            if (referencedValue in fieldDict['ontologyMappingEnumValues']):
                                if (fieldDict['ontologyMappingEnumValues'][referencedValue]['ontologyMapping'] != ''):
                                    OntologyReference = fieldDict['ontologyMappingEnumValues'][referencedValue][
                                        'ontologyMapping']

                            else:
                                for eValue in fieldDict['ontologyMappingEnumValues']:
                                    if ('*' in eValue and eValue != '*' and
                                                fieldDict['ontologyMappingEnumValues'][eValue][
                                                    'ontologyMapping'] != ''):
                                        if (eValue.startswith('*')):
                                            if (referencedValue.endswith(eValue.strip('*'))):
                                                OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                    'ontologyMapping']
                                                break
                                        elif (eValue.endswith('*')):
                                            if (referencedValue.startswith(eValue.strip('*'))):
                                                OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                    'ontologyMapping']
                                                break

                            if (OntologyReference is None and "*" in fieldDict['ontologyMappingEnumValues']):
                                if (fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping'] != ''):
                                    OntologyReference = fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping']

                            # TODO: If this test fails, no direct map back to source.  Check the ontology for other options       
                            if (OntologyReference in DataDictionary):
                                OntologyReferences[OntologyReference].extend(DataDictionary[OntologyReference].keys())
                        else:
                            raise Exception('ontologyMappingEnumValues',
                                            'ontologyMappingEnumValues missing from field %s' % field)
                    elif ('ontologyMappingEnumValues' in fieldDict and '' in fieldDict['ontologyMappingEnumValues']):
                        OntologyReference = fieldDict['ontologyMappingEnumValues']['']['ontologyMapping']
                else:
                    raise Exception('UnknownOntologyMappingType',
                                    'The OntologyMappingType %s in field %s is undefined' % (
                                    fieldDict['ontologyMappingType'], field))

            else:
                raise Exception('MissingOntologyMappingType',
                                'The OntologyMappingType is missing from field %s' % field)

            if (len(OntologyReferences) == 0 and 'reverseOntologyMappings' in fieldDict):
                for reverseMapping in fieldDict['reverseOntologyMappings']:
                    if (reverseMapping in DataDictionary):
                        OntologyReference = reverseMapping
                        OntologyReferences[OntologyReference].extend(DataDictionary[OntologyReference].keys())
                        break

            if (len(OntologyReferences) == 0):
                # No mapped data found, check if the field is required and if so if there is a default value
                # Raise an exception if a required field has no data
                required = False

                if ('requiredIfReferenceField' in fieldDict):
                    ReferenceField = fieldDict['requiredIfReferenceField']
                    if ('requiredIfReferenceValues' in fieldDict):
                        ReferenceValues = fieldDict['requiredIfReferenceValues']
                        for val in ReferenceValues:
                            if (
                                        (ReferenceField in newDict and val == newDict[ReferenceField]['Value']) or
                                        (val == '' and (
                                            not ReferenceField in newDict or not newDict[ReferenceField]['Value']))):
                                required = True
                                break

                    elif ('requiredIfReferenceValuesMatch' in fieldDict):
                        if (ReferenceField in newDict):
                            ReferenceValuesMatch = fieldDict['requiredIfReferenceValuesMatch']
                            for val in ReferenceValuesMatch:
                                if (val == '*'):
                                    if ('Value' in newDict[ReferenceField]):
                                        required = True
                                        break
                                elif (val.endswith('*')):
                                    if ('Value' in newDict[ReferenceField] and newDict[ReferenceField][
                                        'Value'].startswith(val.strip('*'))):
                                        required = True
                                        break
                                    else:
                                        match = re.match(val, newDict[ReferenceField]['Value'])
                                        if match:
                                            required = True
                                            break

                if (required == True or ('required' in fieldDict and fieldDict['required'] == True)):
                    if ('defaultValue' in fieldDict):
                        newDict[field] = fieldDict.copy()
                        newDict[field]['Value'] = fieldDict['defaultValue']

                        if (newDict[field]['Value'].startswith('&')):
                            newDict[field]['Value'] = self._CalculateFunctionValue(newDict[field]['Value'], field,
                                                                                   newDict[field], rowType, newDict,
                                                                                   IndicatorType,
                                                                                   TransformedData=self.TransformedData)

                        self._ValidateField(newDict[field], field, rowType)

                    elif ('outputFormat' in fieldDict):
                        Value = self._BuildOutputFormatText(fieldDict, newDict)
                        if (Value):
                            newDict[field] = fieldDict.copy()
                            newDict[field]['Value'] = Value

                            self._ValidateField(newDict[field], field, rowType)

                    elif ('datatype' in fieldDict and fieldDict['datatype'] == 'group'):
                        if ('memberof' in fieldDict):
                            self.logging.warning(
                                "Sub-groups should not have 'required' set to true, processing skipped: %s", field)
                        else:
                            groupRow = {'fields': {}}
                            self._BuildFieldGroup(DataDictionary, newDict, rowType, field, groupRow, IndicatorType)
                    else:
                        raise Exception('NoDefaultValue',
                                        'Default Value or outputFormat not defined for required field %s' % field)

            else:
                # One or more values found
                if ('memberof' in fieldDict):
                    # Field is part of a group, handle using special group processing code
                    memberof = fieldDict['memberof']

                    while ('memberof' in self.SchemaConfig[rowType]['fields'][memberof]):
                        # This is a subgroup, add to the parent group
                        memberof = self.SchemaConfig[rowType]['fields'][memberof]['memberof']

                    if (memberof not in GroupRows):
                        GroupRows[memberof] = {'fields': {}}
                    if (field not in GroupRows[memberof]['fields']):
                        GroupRows[memberof]['fields'][field] = []

                    for OntologyReference in OntologyReferences:
                        for Value in OntologyReferences[OntologyReference]:
                            newFieldDict = fieldDict.copy()
                            newFieldDict['matchedOntology'] = OntologyReference
                            NewValue = Value
                            if (OntologyReference in DataDictionary and Value in DataDictionary[OntologyReference]):
                                sourceDict = DataDictionary[OntologyReference][Value]

                                if ('groupID' in sourceDict):
                                    newFieldDict['groupID'] = sourceDict['groupID']

                                NewValue = self._ConvertValueToTargetSchema(field, fieldDict, sourceDict, Value)
                                if (NewValue is None):
                                    raise Exception('ValueNotConverted',
                                                    'Data could not be converted to the target schema [{0}]'.format(
                                                        Value))

                            newFieldDict['NewValue'] = NewValue

                            GroupRows[memberof]['fields'][field].append(newFieldDict)

                else:
                    if (fieldDict['ontologyMappingType'] == 'multiple'):
                        # Fields with multiple ontology mappings are listed in best first order
                        # This finds the best possible match and uses that in the translation

                        for OntologyReference in fieldDict['ontologyMappings']:
                            if (OntologyReference in OntologyReferences):
                                for Value in OntologyReferences[OntologyReference]:
                                    if (field not in newDict):
                                        newDict[field] = fieldDict.copy()
                                        newDict[field]['matchedOntology'] = OntologyReference
                                        NewValue = Value
                                        if (Value in DataDictionary[OntologyReference]):
                                            sourceDict = DataDictionary[OntologyReference][Value]
                                            NewValue = self._ConvertValueToTargetSchema(field, fieldDict, sourceDict,
                                                                                        Value)
                                            if (NewValue is None):
                                                raise Exception('ValueNotConverted',
                                                                'Data could not be converted to the target schema [{0}]'.format(
                                                                    Value))
                                        newDict[field]['Value'] = NewValue
                                    elif ('multiple' in fieldDict and fieldDict['multiple'] == True):
                                        # TODO: Handle fields with multiple values
                                        pass
                                    else:
                                        break

                                break
                    else:
                        for OntologyReference in OntologyReferences:
                            for Value in OntologyReferences[OntologyReference]:
                                if (field not in newDict):
                                    newDict[field] = fieldDict.copy()
                                    newDict[field]['matchedOntology'] = OntologyReference
                                    NewValue = Value
                                    if (OntologyReference in DataDictionary and Value in DataDictionary[
                                        OntologyReference]):
                                        sourceDict = DataDictionary[OntologyReference][Value]
                                        NewValue = self._ConvertValueToTargetSchema(field, fieldDict, sourceDict, Value)
                                        if (NewValue is None):
                                            raise Exception('ValueNotConverted',
                                                            'Data could not be converted to the target schema [{0}]'.format(
                                                                Value))
                                    newDict[field]['Value'] = NewValue
                                elif ('multiple' in fieldDict and fieldDict['multiple'] == True):
                                    # TODO: Handle fields with multiple values
                                    pass
                                else:
                                    break

                            if ('multiple' not in fieldDict or fieldDict['multiple'] == False):
                                break

                        try:
                            self._ValidateField(newDict[field], field, rowType)
                        except Exception as inst:
                            self.logging.info("Validation failed for %s, %s", field, inst)
                            newDict.pop(field)

        if (len(GroupRows) != 0):
            self.logging.error("A group has subrow data that was never processed: %s", GroupRows)

        return newDict

    def _BuildFieldGroup(self, DataDictionary, groupDict, rowType, group, groupRow, IndicatorType):
        '''
        Takes the group data and updates the groupDict with the new groupedFields configuration.
        '''
        # Remove - What is groupDict

        '''
        TODO: This function is still messy and needs a lot more work. It works okay for most of the common use cases
        but will likely be broken for more complex groups
        
        ** Where does the group association need to be preserved to ensure that related indicators are still related on
           output?
        '''

        if (group not in groupDict):
            groupDict[group] = self.SchemaConfig[rowType]['fields'][group].copy()
            groupDict[group]['Value'] = 'True'
            groupDict[group]['ParsedValue'] = True
            groupDict[group]['groupedFields'] = []

        subfields = self.SchemaConfig[rowType]['fields'][group]['subfields']

        # Build the list of required fields for this group

        '''
        subfields should be a dictionary like the following:
        
        "subfields": { 
                        "reasonList_reasonCategory": {"required":true, "primaryKey":true}, 
                        "reasonList_reasonDescription": {"required":false}
        }
        '''

        # Add default values for fields to group if defined

        if ('defaultFields' in self.SchemaConfig[rowType]['fields'][group]):
            defaultFields = self.SchemaConfig[rowType]['fields'][group]['defaultFields']
            for k, v in defaultFields.items():
                if (k not in groupRow['fields']):
                    groupRow['fields'][k] = []

                    if (isinstance(v, list)):
                        for v2 in v:
                            fieldDict = {}
                            fieldDict['ReferencedField'] = None
                            fieldDict['ReferencedValue'] = None
                            fieldDict['matchedOntology'] = None

                            if (v2.startswith('&')):
                                v2 = self._CalculateFunctionValue(v2, k, self.SchemaConfig[rowType]['fields'][k],
                                                                  rowType, groupDict, IndicatorType,
                                                                  TransformedData=self.TransformedData)

                            fieldDict['NewValue'] = v2
                            groupRow['fields'][k].append(fieldDict)
                    else:
                        fieldDict = {}
                        fieldDict['ReferencedField'] = None
                        fieldDict['ReferencedValue'] = None
                        fieldDict['matchedOntology'] = None

                        if (v.startswith('&')):
                            v = self._CalculateFunctionValue(v, k, self.SchemaConfig[rowType]['fields'][k], rowType,
                                                             groupDict, IndicatorType,
                                                             TransformedData=self.TransformedData)

                        fieldDict['NewValue'] = v
                        groupRow['fields'][k].append(fieldDict)

        requiredFields = []
        otherFields = []
        additionalValueFields = []

        primaryKey = None

        '''
        TODO: As an example:
          * Incoming data includes multiple PORT/PROTOCOL pairs
          * After translation, the pairings are decoupled
        '''
        for k, v in subfields.items():
            if ('primaryKey' in v and v['primaryKey'] == True):
                if (primaryKey is None):
                    primaryKey = k
                else:
                    raise Exception('MultiplePrimaryKeys',
                                    'Group %s has multiple primaryKeys defined, that is not supported' % group)

            elif ('required' in v and v['required'] == True):
                requiredFields.append(k)

            else:
                otherFields.append(k)

        if (primaryKey is None):
            raise Exception('primaryKeyNotDefined', 'primaryKey not defined for group %s' % group)

        if (primaryKey not in groupRow['fields']):
            if ('defaultValue' in self.SchemaConfig[rowType]['fields'][primaryKey]):
                fieldDict = {}
                fieldDict['matchedOntology'] = None
                fieldDict['NewValue'] = self.SchemaConfig[rowType]['fields'][primaryKey]['defaultValue']
                groupRow['fields'][primaryKey] = [fieldDict]
            else:
                self.logging.info('primaryKey not found for group %s and no defaultValue defined', group)
                return

        for fieldDict in groupRow['fields'][primaryKey]:
            # Create one group for each unique primary key
            fieldGroup = {}
            fieldGroup[primaryKey] = self.SchemaConfig[rowType]['fields'][primaryKey].copy()
            fieldGroup[primaryKey]['matchedOntology'] = fieldDict['matchedOntology']
            fieldGroup[primaryKey]['Value'] = fieldDict['NewValue']

            if (fieldGroup[primaryKey]['Value'].startswith('&')):
                fieldGroup[primaryKey]['Value'] = self._CalculateFunctionValue(fieldGroup[primaryKey]['Value'],
                                                                               primaryKey, fieldGroup, rowType,
                                                                               fieldGroup, IndicatorType,
                                                                               TransformedData=self.TransformedData)

            self._ValidateField(fieldGroup[primaryKey], primaryKey, rowType)

            groupID = None
            if ('groupID' in fieldDict):
                groupID = fieldDict['groupID']

            for requiredField in requiredFields:
                if (requiredField in groupRow['fields']):
                    if (groupID is not None):
                        for k in groupRow['fields'][requiredField]:
                            if ('groupID' in k and k['groupID'] == groupID):
                                fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()
                                fieldGroup[requiredField]['Value'] = k['NewValue']
                                fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']

                    # Determine if any of the defined fields match this primary key
                    elif (len(groupRow['fields'][primaryKey]) == 1 and len(groupRow['fields'][requiredField]) == 1):
                        # If there is only one group, assume required fields belong to the same group.
                        k = groupRow['fields'][requiredField][0]
                        fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()
                        fieldGroup[requiredField]['Value'] = k['NewValue']
                        fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']

                    elif (self.SchemaConfig[rowType]['fields'][requiredField]['ontologyMappingType'] == 'enum'):
                        # Check if the enum value maps back to a specific primary key value
                        for k in groupRow['fields'][requiredField]:
                            if ('NewValue' in k and k['NewValue'] in
                                self.SchemaConfig[rowType]['fields'][requiredField]['enumValues'] and
                                        'primaryKeyMatch' in
                                        self.SchemaConfig[rowType]['fields'][requiredField]['enumValues'][
                                            k['NewValue']]):

                                primaryKeyMatch = \
                                self.SchemaConfig[rowType]['fields'][requiredField]['enumValues'][k['NewValue']][
                                    'primaryKeyMatch']
                                if (primaryKeyMatch == fieldGroup[primaryKey]['Value']):
                                    if (requiredField not in fieldGroup):
                                        fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][
                                            requiredField].copy()
                                        fieldGroup[requiredField]['Value'] = k['NewValue']
                                        fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']
                                    elif (subfields[requiredField]['addAdditionalValues']):
                                        additionalValueFields.append({requiredField: k})
                                    else:
                                        break

                    else:
                        self.logging.warning('Required field %s could not be matched to the appropriate group',
                                             requiredField)

                if (requiredField not in fieldGroup):
                    # Create a new entry for this field
                    fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()

                    if ('defaultValue' in fieldGroup[requiredField]):
                        fieldGroup[requiredField]['Value'] = fieldGroup[requiredField]['defaultValue']

                    elif (fieldGroup[requiredField]['datatype'] == 'group'):
                        fieldGroup[requiredField]['Value'] = 'True'
                        fieldGroup[requiredField]['ParsedValue'] = True
                        fieldGroup[requiredField]['groupedFields'] = []

                        self._BuildFieldGroup(DataDictionary, fieldGroup, rowType, requiredField, groupRow,
                                              IndicatorType)
                        continue

                    else:
                        self.logging.warning('Field %s is required, but does not have a default value assigned',
                                             requiredField)
                        return

                    # Don't validate fields that are set to function names until after the function is processed 
                    if (fieldGroup[requiredField]['Value'].startswith('&')):
                        fieldGroup[requiredField]['Value'] = self._CalculateFunctionValue(
                                fieldGroup[requiredField]['Value'], requiredField, fieldGroup, rowType, fieldGroup,
                                IndicatorType, TransformedData=None)

                    self._ValidateField(fieldGroup[requiredField], requiredField, rowType)

            for otherField in otherFields:
                if (otherField in groupRow['fields']):
                    # Determine if any of the defined fields match this primary key
                    if (groupID is not None):
                        for k in groupRow['fields'][otherField]:
                            if ('groupID' in k and k['groupID'] == groupID):
                                fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                                fieldGroup[otherField]['Value'] = k['NewValue']
                                fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']

                    elif (len(groupRow['fields'][primaryKey]) == 1 and len(groupRow['fields'][otherField]) == 1):
                        # If there is only one group, assume required fields belong to the same group.
                        k = groupRow['fields'][otherField][0]
                        fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                        fieldGroup[otherField]['Value'] = k['NewValue']
                        fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']
                    elif (fieldGroup and 'primaryKeyMatch' in subfields[otherField]):
                        for k in groupRow['fields'][otherField]:
                            if (subfields[otherField]['primaryKeyMatch'] == fieldGroup[primaryKey]['Value']):
                                if (otherField not in fieldGroup):
                                    fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                                    fieldGroup[otherField]['Value'] = k['NewValue']
                                    fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']
                                elif (subfields[otherField]['addAdditionalValues']):
                                    additionalValueFields.append({otherField: k})
                                else:
                                    break
                    else:
                        self.logging.warning('Field %s could not be matched to the appropriate group', otherField)

            if (fieldGroup):
                groupDict[group]['groupedFields'].append(fieldGroup)
                if (len(additionalValueFields) > 0):
                    for field in additionalValueFields:
                        for k, v in field.items():
                            newFieldGroup = copy.deepcopy(fieldGroup)
                            newFieldGroup.pop(k)
                            newFieldGroup[k] = self.SchemaConfig[rowType]['fields'][k].copy()
                            newFieldGroup[k]['Value'] = v['NewValue']
                            newFieldGroup[k]['matchedOntology'] = v['matchedOntology']
                            groupDict[group]['groupedFields'].append(newFieldGroup)

    def _ConvertValueToTargetSchema(self, field, fieldDict, sourceDict, Value):
        '''
        field - Field name
        fieldDict - the target schema field description dictionary
        sourceDict - the source schema field description dictionary
        Value - the source value that needs to be converted
        
        Convert data formats between source and target schemas
        '''
        NewValue = None

        if (fieldDict['datatype'] == 'datetime'):
            if ('ParsedValue' in sourceDict):
                if (fieldDict['dateTimeFormat'] == 'unixtime'):
                    NewValue = time.mktime(sourceDict['ParsedValue'].timetuple())
                else:
                    NewValue = sourceDict['ParsedValue'].strftime(fieldDict['dateTimeFormat'])
            else:
                # TODO: ParsedValue should always exist, but I got errors when testing some CISCP STIX documents, need to test further
                self.logging.error('DateTime data type did not have a ParsedValue defined for field %s (%s)', field,
                                   fieldDict)

        elif (fieldDict['datatype'] != sourceDict['datatype']):
            if (fieldDict['datatype'] == 'string' or fieldDict['datatype'] == 'enum'):
                NewValue = Value
            else:
                if (fieldDict['datatype'] == 'ipv4' and re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', Value)):
                    NewValue = Value
                else:
                    # FIXME: Process value to appropriate type for target schema
                    self.logging.warning("Cannot convert between data types for field %s (%s, %s)", field,
                                         fieldDict['datatype'], sourceDict['datatype'])

        else:
            NewValue = Value

        return NewValue

    def _MapDataToOntology(self, DataRow, DocumentHeaderData, DocumentMetaData):
        '''
        Builds a dictionary that maps each ontology concept to all the values in the source data, and their associated schema field configuration dictionary
        Combines the all the data from the data row, optional document header data and optional document meta data
        
        Example:
        {
            OntologyConcept = { 'Value': { field: dictionary, field2: data, ... } }
        }
        '''
        # Result data dictionary
        DataDictionary = {}

        # CombinedDataRow aggregates the data from the document header, metadata and the specific data row into one dictionary
        CombinedDataRow = {}

        # Start with the least specific data, which is the document header data
        if (DocumentHeaderData is not None):
            CombinedDataRow.update(DocumentHeaderData)

        # Check to see if any of the header data is overridden by the document metadata.
        if (DocumentMetaData is not None):
            for k, v in DocumentMetaData.items():
                if (k in CombinedDataRow):
                    self.logging.warning(
                        'Key %s already exists in data row, value %s, overwritten by DocumentMetaData key with value %s',
                        k, CombinedDataRow[k], v)

            CombinedDataRow.update(DocumentMetaData)

        if (DataRow is not None):
            # Check to see if the specific data overrides the document header data or document metadata
            for k, v in DataRow.items():
                if (k in CombinedDataRow):
                    self.logging.warning(
                        'Key %s already exists in data row, value %s, overwritten by DataRow key with value %s', k,
                        CombinedDataRow[k], v)

            CombinedDataRow.update(DataRow)
        for field, fieldDict in CombinedDataRow.items():
            if ('Value' not in fieldDict):
                self.logging.warning("Field %s has no value", field)
                continue

            Values = []

            Values.append(fieldDict['Value'])

            if ('AdditionalValues' in fieldDict):
                Values.extend(fieldDict['AdditionalValues'])

            for Value in Values:
                OntologyReference = None
                AdditionalOntologyReferences = []

                if ('ontologyMappingType' in fieldDict):
                    if (fieldDict['ontologyMappingType'] == 'none'):
                        continue

                    elif (fieldDict['ontologyMappingType'] == 'simple'):
                        if (fieldDict['ontologyMapping'] != ''):
                            OntologyReference = fieldDict['ontologyMapping']

                    elif (fieldDict['ontologyMappingType'] == 'multiple'):
                        if ('ontologyMappings' in fieldDict):
                            for mapping in fieldDict['ontologyMappings']:
                                if (mapping != ''):
                                    if (OntologyReference is None):
                                        OntologyReference = mapping
                                    else:
                                        AdditionalOntologyReferences.append(mapping)

                    elif (fieldDict['ontologyMappingType'] == 'enum'):
                        if ('enumValues' in fieldDict):
                            if (Value in fieldDict['enumValues']):
                                if (fieldDict['enumValues'][Value]['ontologyMapping'] != ''):
                                    OntologyReference = fieldDict['enumValues'][Value]['ontologyMapping']

                            else:
                                for eValue in fieldDict['enumValues']:
                                    if ('*' in eValue and eValue != '*' and fieldDict['enumValues'][eValue][
                                        'ontologyMapping'] != ''):
                                        if (eValue.startswith('*')):
                                            if (Value.endswith(eValue.strip('*'))):
                                                OntologyReference = fieldDict['enumValues'][eValue]['ontologyMapping']
                                                break
                                        elif (eValue.endswith('*')):
                                            if (Value.startswith(eValue.strip('*'))):
                                                OntologyReference = fieldDict['enumValues'][eValue]['ontologyMapping']
                                                break

                            if (OntologyReference is None and "*" in fieldDict['enumValues']):
                                if (fieldDict['enumValues']['*']['ontologyMapping'] != ''):
                                    OntologyReference = fieldDict['enumValues']['*']['ontologyMapping']

                        else:
                            raise Exception('MissingEnumValues', 'enumValues missing from field %s' % field)

                    elif (fieldDict['ontologyMappingType'] == 'referencedEnum'):
                        referencedField = fieldDict['ontologyEnumField']
                        if (referencedField in DataRow and 'Value' in DataRow[referencedField]):
                            # TODO: Will this ever need to use ParsedValue?
                            referencedValue = DataRow[referencedField]['Value']
                            if ('ontologyMappingEnumValues' in fieldDict):
                                if (referencedValue in fieldDict['ontologyMappingEnumValues']):
                                    if (fieldDict['ontologyMappingEnumValues'][referencedValue][
                                            'ontologyMapping'] != ''):
                                        OntologyReference = fieldDict['ontologyMappingEnumValues'][referencedValue][
                                            'ontologyMapping']

                                else:
                                    for eValue in fieldDict['ontologyMappingEnumValues']:
                                        if ('*' in eValue and eValue != '*' and
                                                    fieldDict['ontologyMappingEnumValues'][eValue][
                                                        'ontologyMapping'] != ''):
                                            if (eValue.startswith('*')):
                                                if (referencedValue.endswith(eValue.strip('*'))):
                                                    OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                        'ontologyMapping']
                                                    break
                                            elif (eValue.endswith('*')):
                                                if (referencedValue.startswith(eValue.strip('*'))):
                                                    OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                        'ontologyMapping']
                                                    break

                                if (OntologyReference is None and "*" in fieldDict['ontologyMappingEnumValues']):
                                    if (fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping'] != ''):
                                        OntologyReference = fieldDict['ontologyMappingEnumValues']['*'][
                                            'ontologyMapping']
                            else:
                                raise Exception('ontologyMappingEnumValues',
                                                'ontologyMappingEnumValues missing from field %s' % field)
                        elif ('ontologyMappingEnumValues' in fieldDict and '' in fieldDict[
                            'ontologyMappingEnumValues']):
                            OntologyReference = fieldDict['ontologyMappingEnumValues']['']['ontologyMapping']

                    else:
                        raise Exception('UnknownOntologyMappingType',
                                        'The OntologyMappingType %s in field %s is undefined' % (
                                        fieldDict['ontologyMappingType'], field))

                else:
                    raise Exception('MissingOntologyMappingType',
                                    'The OntologyMappingType is missing from field %s' % field)

                if (OntologyReference is not None):

                    # Some schemas included namespace or other data in the value of the field, which should be stripped before transformation
                    # to the target schema.
                    if ('stripNamespace' in fieldDict):
                        Value = Value.replace(fieldDict['stripNamespace'], '')

                    AdditionalOntologyReferences.insert(0, OntologyReference)
                    for Reference in AdditionalOntologyReferences:
                        if (Reference not in DataDictionary):
                            DataDictionary[Reference] = {}
                        elif (Value in DataDictionary[Reference]):
                            # self.logging.debug("Value %s is already mapped to Ontology concept %s, skipping new mapping from field %s" % (Value, Reference, field))
                            continue

                        DataDictionary[Reference][Value] = fieldDict

        return DataDictionary

    def _BuildOutputFormatText(self, fieldDict, newDict):

        # Build a new value based on the output format, if it exists
        # Regex match returns two values into a set. [0] is anything that isn't a field name and [1] is a field name
        # New value replaces [field] with the value of that field and outputs everything else out directly
        if ('outputFormatCondition' in fieldDict):
            condition = self._outputFormatRE.findall(fieldDict['outputFormatCondition'])
            conditionMet = True
            evalString = ''
            if (condition):
                for m in condition:
                    if (m[0] != ''):
                        evalString += m[0]
                    if (m[1] != ''):
                        if (m[1] in newDict and 'Value' in newDict[m[1]]):
                            evalString += newDict[m[1]]['Value']
                        else:
                            conditionMet = False
                            break

                if (conditionMet and evalString):
                    if (not eval(evalString)):
                        # Condition is not met, do not generate output format
                        return None
            else:
                # Condition is not met, do not generate output format
                return None

        match = self._outputFormatRE.findall(fieldDict['outputFormat'])
        if (match):
            Value = ''
            AllFields = True
            for m in match:
                if (m[0] != ''):
                    Value += m[0]
                if (m[1] != ''):
                    if (m[1] in newDict and 'Value' in newDict[m[1]]):
                        Value += newDict[m[1]]['Value']
                    elif ('required' in fieldDict and fieldDict['required'] == True):
                        raise Exception('NoDefaultValue', 'Default Value not defined for required field %s' % m[1])
                    else:
                        AllFields = False
                        break

            # Check that all fields required for the output formated text exist, or delete the field from the results
            if (AllFields):
                return Value

        return None

    def _CalculateFunctionValue(self, value, fieldName, fieldDict, rowType, row=None, IndicatorType=None,
                                TransformedData=None):
        '''
        '''
        if (value.startswith('&')):
            match = re.match(r'&([^\(]+)\(([^\)]*)\)', value)
            if (match):
                function = match.group(1)
                functionarg = match.group(2)

                FunctionScopeValid = self.FunctionManager.GetFunctionScope(rowType, function)

                if (FunctionScopeValid):

                    args = {
                        'fieldName': fieldName,
                        'fieldDict': fieldDict,
                        'functionArg': functionarg,
                        'currentRow': row,
                        'indicatorType': IndicatorType,
                        'transformedData': TransformedData
                    }

                    value = self.FunctionManager.ExecuteTransformFunction(rowType, function, args)

                else:
                    self.logging.warning('Function %s in field %s is not valid for current document scope %s', function,
                                         fieldName, rowType)
            else:
                raise Exception('InvalidFunctionFormat',
                                'The function reference for field %s, %s, is not valid' % (fieldName, value))
        else:
            self.logging.warning('Value %s is not a function reference', value)

        return value

    @classmethod
    def FlattenDict(cls, NestedDict, ParentKey='', Sep=';'):
        '''
        Takes a nested dictionary, and rewrites it to a flat dictionary, where each nested key is appended to the
        top level key name, separated with Sep
        '''

        items = []
        for k, v in NestedDict.items():
            new_key = ParentKey + Sep + k if ParentKey else k
            if (isinstance(v, collections.MutableMapping)):
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
