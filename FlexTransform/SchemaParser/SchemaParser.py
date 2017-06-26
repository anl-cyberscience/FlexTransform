"""
Created on Oct 13, 2014

@author: ahoying
"""

import collections
import copy
import logging
import re
import socket
from builtins import str

import arrow

from FlexTransform.SchemaParser.TransformFunctions import TransformFunctionManager


class SchemaParser(object):
    """
    Base class for the Schema Parser logic.  The following fields are defined for this class:

    * self.SchemaConfig - The schema configuration for the target format
    * self._ValueMap - Mapping from the valuemap specification to the JSON config item that defines
                      it (or items)
    * self._field_order - Ordered list of field names used to process the fields in the schema based on their relationship to each other.
    * self._outputFormatRE -  Regex used to parse the outputFormat field
                              Example outputFormat: "[comment], direction:[direction],
                                                     confidence:[confidence], severity:[severity]"
    * self.logging - The logging object
    """

    # Class global variables
    _outputFormatRE = re.compile(r"([^\[]+)?(?:\[([^\]]+)\])?")

    def __init__(self, config, trace, tracelist=[]):
        """
        Constructor
        """
        self.logging = logging.getLogger('FlexTransform.SchemaParser')
        self.trace = trace
        self.tracelist = tracelist
        self.traceindex = {}
        if self.trace:
            for x in self.tracelist:
                for v in x["src_fields"]:
                    self.traceindex[v] = x
                for y in x["dst_fields"]:
                    self.traceindex[y] = x
                for w in x["src_IRIs"]:
                    self.traceindex[w] = x
                for z in x["dst_IRIs"]:
                    self.traceindex[z] = x
            if len(self.traceindex) > 0:
                self.logging.debug("[TRACE __init__] - Monitoring {} elements".format(len(self.traceindex.keys())))

        self.SchemaConfig = config

        self._field_order = self._calculate_schema_field_order()

        self.FunctionManager = TransformFunctionManager(self.trace, trace_list=self.tracelist)

        # TODO: Create a JSON schema document and validate the config against the schema. Worst case, define accepted tags and validate there are no unknown tags.

    def map_data_to_schema(self, SourceData, oracle=None):
        """
        Maps the values in SourceData to the underlying schema from the config
        Parameters:
        * SourceData -
        * oracle - An instance of the OntologyOracle to build an ABOX for the source data
                   Assumes the oracle has been initialized with a FlexTransform TBOX

        TODO: Create an ABOX (using the Ontology Oracle) to represent the source file; this will also inform the
              target production, as data will be requested from the ABOX.

              Essentially this will consist of creating instances of the appropriate subclasses in an ABOX.
        """
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE MapDataToSchema] - Monitoring {} elements".format(len(self.traceindex.keys())))

        # The value map is only used by the _MapRowToSchema function, so it isn't calculated
        # until this method is called and not under __init__()
        self._value_map = self._valuemap_to_field()

        self.mapped_data = {}

        row_types = []

        if 'IndicatorData' in SourceData:
            row_types.append('IndicatorData')
        if 'DocumentHeaderData' in SourceData:
            row_types.append('DocumentHeaderData')
        # TODO: Need to generalize this to deal elegantly with environment-derived data:
        ''' Get data about the environment '''
        if 'DerivedData' in SourceData:
            row_types.append('DerivedData')

        for rowType in row_types:
            if rowType in self.SchemaConfig:
                if isinstance(SourceData[rowType], list):
                    self.mapped_data[rowType] = []
                    for row in SourceData[rowType]:
                        if isinstance(row, dict):
                            try:
                                DataRow = self._map_row_to_schema(SchemaParser.FlattenDict(row), rowType)
                                self.mapped_data[rowType].append(DataRow)
                            except Exception as inst:
                                self.logging.error(inst)
                                # self.logging.debug(str(SchemaParser.FlattenDict(row)))
                        else:
                            raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
                elif isinstance(SourceData[rowType], dict):
                    DataRow = self._map_row_to_schema(SchemaParser.FlattenDict(SourceData[rowType]), rowType)
                    self.mapped_data[rowType] = DataRow
                else:
                    raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            else:
                raise Exception('SchemaConfigNotFound', 'Data Type: ' + rowType)

        # Let's start here.  Build an ABOX:
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

        return self.mapped_data

    def map_metadata_to_schema(self, sourceMetaData):
        """
        Add meta data to the MappedData
        """
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE MapMetadataToSchema] - Monitoring {} elements".format(len(self.traceindex.keys())))

        if 'DocumentMetaData' in self.SchemaConfig:
            if isinstance(sourceMetaData, dict):
                DataRow = self._map_row_to_schema(SchemaParser.FlattenDict(sourceMetaData), 'DocumentMetaData')
                self.mapped_data['DocumentMetaData'] = DataRow
            else:
                raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
        else:
            raise Exception('SchemaConfigNotFound', 'Data Type: DocumentMetaData')

    def TransformData(self, MappedData, oracle=None):
        """
        Takes the data that was mapped to the source schema and transform it using the target schema
        Parameters:
        * MappedData - The data mapped from the source document
        * oracle - An instance of the OntologyOracle class which encapsulates the target schema ontology
                   If 'None', will not be used.
        """
        self.logging.debug("Begin TransformData(...)")
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE TransformData] - Monitoring {} elements".format(len(self.traceindex.keys())))
        self.transformed_data = {}

        # If the oracle is set, initialize it:
        if oracle is not None:
            oracle.buildABOX(MappedData)

        # Parse indicators before headers
        row_types = []

        document_header_data = None
        document_meta_data = None
        derived_data = None

        ''' self.SchemaConfig is the dictionary representation of the destination schema '''
        if 'IndicatorData' in self.SchemaConfig.keys():
            row_types.append('IndicatorData')
        if 'DocumentHeaderData' in self.SchemaConfig.keys():
            row_types.append('DocumentHeaderData')

        ''' MappedData is the dictionary representation of the source data mapped to the source schema '''
        if 'DerivedData' in MappedData:
            derived_data = MappedData['DerivedData']

        if 'DocumentHeaderData' in MappedData:
            document_header_data = MappedData['DocumentHeaderData']

        if 'DocumentMetaData' in MappedData:
            document_meta_data = MappedData['DocumentMetaData']

        for rowType in row_types:
            if rowType in MappedData:
                if isinstance(MappedData[rowType], list):
                    self.transformed_data[rowType] = []
                    for row in MappedData[rowType]:
                        if isinstance(row, dict):
                            try:
                                self.transformed_data[rowType].append(
                                    self._TransformDataToNewSchema(rowType, row, document_header_data,
                                                                   document_meta_data, derived_data, oracle))
                            except Exception as inst:
                                self.logging.error(inst)
                        else:
                            raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")

                elif isinstance(MappedData[rowType], dict):
                    self.transformed_data[rowType] = self._TransformDataToNewSchema(rowType, MappedData[rowType], None,
                                                                                    document_meta_data, derived_data, oracle)
                else:
                    raise Exception('NoParsableDataFound', "Data isn't in a parsable dictionary format")
            else:
                self.logging.info("Row type {} *not* in MappedData".format(rowType))
                self.transformed_data[rowType] = self._TransformDataToNewSchema(rowType, None, None, document_meta_data,
                                                                                oracle)

        return self.transformed_data

    def _valuemap_to_field(self):
        """
        Create a fast lookup dictionary for mapping values from flattened dictionaries back to the schema field
        """
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE _ValuemapToField] - Monitoring {} elements".format(len(self.traceindex.keys())))

        value_map = {}

        for rowType in self.SchemaConfig:
            value_map[rowType] = {}
            if 'fields' in self.SchemaConfig[rowType] and isinstance(self.SchemaConfig[rowType]['fields'], dict):
                for fieldName, fieldDict in self.SchemaConfig[rowType]['fields'].items():
                    if 'valuemap' in fieldDict:
                        value_map[rowType][fieldDict['valuemap']] = fieldName
                        if self.trace and fieldName in self.traceindex:
                            self.logging.debug("[TRACE {}] - Added to ValueMap[{}][{}]".format(fieldName, rowType, fieldDict['valuemap']))
                    if 'additionalValuemaps' in fieldDict:
                        for valuemap in fieldDict['additionalValuemaps']:
                            value_map[rowType][valuemap] = fieldName
                            if self.trace and fieldName in self.traceindex:
                                self.logging.debug("[TRACE {}] - Added to ValueMap[{}][{}]".format(fieldName, rowType, valuemap))

        return value_map

    def _calculate_schema_field_order(self):
        """
        Sorts the schema fields from the first fields that must be processed to the last based on the relationships between the fields.
        Caches the data so that this only has to be determined the first time.

        Returns a list with the fields in order.
        """
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE _CalculateSchemaFieldOrder] - Monitoring {} elements".format(len(self.traceindex.keys())))

        # TODO: Can this be cached offline so it is loaded between runs so long as the schema .json files don't change?
        schema_field_order = {}

        for rowType in self.SchemaConfig:
            schema_field_order[rowType] = []

            field_order = {}

            for field, fieldDict in self.SchemaConfig[rowType]['fields'].items():
                if 'datatype' in fieldDict and fieldDict['datatype'] == "group":
                    # Groups need to be processed last by the transform engine
                    if field not in field_order or field_order[field] < 10:
                        field_order[field] = 10
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Group data type - field_order set to {}".format(field, field_order[field]))

                    # Handle subgroups, parent group needs to be processed after all child groups
                    if 'memberof' in fieldDict:
                        if fieldDict['memberof'] not in field_order \
                                or field_order[fieldDict['memberof']] <= field_order[field]:
                            field_order[fieldDict['memberof']] = field_order[field] + 1
                            if self.trace and fieldDict['memberof'] in self.traceindex:
                                self.logging.debug("[TRACE {}] - memberof {}, incrementing field_order to {}".format(fieldDict['memberof'],
                                                                                                                    field,
                                                                                                                    field_order[fieldDict['memberof']]))
                elif 'required' in fieldDict and fieldDict['required'] == True:
                    if field not in field_order or field_order[field] > 1:
                        field_order[field] = 1
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Required; field_order set to {}".format(field, field_order[field]))
                elif 'memberof' in fieldDict:
                    if field not in field_order or field_order[field] > 5:
                        field_order[field] = 5
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - memberof {}; field_order set to {}".format(field, fieldDict['memberof'], field_order[field]))
                        if (fieldDict['memberof'] not in field_order or field_order[fieldDict['memberof']] <= field_order[
                            field]):
                            field_order[fieldDict['memberof']] = field_order[field] + 1
                            if self.trace and fieldDict['memberof'] in self.traceindex:
                                self.logging.debug("[TRACE {}] - Incremented parent {}; field_order set to {}".format(fieldDict['memberof'], field, field_order[fieldDict['memberof']]))

                elif 'dependsOn' in fieldDict:
                    if field not in field_order or field_order[field] < 6:
                        field_order[field] = 6
                        if self.trace and field in self.traceindex:
                            self.logging.debug(("[TRACE {}] - dependsOn {}; field_order set to {}".format(field, fieldDict['dependsOn'], field_order[field])))
                else:
                    if field not in field_order or field_order[field] > 4:
                        field_order[field] = 4
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - no conditions apply; field_order set to {}".format(field, field_order[field]))

            # Run through all the fields again and re-order based on references
            for field, fieldDict in self.SchemaConfig[rowType]['fields'].items():
                if 'defaultValue' in fieldDict and fieldDict['defaultValue'].startswith('&'):
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - defaultValue is a function, evaluating args to see if order needs revision.".format(field))
                    match = re.match(r'&([^\(]+)\(([^\)]*)\)', fieldDict['defaultValue'])
                    if match:
                        args = match.group(2)
                        if args and args in self.SchemaConfig[rowType]['fields']:
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - function argument {} found.".format(field, args))
                            if (field in field_order and (
                                    args not in field_order or field_order[args] >= field_order[field])):
                                field_order[field] = field_order[args] + 1
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Updated order based on argument {} - field_order set to {}".format(field, args, field_order[field]))

                elif 'outputFormat' in fieldDict:
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Found output format specification {} - processing.".format(field, fieldDict['outputFormat']))
                    match = self._outputFormatRE.findall(fieldDict['outputFormat'])
                    if match:
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Matched output format specification {}".format(field, fieldDict['outputFormat']))
                        for m in match:
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Extracted component field {}".format(field, m[1]))
                            if m[1] != '':
                                if self.trace and m[1] in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Found in outputFormat for {}; evaluating field order".format(m[1], field))
                                if m[1] in self.SchemaConfig[rowType]['fields']:
                                    if (field in field_order and (
                                            m[1] not in field_order or field_order[m[1]] >= field_order[field])):
                                        field_order[m[1]] = field_order[field] - 1
                                        if self.trace and m[1] in self.traceindex:
                                            self.logging.debug("[TRACE {}] - field_order set to {} ({} - 1)".format(m[1], field_order[m[1]], field))
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - field_order of outputFormatField {} set to {}".format(field, m[1], field_order[m[1]]))

                    if 'outputFormatCondition' in fieldDict:
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Found output format condition specification {} - processing.".format(field, fieldDict['outputFormatCondition']))
                        match = self._outputFormatRE.findall(fieldDict['outputFormatCondition'])
                        if match:
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Matched output format condition specification {}".format(field, fieldDict['outputFormatCondition']))
                            for m in match:
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Extracted component field {}".format(field, m[1]))
                                if m[1] != '':
                                    if self.trace and m[1] in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Found in outputFormat for {}; evaluating field order".format(m[1], field))
                                    if m[1] in self.SchemaConfig[rowType]['fields']:
                                        if field in field_order and (
                                                m[1] not in field_order or field_order[m[1]] >= field_order[field]):
                                            field_order[m[1]] = field_order[field] - 1
                                            if self.trace and m[1] in self.traceindex:
                                                self.logging.debug("[TRACE {}] - Found in outputFormat for {}; evaluating field order".format(m[1], field))
                                            if self.trace and field in self.traceindex:
                                                self.logging.debug("[TRACE {}] - field_order of outputFormatField {} set to {}".format(field, m[1], field_order[m[1]]))
                        else:
                            self.logging.warning("OutputFormatCondition {} specified for field {} but could not be parsed.".format(fieldDict['outputFormatCondition'], field))

                if field in field_order:
                    if 'requiredIfReferenceField' in fieldDict:
                        if fieldDict['requiredIfReferenceField'] not in field_order:
                            field_order[fieldDict['requiredIfReferenceField']] = field_order[field] - 1
                        elif field_order[fieldDict['requiredIfReferenceField']] >= field_order[field]:
                            field_order[field] = field_order[fieldDict['requiredIfReferenceField']] + 1
                        tfield = fieldDict['requiredIfReferenceField']
                        if self.trace and tfield in self.traceindex:
                            self.logging.debug("[TRACE {}] - Found in requiredIfReferenceField for {}; field_order set to {}".format(
                                                                 tfield, field, field_order[tfield]))

                    if 'ontologyMappingType' in fieldDict and fieldDict['ontologyMappingType'] == 'referencedEnum':
                        if fieldDict['ontologyEnumField'] not in field_order:
                            field_order[fieldDict['ontologyEnumField']] = field_order[field] - 1
                        elif field_order[fieldDict['ontologyEnumField']] >= field_order[field]:
                            field_order[field] = field_order[fieldDict['ontologyEnumField']] + 1
                        tfield = fieldDict['ontologyEnumField']
                        if self.trace and tfield in self.traceindex:
                            self.logging.debug("[TRACE {}] - Found in ontologyEnumField for {}; field_order set to {}".format(
                                                                 tfield, field, field_order[tfield]))

                    if 'dependsOn' in fieldDict:
                        if fieldDict['dependsOn'] not in field_order:
                            field_order[fieldDict['dependsOn']] = field_order[field] - 1
                        elif field_order[fieldDict['dependsOn']] >= field_order[field]:
                            field_order[field] = field_order[fieldDict['dependsOn']] + 1
                        tfield = fieldDict['dependsOn']
                        if self.trace and tfield in self.traceindex:
                            self.logging.debug("[TRACE {}] - Found in dependsOn for {}; field_order set to {}".format(
                                                                 tfield, field, field_order[tfield]))

                    if 'fields' in fieldDict:
                        requiredFields = fieldDict['fields']
                        for requiredField in requiredFields:
                            if requiredField not in field_order:
                                field_order[requiredField] = field_order[field] - 1
                            elif field_order[requiredField] >= field_order[field]:
                                field_order[field] = field_order[requiredField] + 1
                            tfield = requiredField
                            if self.trace and tfield in self.traceindex:
                                self.logging.debug("[TRACE {}] - Found in requiredFields for {}; field_order set to {}".format(
                                                                 tfield, field, field_order[tfield]))

            schema_field_order[rowType].extend(sorted(field_order, key=field_order.get))

        return schema_field_order

    def _map_row_to_schema(self, DataRow, rowType, SubGroupedRow=False):
        """
        Create a new dictionary with the mapping between the data row and the schema field definition
        Parameters:
          * DataRow - The specification of data which will be the source for this mapping
          * rowType - Either DocumentHeaderData, DocumentMetaData or IndicatorData.
          * SubGroupedRow - Set to true if this is processing a subgrouped row and not the primary data row

          TODO: Add processing for derived data rowType

          Data structures used:
          * new_dict - Dictionary to hold the mapping of data to new schema that we return.
          * processed_fields - Keep track of the fields we've already processed; important to ensure that dependent values are taken from the
                              source data, or are defined before they are referenced.
          * fieldDict - The dictionary of metadata related to the field from the source schema.
        """
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE _MapRowToSchema] - Monitoring {} elements".format(len(self.traceindex.keys())))

        new_dict = {}
        processed_fields = {}

        if 'IndicatorType' in DataRow:
            new_dict['IndicatorType'] = DataRow['IndicatorType']

        ValueMap = self._value_map[rowType]

        # Get the field dependency order for processing the source schema
        field_order = self._field_order[rowType]

        for field in field_order:
            fieldDict = self.SchemaConfig[rowType]['fields'][field]
            mappedField = None
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}] - Mapping row to schema:".format(field))

            if (field in DataRow):
                mappedField = field
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Field found in DataRow; setting mappedField.".format(field))

            if (not mappedField and 'valuemap' in fieldDict):
                if (fieldDict['valuemap'] in DataRow):
                    mappedField = fieldDict['valuemap']
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Field not found in DataRow, mapping to found valuemap ({})".format(field, fieldDict['valuemap']))

            if (not mappedField and 'additionalValuemaps' in fieldDict):
                for valuemap in fieldDict['additionalValuemaps']:
                    if (valuemap in DataRow):
                        mappedField = valuemap
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Field not found in DataRow, mapping to found additionalValuemap ({})".format(field, valuemap))
                        break

            if mappedField is not None:
                processed_fields[mappedField] = True
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Setting prcessedFields to True".format(field))

                if 'ignore' in fieldDict and fieldDict['ignore'] == True:
                     # TODO - Add logging of ignore flag processed
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Field ignored, not mapping to schema.".format(field))
                    continue

                elif 'error' in fieldDict:
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Field error flagged, not mapping to schema.".format(field))
                    raise Exception("InvalidSchemaMapping", fieldDict['error'])

                if 'dependsOn' in fieldDict:
                    # If the field this field depends on does not exist, then don't add to new dictionary
                    dependsOn = fieldDict['dependsOn']
                    if dependsOn not in new_dict or 'Value' not in new_dict[dependsOn]:
                        # TODO - Add logging of skipping this element
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Field depends on another that does not exist {}, not mapping to schema.".format(field, dependsOn))
                        if self.trace and dependsOn in self.traceindex:
                            self.logging.debug("[TRACE {}] - Field does not exist for dependent field {}; not mapping dependent to schema.".format(dependsOn, field))
                        continue

                Value = DataRow[mappedField]

                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Using DataRow for {} as Value".format(field, mappedField))

                # TODO - Add traceindex logging for this block
                if fieldDict['datatype'] == "datetime":
                    if 'dateTimeFormat' not in fieldDict:
                        raise Exception('SchemaConfigMissing',
                                        'The dateTimeFormat configuration is missing for field ' + field)
                    try:
                        if fieldDict['dateTimeFormat'] == "unixtime":
                            fieldDict['ParsedValue'] = arrow.get(Value)
                        else:
                            datetime_formats = list()
                            datetime_formats.append(fieldDict['dateTimeFormat'])
                            if 'dateTimeFormatAlternate' in fieldDict:
                                datetime_formats.append(fieldDict['dateTimeFormatAlternate'])

                            # If datetime value ends with "+XXXX", "-XXXX", "+XX:XX", "-XX:XX", or "Z", ingest normally
                            if re.match(r"(.*)([+-]\d\d):(\d\d)$|(.*)\d+([+-]\d\d\d\d)$|(.*)Z$", Value):
                                fieldDict['ParsedValue'] = arrow.get(Value, datetime_formats)
                                # self.logging.info("Datetime parsed with provided Timezone, value=%".format(Value))
                            elif 'dateTimezoneDefault' in fieldDict:
                                # If value has no timezone, but default is provided, ingest with default timezone
                                fieldDict['ParsedValue'] = arrow.get(Value, datetime_formats, tzinfo=fieldDict['dateTimezoneDefault'])
                                # self.logging.info("Datetime ingested with default Timezone ({}), value={}".format(fieldDict['dateTimezoneDefault'], Value))
                            else:
                                # If value has no timezone & no default, ingest as UTC
                                fieldDict['ParsedValue'] = arrow.get(Value, datetime_formats)
                                # self.logging.warning("Datetime ingested as UTC, no timezone provided, value={}".format(Value))
                    except Exception as inst:
                        self.logging.error(inst)
                        raise Exception('DataTypeInvalid',
                                        'Value for field ' + mappedField + ' is not a valid date time value: ' + Value)

                new_dict[field] = fieldDict.copy()

                if 'mapOntologyToElement' in fieldDict:
                    # TODO - Add logging & additional error checking
                    map_onto = fieldDict['mapOntologyToElement']
                    if map_onto in new_dict and not new_dict[map_onto]['ontologyMapping']:
                        new_dict[map_onto]['ontologyMapping'] = \
                            fieldDict['enumValues'][DataRow[mappedField]]['ontologyMapping']
                        new_dict[field]["discardBeforeTranslation"] = True
                    else:
                        # TODO - Throw error and remove pass command
                        pass

                if isinstance(Value, list) and 'multiple' in fieldDict and fieldDict['multiple'] == True:
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - List of values found, and this is a multiple value field".format(field))

                    if fieldDict['datatype'] == 'group':
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Group datatype found; processing".format(field))

                        # This processes instances where the same field grouping may exist multiple times in a single indicator

                        newDataRow = {}

                        subfields = fieldDict['subfields']

                        # GroupID is a reference ID to fields that were grouped together in the source document, so they can be processed together in the target document
                        GroupID = 0

                        for row in Value:
                            if isinstance(row, dict):
                                subRow = SchemaParser.FlattenDict(row, ParentKey=mappedField)
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Processing subRow as flattened dict".format(field))

                                for (subkey, subvalue) in subRow.items():
                                    if subkey in ValueMap and ValueMap[subkey] not in subfields:
                                        raise Exception('FieldNotAllowed',
                                                        'Field %s is not an allowed subfield of %s' % (
                                                        ValueMap[subkey], field))

                                    newDataRow[subkey] = subvalue
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Set value for subkey {}, GroupID {}".format(field, subkey, GroupID))

                                subDict = self._map_row_to_schema(newDataRow, rowType, SubGroupedRow=True)
                                new_dict.update(self._UpdateFieldReferences(subDict, GroupID, subfields))
                                GroupID = GroupID + 1

                            else:
                                raise Exception('DataError',
                                                'Data type of sub row for %s is not dict: %s' % (mappedField, row))

                        # Value could be set to any string, it isn't used for field groups except to indicate that the group has been parsed
                        new_dict[field]['Value'] = 'True'
                    else:
                        if Value.__len__() > 1:
                            new_dict[field]['AdditionalValues'] = []
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Field has multiple values; setting...".format(field))
                        for d in Value:
                            if isinstance(d, (list, dict)):
                                self.logging.warning(
                                    '%s subvalue in the list is another list or dictionary, not currently supported: %s',
                                    mappedField, d)
                                continue

                            if 'Value' not in new_dict[field]:
                                # Put the first value in Value and the rest into AdditionalValues
                                new_dict[field]['Value'] = str(d)
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Setting Value to {}".format(field, str(d)))
                            else:
                                new_dict[field]['AdditionalValues'].append(str(d))
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Appending AdditionalValue {}".format(field, str(d)))

                elif isinstance(Value, (list, dict)):
                    self.logging.warning('%s value is a list or dictionary, not currently supported: %s', mappedField,
                                         Value)
                    continue
                elif isinstance(Value, str):
                    # The rstrip is to get rid of rogue tabs and white space at the end of a value, a frequent problem with STIX formated documents in testing
                    new_dict[field]['Value'] = str.rstrip(Value)
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Setting (rstripped) string value to {}".format(field, new_dict[field]['Value']))
                else:
                    new_dict[field]['Value'] = str(Value)
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Setting string value to {}".format(field, new_dict[field]['Value']))

                # Process the regexSplit directive
                if 'regexSplit' in fieldDict:
                    match = re.match(fieldDict['regexSplit'], new_dict[field]['Value'])
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Identified as regex field, processing {} with {}".format(
                                                field, fieldDict['regexSplit'], new_dict[field]['Value']))
                    if match:
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Regex matched, pulling out comma-delimeted fields from ".format(
                                                field, fieldDict['regexFields']))
                        regexFields = re.split(',\s+', fieldDict['regexFields'])
                        i = 0
                        while i < regexFields.__len__():
                            if match.group(i + 1):
                                newFieldName = regexFields[i]
                                newFieldValue = match.group(i + 1)
                                new_dict[newFieldName] = self.SchemaConfig[rowType]['fields'][newFieldName].copy()
                                new_dict[newFieldName]['Value'] = newFieldValue
                                if self.trace and newFieldName in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Extracted value {} from regex for field {}.".format(
                                                newFieldName, newFieldValue, field))

                                self._ValidateField(new_dict[newFieldName], newFieldName, rowType)
                            i += 1

                self._ValidateField(new_dict[field], field, rowType)

            elif not SubGroupedRow:
                # Check if there is a default value
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - No mapped data found; looking for default value.".format(field))

                # No mapped data found, check if the field is required and if so if there is a default value
                # Raise an exception if a required field has no data
                required = False
                ReferenceField = None

                if 'requiredIfReferenceField' in fieldDict:
                    ReferenceField = fieldDict['requiredIfReferenceField']
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - requiredIfReferenceField {}".format(field, ReferenceField))
                    if 'requiredIfReferenceValues' in fieldDict:
                        ReferenceValues = fieldDict['requiredIfReferenceValues']
                        for val in ReferenceValues:
                            if (
                                        (ReferenceField in new_dict and val == new_dict[ReferenceField]['Value']) or
                                        (val == '' and (
                                            not ReferenceField in new_dict or not new_dict[ReferenceField]['Value']))):
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - requiredIfReferenceValue {}; setting to true".format(field, val))
                                if self.trace and ReferenceField in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Value {} forcing required unmapped field {}".format(
                                                                        ReferenceField, val, field))
                                required = True
                                break

                    elif 'requiredIfReferenceValuesMatch' in fieldDict:
                        if ReferenceField in new_dict:
                            ReferenceValuesMatch = fieldDict['requiredIfReferenceValuesMatch']
                            for val in ReferenceValuesMatch:
                                if val == '*':
                                    if 'Value' in new_dict[ReferenceField]:
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - requiredIfReferenceValuesMatch {}; setting to true".format(field, val))
                                        if self.trace and ReferenceField in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Value {} forcing required unmapped field {}".format(
                                                                                ReferenceField, val, field))
                                        required = True
                                        break
                                elif val.endswith('*'):
                                    if 'Value' in new_dict[ReferenceField] and \
                                            new_dict[ReferenceField]['Value'].startswith(val.strip('*')):
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - requiredIfReferenceValuesMatch {}; setting to true".format(field, val))
                                        if self.trace and ReferenceField in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Value {} forcing required unmapped field {}".format(
                                                                                ReferenceField, val, field))
                                        required = True
                                        break

                if required is True or ('required' in fieldDict and fieldDict['required'] == True):
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Required flag is set; checking default value:".format(field))
                    if 'defaultValue' in fieldDict:
                        new_dict[field] = fieldDict.copy()
                        new_dict[field]['Value'] = fieldDict['defaultValue']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Using default value {}".format(field, new_dict[field]['Value']))

                        if new_dict[field]['Value'].startswith('&'):
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Default value is a function; calculating result...".format(field, new_dict[field]['Value']))
                            new_dict[field]['Value'] = self._CalculateFunctionValue(new_dict[field]['Value'], field,
                                                                                    new_dict[field], rowType, new_dict,
                                                                                    IndicatorType=None,
                                                                                    TransformedData=self.mapped_data)
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Function returned result {}".format(field, new_dict[field]['Value']))

                        self._ValidateField(new_dict[field], field, rowType)

                    elif 'outputFormat' in fieldDict:
                        Value = self._BuildOutputFormatText(fieldDict, new_dict)
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Output format specified, building".format(field))
                        if Value:
                            new_dict[field] = fieldDict.copy()
                            new_dict[field]['Value'] = Value
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Value set to {}".format(field, Value))

                        self._ValidateField(new_dict[field], field, rowType)

                    elif 'datatype' in fieldDict and fieldDict['datatype'] == 'group':
                        if 'memberof' in fieldDict:
                            self.logging.warning(
                                "Sub-groups should not have 'required' set to true, processing skipped: %s", field)
                        else:
                            if field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Required group, building group row".format(field))
                            groupRow = {'fields': {}}
                            self._BuildFieldGroup(None, new_dict, rowType, field, groupRow, None)

                    else:
                        raise Exception('NoDefaultValue',
                                        'Default Value or outputFormat not defined for required field %s' % field)

        if not SubGroupedRow:
            for field in DataRow:
                if field not in processed_fields:
                    self.logging.warning('%s not processed for row type %s in schema config. Value: %s', field, rowType,
                                         DataRow[field])

            if rowType == "IndicatorData":
                self._AddIndicatorType(new_dict)
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Field processed, adding Indicator Type".format(field))

        return new_dict

    def _UpdateFieldReferences(self, subDict, GroupID, subfields):
        '''
        Update any key or value that equals one of the subfields with the name subfield_GroupID
        '''

        if GroupID:
            # Only rename entries if GroupID is > 0
            for (k, v) in subDict.items():
                if isinstance(v, dict):
                    self._UpdateFieldReferences(v, GroupID, subfields)
                elif isinstance(v, str):
                    if v in subfields:
                        subDict[k] = "%s_%i" % (v, GroupID)

        for k in subfields:
            if k in subDict:
                if GroupID:
                    # Only rename entries if GroupID is > 0
                    v = subDict.pop(k)
                    k = "%s_%i" % (k, GroupID)
                    subDict[k] = v
                subDict[k]['groupID'] = GroupID

        return subDict

    def _AddIndicatorType(self, newDict):
        """
        Determine the indicator type from the data and add a new field IndicatorType to the data row
        """
        if "types" not in self.SchemaConfig["IndicatorData"]:
            raise Exception("NoIndicatorTypes", "Indicator Types not defined in schema")

        '''
        The layout of the indicator types in the schema is a dictionary of indicator Types, which have a list of
        possible indicator matches, which have one or more required fields and values in a dictionary. The best match
        (based on weight, more exact matches have a higher weight) wins. In the case of a tie, the first match wins.
        Running through every possible type is a little slower, but it makes sure the best possible indicator
        types are chosen

        Example: "DNS-Hostname-Block": [ { "classification_text": "Domain Block:*" } ],
                If the classification_text field has a value of Domain Blocks:<anything> then the indicator type
                is determined to be a DNS-Hostname-Block. Multiple fields can be required for a single match, and
                multiple possible matches can be tried for a single indicator type
        '''

        bestMatch = None
        bestWeight = 0

        for indicatorType, indicatorMatches in self.SchemaConfig["IndicatorData"]["types"].items():
            for indicatorMatch in indicatorMatches:
                match = False
                Weight = 0
                for k, v in indicatorMatch.items():
                    matchKeys = {}

                    if k in newDict and 'Value' in newDict[k]:
                        matchKeys[k] = [newDict[k]['Value']]

                        prefix = "%s_" % k
                        for key in newDict:
                            if key.startswith(prefix):
                                if k not in matchKeys:
                                    matchKeys[k] = []
                                matchKeys[k].append(newDict[key]['Value'])

                    if len(matchKeys) > 0:
                        submatch = False
                        for key, values in matchKeys.items():
                            for value in values:
                                if v == "*" and value != "":
                                    Weight += 1
                                    submatch = True
                                elif v.endswith("*") and value.startswith(v.strip("*")):
                                    Weight += 5
                                    submatch = True
                                elif value == v:
                                    Weight += 10
                                    submatch = True

                        if submatch:
                            match = True
                        else:
                            match = False
                            Weight = 0
                            break

                    elif v == "":
                        Weight += 5
                        match = True
                    else:
                        match = False
                        Weight = 0
                        break

                if match and Weight > bestWeight:
                    bestMatch = indicatorType
                    bestWeight = Weight

        if bestMatch is not None:
            newDict["IndicatorType"] = bestMatch
            self.logging.debug("Determined best indicator type match of {}.".format(bestMatch))
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
        if self.trace and fieldName in self.traceindex:
            self.logging.debug("[TRACE {}] - Validating field with type {}".format(fieldName, dataType))

        values = []
        if 'Value' in fieldDict:
            if fieldDict['Value'] is None:
                raise Exception('FieldValueIsNone',
                                'Value for field %s is None' % (
                                fieldName))
            elif fieldDict['Value'].startswith('&'):
                raise Exception('ValueIsFunction',
                                'Value for field %s maps to a function which should already have been processed: %s' % (
                                fieldName, fieldDict['Value']))

            values.append(fieldDict['Value'])
            if self.trace and fieldName in self.traceindex:
                self.logging.debug("[TRACE {}] - Appended value {}".format(fieldName, fieldDict['Value']))

        if 'AdditionalValues' in fieldDict:
            values.extend(fieldDict['AdditionalValues'])
            if self.trace and fieldName in self.traceindex:
                self.logging.debug("[TRACE {}] - Appended additional values".format(fieldName))

        if values.__len__() == 0:
            raise Exception('NoValue', 'Field %s has no value' % fieldName)

        # TODO: ParsedValue only contains the last tested value if there are multiple values for the field. This might be a problem for some data types.

        for value in values:
            if dataType == 'string':
                # String data type is always valid, pass
                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - String data type; valid value {}.".format(fieldName, value))
                pass
            elif dataType == 'group':
                # Group data type is always valid, pass
                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - Group data type; valid value {}.".format(fieldName, value))
                pass
            elif dataType == 'int':
                fieldDict['ParsedValue'] = int(value)
                if str(fieldDict['ParsedValue']) != value:
                    raise Exception('DataTypeInvalid', 'Value for field ' + fieldName + ' is not an int: ' + value)
                if 'dataRange' in fieldDict:
                    datarange = fieldDict['dataRange'].split('-')
                    if fieldDict['ParsedValue'] < int(datarange[0]) or fieldDict['ParsedValue'] > int(datarange[1]):
                        raise Exception('DataOutOfRange',
                                        'The value for field ' + fieldName + ' is outside of the allowed range(' +
                                        fieldDict['dataRange'] + '): ' + value)
                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - int data type; valid value {}".format(fieldName, value))

            elif dataType == 'datetime':
                if 'dateTimeFormat' not in fieldDict:
                    raise Exception('SchemaConfigMissing',
                                    'The dateTimeFormat configuration is missing for field ' + fieldName)
                # TODO - Identify better method of handling function call cases for "&now()" & "&stix_now()"
                # Exists only to create "ParsedValue" when functions such as "&now()" & "&stix_now()" are used
                if "ParsedValue" not in fieldDict and "Value" in fieldDict and fieldDict['Value']:
                    if fieldDict['dateTimeFormat'] == 'unixtime':
                        fieldDict['ParsedValue'] = arrow.get(fieldDict['Value'])
                    else:
                        fieldDict['ParsedValue'] = arrow.get(fieldDict['Value'], fieldDict['dateTimeFormat'])
                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - datetime data type; valid value {}.".format(fieldName, value))
            elif dataType == 'enum':
                if value not in fieldDict['enumValues']:
                    # Check if there is a case mismatch, update the value to the correct case if there is.
                    caseUpdated = False
                    for k in fieldDict['enumValues']:
                        if value.lower() == k.lower():
                            fieldDict['Value'] = k
                            caseUpdated = True
                            break

                    if not caseUpdated:
                        raise Exception('DataTypeInvalid',
                                        'Value for field ' + fieldName + ' is not listed in the enum values: ' + value)
                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - enum data type; valid value {}.".format(fieldName, value))
            elif dataType == 'emailAddress':
                if EMAIL_REGEX.match(value) is None:
                    raise Exception('DataTypeInvalid',
                                    'Value for field ' + fieldName + ' is not a valid email address: ' + value)
                if fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - emailAddress data type; valid value {}.".format(fieldName, value))
            elif dataType == 'ipv4':
                try:
                    fieldDict['ParsedValue'] = socket.inet_aton(value)
                except:
                    raise Exception('DataTypeInvalid',
                                    'Value for field ' + fieldName + ' is not a valid ipv4 address: ' + value)
                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - ipv4 data type; valid value {}.".format(fieldName, value))
            elif dataType == 'ipv6':
                try:
                    fieldDict['ParsedValue'] = socket.inet_pton(socket.AF_INET6, value)
                except:
                    raise Exception('DataTypeInvalid',
                                    'Value for field ' + fieldName + ' is not a valid ipv6 address: ' + value)
                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}] - ipv6 data type; valid value {}.".format(fieldName, value))
            else:
                self.logging.error("No validation written for dataType: %s", dataType)

        return

    def _TransformDataToNewSchema(self, rowType, DataRow, DocumentHeaderData, DocumentMetaData, DerivedData, oracle=None):
        '''
        Transform the data row using the underlying ontology mappings to the new schema
        Parameters:
        * rowType
        * DataRow
        * DocumentHeader
        * DocumentMetadata
        * DerivedData
        * oracle - An instance of the OntologyOracle class which encapsulates the target schema ontology
                   If 'None', will not be used.

        TODO: Update to query ontology directly
        '''
        self.logging.debug("_TransformDataToNewSchema(self, rowType={}, ...)".format(rowType))
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE _TransformDataToNewSchema] - Monitoring {} elements".format(len(self.traceindex.keys())))


        # newDict stores the transformed data mapped into the target schema for this row
        newDict = {}
        IndicatorType = None

        if rowType == 'IndicatorData':

            # Determine if the target schema accepts Indicators of type IndicatorType
            if 'IndicatorType' in DataRow:
                IndicatorType = DataRow.pop('IndicatorType')

                # TODO: Update to query the ontology for supported indicator types
                if IndicatorType not in self.SchemaConfig["IndicatorData"]["types"]:
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
        DataDictionary = self._MapDataToOntology(DataRow, DocumentHeaderData, DocumentMetaData, DerivedData)

        # Build the dependency order for processing the target schema
        field_order = self._field_order[rowType]

        GroupRows = {}
        fieldcount = 0

        for field in field_order:
            # Iterate over each field in the target file schema, copying in data from the source as it is available.
            fieldcount = fieldcount + 1
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}]: Processing as field number {}".format(field, fieldcount))

            fieldDict = self.SchemaConfig[rowType]['fields'][field].copy()
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}] - Processing field mapping to target schema.".format(field))

            OntologyReferences = collections.defaultdict(list)
            OntologyReference = None

            # TODO: Chris - this is the code that should be replaced or supplemented with the Ontology Oracle
            if 'ontologyMappingType' in fieldDict:
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Field has ontologyMappingType {}".format(field, fieldDict['ontologyMappingType']))
                if fieldDict['ontologyMappingType'] == 'none':
                    # If there is no ontology mapping, this must be either a group or another aggregate type (e.g. a regex)
                    if 'datatype' in fieldDict and fieldDict['datatype'] == 'group':
                        if (field in GroupRows):
                            groupRow = GroupRows.pop(field)
                            #  -- Modifies 'newDict'[group] to contain values from source document
                            #     depending on mapping.
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Building group row for field without ontologyMapping.".format(field))
                            self._BuildFieldGroup(DataDictionary, newDict, rowType, field, groupRow, IndicatorType)
                            continue
                    elif 'outputFormat' in fieldDict and 'memberof' not in fieldDict:
                        # TODO:
                        # We're a combination of other fields; process unless we're a member of another group?
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Building combination row from fields specified in output format {}.".format(field, fieldDict['outputFormat']))
                    else:
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - No ontology mapping defined, no ontology reference added.".format(field, fieldDict['outputFormat']))

                elif fieldDict['ontologyMappingType'] == 'simple':
                    if fieldDict['ontologyMapping'] != '':
                        # Get the ontology reference we need in the destination schema:
                        OntologyReference = fieldDict['ontologyMapping']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Found ontology mapping {}".format(field, OntologyReference))
                            if OntologyReference not in self.traceindex[field]["dst_fields"]:
                                self.traceindex[field]["dst_IRIs"].append(OntologyReference)
                                self.traceindex[OntologyReference] = self.traceindex[field]
                        if self.trace and OntologyReference in self.traceindex:
                            self.logging.debug("[TRACE {}] - Ontology reference mapped to field {}".format(OntologyReference, field))
                            if field not in self.traceindex[OntologyReference]["dst_fields"]:
                                self.traceindex[OntologyReference]["dst_fields"].append(OntologyReference)
                                self.traceindex[field] = self.traceindex[OntologyReference]
                        if OntologyReference in DataDictionary:
                            # If the semantic value exists exactly in the data dictionary, we can use it
                            # directly; no oracle call is required.
                            OntologyReferences[OntologyReference].extend(DataDictionary[OntologyReference].keys())
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Adding DataDictionary[{}].keys() = {}".format(field, OntologyReference, DataDictionary[OntologyReference].keys()))
                            if self.trace and OntologyReference in self.traceindex:
                                self.logging.debug("[TRACE {}] - Adding for field {} DataDictionary[{}].keys() = {}".format(OntologyReference, field, OntologyReference, DataDictionary[OntologyReference].keys()))
                        elif oracle is not None:
                            # If we have a semantic mismatch, check the DataDictionary for ontology references which are
                            # either specializations (prefered) or generalizations of the concept.
                            # Lookup Ontology reference from the oracle instead:
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Using the oracle to get compatible concepts".format(field, OntologyReference))
                            oRefList = oracle.getCompatibleConcepts(OntologyReference)
                            for altOntologyReference in oRefList:
                                # For each possible value returned in oRefList, see if we have it in the data dictionary:
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Checking alternative ontology reference {} in DataDictionary".format(
                                                                        field, altOntologyReference))
                                if altOntologyReference.IRI.__str__() in DataDictionary:
                                    OntologyReferences[OntologyReference].extend(
                                        DataDictionary[altOntologyReference.IRI.__str__()].keys())
                                    if self.trace and field in self.traceindex:
                                        self.traceindex[field]["dst_IRIs"].append(OntologyReference)
                                        self.logging.debug("[TRACE {}] - Alternate reference found in DataDictionary for {}".format(
                                                                        field, altOntologyReference))
                                    # TODO: Re-enable this when we start checking supported vs. required
                                    # else:
                                    # logging.warn("Semantic match attempt found an ontology reference not in Data Dictionary (%s)"%altOntologyReference.IRI)

                elif fieldDict['ontologyMappingType'] == 'multiple':
                    # In the case of multiple possible fields, look up which one(s) are present:
                    if 'ontologyMappings' in fieldDict:
                        for OntologyReference in fieldDict['ontologyMappings']:
                            # TODO: Lookup Ontology reference from the oracle instead:
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Processing reference {} in multiple mappings list.".format(
                                                                field, OntologyReference))
                                self.traceindex[field]["dst_IRIs"].append(OntologyReference)
                            if OntologyReference != '':
                                if OntologyReference in DataDictionary:
                                    # If the semantic value exists exactly in the data dictionary, we can use it
                                    # directly; no oracle call is required.
                                    OntologyReferences[OntologyReference].extend(
                                        DataDictionary[OntologyReference].keys())
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Reference {} found in DataDictionary.".format(
                                                                field, OntologyReference))
                                else:
                                    # If we have a semantic mismatch, check the DataDictionary for ontology references which are
                                    # either specializations (prefered) or generalizations of the concept.
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Reference {} NOT found in DataDictionary.".format(
                                                                field, OntologyReference))
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

                elif fieldDict['ontologyMappingType'] == 'enum':
                    # If the destination field type is an enum, we need to determine what value to use for it
                    # based on the source's data values.  An enum ontology mapping type indicates that the value
                    # of the field carries a semantic significance, not just the field itself.
                    if 'enumValues' in fieldDict:
                        for k, v in fieldDict['enumValues'].items():
                            if v['ontologyMapping'] != '':
                                OntologyReference = v['ontologyMapping']
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Evaluating enum value mapping to ontology: {} => {}.".format(
                                                                field, k, OntologyReference))
                                if self.trace and OntologyReference in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Evaluating as reference for enum field {}, value {}.".format(
                                                                OntologyReference, field, k))
                                # if oracle is not None:
                                # oRefList = oracle.getCompatibleConcepts(OntologyReference)
                                # if len(oRefList) > 0 and OntologyReference in DataDictionary:
                                # OntologyReferences[OntologyReference].extend(DataDictionary[oRefList[0].IRI].keys())
                                # else:
                                if OntologyReference not in DataDictionary:
                                    # We don't have an exact match, so check the ontology for one:
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Ontology reference not found, checking oracle for alternative".format(
                                                                field, k, OntologyReference))
                                    if oracle is not None and False:
                                        oRefList = oracle.getCompatibleConcepts(OntologyReference)
                                        for altOntologyReference in oRefList:
                                            if altOntologyReference.IRI.__str__() in DataDictionary:
                                                logging.warn(
                                                    "Semantic mismatch detected (Type/Distance: %s/%d ; Source: %s ; Target: %s )" % (
                                                    altOntologyReference.stype, altOntologyReference.distance,
                                                    altOntologyReference.IRI, OntologyReference))
                                                OntologyReference = altOntologyReference.IRI.__str__()
                                    else:
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Oracle could not be reached; no value selected.".format(
                                                                field, k, OntologyReference))
                                if OntologyReference in DataDictionary:
                                    # If the ontology reference is in the DataDictionary, then it is something that is
                                    # provided by the source file
                                    if fieldDict['datatype'] == 'enum':
                                        # If the target file also represents this concept as an enum:
                                        OntologyReferences[OntologyReference].append(k)
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Adding ontology reference {} for enum value {}".format(
                                                                field, OntologyReference, k))
                                        if self.trace and OntologyReference in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Adding for field {}, enum value {}".format(
                                                                OntologyReference, field, k))
                                    else:
                                        # If the target file represents this concept as direct value:
                                        OntologyReferences[OntologyReference].extend(
                                            DataDictionary[OntologyReference].keys())
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Not an enum type, adding {} value references to list for {}.".format(
                                                                field, len(DataDictionary[OntologyReference].keys()), OntologyReference))
                                    continue

                                if 'reverseOntologyMappings' in v and isinstance(v['reverseOntologyMappings'], list):
                                    # If the source only has a single concept, but the target requires several other
                                    # schema elements to represent the concept:
                                    # Builds out a larger ontology on the target side; accommodate one-to-many
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Enum value {} defines reverse ontology mappings; processing.".format(
                                                                field, k))
                                    for reverseMapping in v['reverseOntologyMappings']:
                                        if reverseMapping in DataDictionary:
                                            if fieldDict['datatype'] == 'enum':
                                                OntologyReferences[OntologyReference].append(k)
                                                if self.trace and field in self.traceindex:
                                                    self.logging.debug("[TRACE {}] - Added reverse mapping {}->{} for enum value {}".format(
                                                                field, reverseMapping, OntologyReference, k))
                                            else:
                                                self.logging.warning(
                                                    'reverseOntologyMappings in field %s not supported because datatype is not enum',
                                                    k)
                                            break
                    else:
                        self.logging.warn("Field {} has type {}, but no enumValues are defined.".format(field,fieldDict['ontologyMappingType']))

                elif fieldDict['ontologyMappingType'] == 'referencedEnum':
                    referencedField = fieldDict['ontologyEnumField']
                    referencedValue = None
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Processing referenced field {} for enum value.".format(
                                                                field, referencedField))
                    if self.trace and referencedField in self.traceindex:
                        self.logging.debug("[TRACE {}] - Referenced in enum of field {}".format(
                                                                referencedField, field))

                    if 'memberof' in fieldDict:
                        # TODO: This needs to be expanded to support adding GroupIDs and mapping each referenced value if multiples exist
                        memberof = fieldDict['memberof']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Field is a memberof group {}".format(
                                                                field, memberof))
                        if memberof in GroupRows and 'fields' in GroupRows[memberof] and referencedField in GroupRows[memberof]['fields']:
                            referencedValue = GroupRows[memberof]['fields'][referencedField][0]['NewValue']
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Found referencedValue {} for referencedField{} in parent group {}".format(
                                                                field, referencedValue, referencedField, memberof))
                            if self.trace and referencedField in self.traceindex:
                                self.logging.debug("[TRACE {}] - Field referenced by {}, providing value {} due to reference by parent".format(
                                                                referencedField, field, referencedValue, memberof))

                    elif referencedField in newDict and 'Value' in newDict[referencedField]:
                        referencedValue = newDict[referencedField]['Value']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Found referencedValue {} for referencedField{}".format(
                                                                field, referencedValue, referencedField, memberof))
                        if self.trace and referencedField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Field referenced by {}, providing value {}".format(
                                                                referencedField, field, referencedValue))

                    if referencedValue:
                        if 'ontologyMappingEnumValues' in fieldDict:
                            if referencedValue in fieldDict['ontologyMappingEnumValues']:
                                if fieldDict['ontologyMappingEnumValues'][referencedValue]['ontologyMapping'] != '':
                                    OntologyReference = fieldDict['ontologyMappingEnumValues'][referencedValue][
                                        'ontologyMapping']
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Using ontology mapping {} from ontologyMappingEnumValues".format(
                                                                field, OntologyReference))

                            else:
                                for eValue in fieldDict['ontologyMappingEnumValues']:
                                    if ('*' in eValue and eValue != '*' and
                                            fieldDict['ontologyMappingEnumValues'][eValue][
                                                    'ontologyMapping'] != ''):
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Checking for wildcard matches for enum value {}".format(
                                                                field, eValue))
                                        if eValue.startswith('*'):
                                            if referencedValue.endswith(eValue.strip('*')):
                                                OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                    'ontologyMapping']
                                                if self.trace and field in self.traceindex:
                                                    self.logging.debug("[TRACE {}] - Wildcard prefix matched for {}".format(
                                                                field, OntologyReference))
                                                break
                                        elif eValue.endswith('*'):
                                            if referencedValue.startswith(eValue.strip('*')):
                                                OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                    'ontologyMapping']
                                                if self.trace and field in self.traceindex:
                                                    self.logging.debug("[TRACE {}] - Wildcard postfix matched for {}".format(
                                                                field, OntologyReference))
                                                break

                            if OntologyReference is None and "*" in fieldDict['ontologyMappingEnumValues']:
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - fieldDict ontology mapping enum value has a wildcard".format(
                                                                field))
                                if fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping'] != '':
                                    OntologyReference = fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping']
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Setting wildcard ontology reference {}".format(
                                                                field, OntologyReference))

                            # TODO: If this test fails, no direct map back to source.  Check the ontology for other options
                            if OntologyReference in DataDictionary:
                                OntologyReferences[OntologyReference].extend(DataDictionary[OntologyReference].keys())
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Found ontology reference {} in source Data Dictionary".format(
                                                                field, OntologyReference))
                        else:
                            raise Exception('ontologyMappingEnumValues',
                                            'ontologyMappingEnumValues missing from field %s' % field)
                    elif 'ontologyMappingEnumValues' in fieldDict and '' in fieldDict['ontologyMappingEnumValues']:
                        OntologyReference = fieldDict['ontologyMappingEnumValues']['']['ontologyMapping']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Enum values contains empty string; using match {}".format(
                                                                field, OntologyReference))
                else:
                    raise Exception('UnknownOntologyMappingType',
                                    'The OntologyMappingType %s in field %s is undefined' % (
                                    fieldDict['ontologyMappingType'], field))

            else:
                raise Exception('MissingOntologyMappingType',
                                'The OntologyMappingType is missing from field %s' % field)

            if len(OntologyReferences) == 0 and 'reverseOntologyMappings' in fieldDict:
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - No ontology mappings found; processing reverse mappings.".format(
                                                                field))
                for reverseMapping in fieldDict['reverseOntologyMappings']:
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Checking reverse mapping {}".format(
                                                                field, reverseMapping))
                    if reverseMapping in DataDictionary:
                        OntologyReference = reverseMapping
                        OntologyReferences[OntologyReference].extend(DataDictionary[OntologyReference].keys())
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Found reverse mapping in data dictionary; using reference {}".format(
                                                                field, OntologyReference))
                        break

            if len(OntologyReferences) == 0:
                # No mapped data found, check if the field is required and if so if there is a default value
                # Raise an exception if a required field has no data
                if field in self.traceindex:
                    self.logging.debug("[TRACE {}] - No mapped data found; checking requirement for output.".format(
                                                                field))
                required = False

                if 'requiredIfReferenceField' in fieldDict:
                    ReferenceField = fieldDict['requiredIfReferenceField']
                    if 'requiredIfReferenceValues' in fieldDict:
                        ReferenceValues = fieldDict['requiredIfReferenceValues']
                        for val in ReferenceValues:
                            if (ReferenceField in newDict and val == newDict[ReferenceField]['Value']) or \
                                    (val == '' and (ReferenceField not in newDict or
                                                    not newDict[ReferenceField]['Value'])):
                                required = True
                                break

                    elif 'requiredIfReferenceValuesMatch' in fieldDict:
                        if ReferenceField in newDict:
                            ReferenceValuesMatch = fieldDict['requiredIfReferenceValuesMatch']
                            for val in ReferenceValuesMatch:
                                if val == '*':
                                    if 'Value' in newDict[ReferenceField]:
                                        required = True
                                        break
                                elif val.endswith('*'):
                                    if ('Value' in newDict[ReferenceField] and newDict[ReferenceField][
                                            'Value'].startswith(val.strip('*'))):
                                        required = True
                                        break
                                    else:
                                        match = re.match(val, newDict[ReferenceField]['Value'])
                                        if match:
                                            required = True
                                            break

                if required == True or ('required' in fieldDict and fieldDict['required'] == True):
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Required; checking default value".format(
                                                                field))
                    if 'defaultValue' in fieldDict:
                        newDict[field] = fieldDict.copy()
                        newDict[field]['Value'] = fieldDict['defaultValue']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Default value found {}.".format(
                                                                field, newDict[field]['Value']))

                        if newDict[field]['Value'].startswith('&'):
                            newDict[field]['Value'] = self._CalculateFunctionValue(newDict[field]['Value'], field,
                                                                                   newDict[field], rowType, newDict,
                                                                                   IndicatorType,
                                                                                   TransformedData=self.transformed_data)
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Default value was a function reference, computed new value {}".format(
                                                                field, newDict[field]['Value']))

                        self._ValidateField(newDict[field], field, rowType)

                    elif 'outputFormat' in fieldDict:
                        Value = self._BuildOutputFormatText(fieldDict, newDict)
                        if Value:
                            newDict[field] = fieldDict.copy()
                            newDict[field]['Value'] = Value

                            self._ValidateField(newDict[field], field, rowType)

                    elif 'datatype' in fieldDict and fieldDict['datatype'] == 'group':
                        if 'memberof' in fieldDict:
                            self.logging.warning(
                                "Sub-groups should not have 'required' set to true, processing skipped: %s", field)
                        else:
                            groupRow = {'fields': {}}
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Processing subfields of group.".format(
                                                                field))
                            self._BuildFieldGroup(DataDictionary, newDict, rowType, field, groupRow, IndicatorType)
                    else:
                        raise Exception('NoDefaultValue',
                                        'Default Value or outputFormat not defined for required field %s' % field)
                else:
                    # The field is not required:
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Not required; leaving out of main data dictionary".format(field))

                    '''
                    # TODO: This should probably be another ontologyMapping type - perhaps regexComposition? It should be reinstated, but just check
                    #       for 'memberOf'.
                    # However, if we can construct a value from its component parts, we should use that:
                    if ('outputFormat' in fieldDict):
                        Value = self._BuildOutputFormatText(fieldDict, newDict)
                        if field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Constructed Value {} from outputFormat".format(field, Value))
                        if (Value):
                            newDict[field] = fieldDict.copy()
                            newDict[field]['Value'] = Value

                            self._ValidateField(newDict[field], field, rowType)
                            self.logging.debug("newDict (for rowType {}) is now:".format(rowType))
                    '''


            else:
                # One or more values found
                if 'memberof' in fieldDict:
                    # Field is part of a group, handle using special group processing code
                    memberof = fieldDict['memberof']
                    if self.trace and field in self.traceindex:
                        self.logging.debug("[TRACE {}] - Field is part of a group {}; processing value".format(
                                                                field, memberof))

                    while 'memberof' in self.SchemaConfig[rowType]['fields'][memberof]:
                        # This is a subgroup, add to the parent group
                        memberof = self.SchemaConfig[rowType]['fields'][memberof]['memberof']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - We are a subgroup; adding to parent group {}".format(
                                                                field, memberof))
                        if self.trace and memberof in self.traceindex:
                            self.logging.debug("[TRACE {}] - Member field {} is adding data to us.".format(
                                                                memberof, field))

                    if memberof not in GroupRows:
                        GroupRows[memberof] = {'fields': {}}
                    if field not in GroupRows[memberof]['fields']:
                        GroupRows[memberof]['fields'][field] = []

                    for OntologyReference in OntologyReferences:
                        for Value in OntologyReferences[OntologyReference]:
                            newFieldDict = fieldDict.copy()
                            newFieldDict['matchedOntology'] = OntologyReference
                            NewValue = Value
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Set ontology reference to {}, and value to {}".format(
                                                                field, OntologyReference, Value))
                            if OntologyReference in DataDictionary and Value in DataDictionary[OntologyReference]:
                                sourceDict = DataDictionary[OntologyReference][Value]

                                if 'groupID' in sourceDict:
                                    newFieldDict['groupID'] = sourceDict['groupID']

                                NewValue = self._ConvertValueToTargetSchema(field, fieldDict, sourceDict, Value)
                                if NewValue is None:
                                    raise Exception('ValueNotConverted',
                                                    'Data could not be converted to the target schema [{0}]'.format(
                                                        Value))

                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Got new value {}".format(
                                                                field, NewValue))
                            newFieldDict['NewValue'] = NewValue

                            GroupRows[memberof]['fields'][field].append(newFieldDict)

                else:
                    if fieldDict['ontologyMappingType'] == 'multiple':
                        # Fields with multiple ontology mappings are listed in best first order
                        # This finds the best possible match and uses that in the translation

                        for OntologyReference in fieldDict['ontologyMappings']:
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Multiple type, processing ontology reference {}".format(
                                                                field, OntologyReference))
                            if OntologyReference in OntologyReferences:
                                for Value in OntologyReferences[OntologyReference]:
                                    if field not in newDict:
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Field matched ontology reference {}; creating newDict with value {}".format(
                                                                field, OntologyReference, Value))
                                        newDict[field] = fieldDict.copy()
                                        newDict[field]['matchedOntology'] = OntologyReference
                                        NewValue = Value
                                        if Value in DataDictionary[OntologyReference]:
                                            sourceDict = DataDictionary[OntologyReference][Value]
                                            NewValue = self._ConvertValueToTargetSchema(field, fieldDict, sourceDict,
                                                                                        Value)
                                            if self.trace and field in self.traceindex:
                                                self.logging.debug("[TRACE {}] - Created NewValue {} from Value {}".format(
                                                                field, NewValue, Value))
                                            if NewValue is None:
                                                raise Exception('ValueNotConverted',
                                                                'Data could not be converted to the target schema [{0}]'.format(
                                                                    Value))
                                        newDict[field]['Value'] = NewValue
                                    elif 'multiple' in fieldDict and fieldDict['multiple'] == True:
                                        # TODO: Handle fields with multiple values
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Handling fields with multiple values not yet supported; skipping.".format(
                                                                field, NewValue, Value))
                                        self.logging.warning("Fields with multiple values for the destination not yet supported; skipping {}".format(field))
                                        pass
                                    else:
                                        break

                                break
                    else:
                        for OntologyReference in OntologyReferences:
                            for Value in OntologyReferences[OntologyReference]:
                                if field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Processing OntologyReference {} Value {}".format(
                                                                field, OntologyReference, Value))
                                if field not in newDict:
                                    newDict[field] = fieldDict.copy()
                                    newDict[field]['matchedOntology'] = OntologyReference
                                    NewValue = Value
                                    if OntologyReference in DataDictionary and Value in DataDictionary[OntologyReference]:
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Both ontology reference and value are in the data dictionary.".format(
                                                                field))
                                        sourceDict = DataDictionary[OntologyReference][Value]
                                        NewValue = self._ConvertValueToTargetSchema(field, fieldDict, sourceDict, Value)
                                        if NewValue is None:
                                            raise Exception('ValueNotConverted',
                                                            'Data could not be converted to the target schema [{0}]'.format(
                                                                Value))
                                    newDict[field]['Value'] = NewValue
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Produced NewValue for field {}".format(
                                                                field, NewValue))
                                elif 'multiple' in fieldDict and fieldDict['multiple'] == True:
                                    # TODO: Handle fields with multiple values
                                    self.logging.warning("Fields with multiple values for the destination not yet supported; skipping {}".format(field))
                                else:
                                    break

                            if 'multiple' not in fieldDict or fieldDict['multiple'] == False:
                                if self.trace and field in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Not a multiple value field.".format(field))
                                break

                        try:
                            self._ValidateField(newDict[field], field, rowType)
                        except Exception as inst:
                            self.logging.info("Validation failed for %s, %s", field, inst)
                            newDict.pop(field)
            self._populate_implied_ontology_values(DataDictionary)

        if len(GroupRows) != 0:
            self.logging.error("A group has subrow data that was never processed: %s", GroupRows)

        # Populate implied ontology values:
        self._populate_implied_ontology_values(DataDictionary)

        return newDict

    def _BuildFieldGroup(self, DataDictionary, groupDict, rowType, group, groupRow, IndicatorType, fullNewDict = None):
        '''
        Takes the group data and updates the groupDict with the new groupedFields configuration.
        * DataDictionary - the Mapping of ontology IRIs to data values from the source
        * groupDict - the fields that have been populated so far in the destination schema
        * rowType - one of Indicator or ... (?)
        * group - the group field ID being processed
        * groupRow - the data row for this group from the schema configuration
        * IndicatorType - needed if this is an indicator row
        * fullNewDict - on recursive calls to this method, groupDict is the slice of dictionary for the parent of this group.
        *               In cases where we need to refer to a value which is not a member of the direct parent dictionary, fullNewDict
        *               can be used.
        '''

        '''
        TODO: This function is still messy and needs a lot more work. It works okay for most of the common use cases
        but will likely be broken for more complex groups

        ** Where does the group association need to be preserved to ensure that related indicators are still related on
           output?
        '''

        # Make sure fullNewDict is always a valid dictionary reference
        if fullNewDict == None:
            fullNewDict = groupDict

        if self.trace and group in self.traceindex:
            self.logging.debug("[TRACE {}] - BuildFieldGroup(rowType = {})".format(group, rowType))

        if group not in groupDict:
            groupDict[group] = self.SchemaConfig[rowType]['fields'][group].copy()
            groupDict[group]['Value'] = 'True'
            groupDict[group]['ParsedValue'] = True
            groupDict[group]['groupedFields'] = []

        subfields = self.SchemaConfig[rowType]['fields'][group]['subfields']
        if self.trace and group in self.traceindex:
            self.logging.debug("[TRACE {}]: Subfield keys are: {}".format(group, ",".join(self.SchemaConfig[rowType]['fields'][group]['subfields'].keys())))

        # Build the list of required fields for this group

        '''
        subfields should be a dictionary like the following:

        "subfields": {
                        "reasonList_reasonCategory": {"required":true, "primaryKey":true},
                        "reasonList_reasonDescription": {"required":false}
        }
        '''

        # Add default values for fields to group if defined

        # TODO: But what about cases where the field is already defined? - It seems this happens first (?)
        if 'defaultFields' in self.SchemaConfig[rowType]['fields'][group]:
            defaultFields = self.SchemaConfig[rowType]['fields'][group]['defaultFields']
            if self.trace and group in self.traceindex:
                self.logging.debug("[TRACE {}] - Processing default fields".format(group))
            for k, v in defaultFields.items():
                if self.trace and k in self.traceindex:
                    self.logging.debug("[TRACE {}] - Processing as one of the default fields for group {}".format(k, group))
                if k not in groupRow['fields']:
                    if self.trace and k in self.traceindex:
                        self.logging.debug("[TRACE {}] - Not found in existing fields for {}; creating new".format(k, group))
                    groupRow['fields'][k] = []

                    if isinstance(v, list):
                        if self.trace and k in self.traceindex:
                            self.logging.debug("[TRACE {}] - Processing list of default values for {}".format(k, group))
                        for v2 in v:
                            fieldDict = {}
                            fieldDict['ReferencedField'] = None
                            fieldDict['ReferencedValue'] = None
                            fieldDict['matchedOntology'] = None

                            if v2.startswith('&'):
                                v2f = v2
                                v2 = self._CalculateFunctionValue(v2f, k, self.SchemaConfig[rowType]['fields'][k],
                                                                  rowType, groupDict, IndicatorType,
                                                                  TransformedData=self.transformed_data)
                                if self.trace and k in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Value {} was a function reference; computed value {}".format(k, v2, v2f))

                            fieldDict['NewValue'] = v2
                            groupRow['fields'][k].append(fieldDict)
                    else:
                        fieldDict = {}
                        fieldDict['ReferencedField'] = None
                        fieldDict['ReferencedValue'] = None
                        fieldDict['matchedOntology'] = None

                        if self.trace and k in self.traceindex:
                            self.logging.debug("[TRACE {}] - Default value defined in group {}: {}".format(k, group, v))

                        if v.startswith('&'):
                            vf = v
                            v = self._CalculateFunctionValue(vf, k, self.SchemaConfig[rowType]['fields'][k], rowType,
                                                             groupDict, IndicatorType,
                                                             TransformedData=self.transformed_data)
                            if self.trace and k in self.traceindex:
                                self.logging.debug("[TRACE {}] - Value {} was a function reference; computed value {}".format(k, vf, v))

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

        # For each subfield, distribute between primaryKey, required, and other field lists. Also process available values from the full data dictionary:
        for k, v in subfields.items():
            if 'primaryKey' in v and v['primaryKey'] == True:
                if primaryKey is None:
                    primaryKey = k
                    if self.trace and group in self.traceindex:
                        self.logging.debug("[TRACE {}] - Set primary key to {}".format(group, k))
                    if self.trace and k in self.traceindex:
                        self.logging.debug("[TRACE {}] - Processing as primary key to group {}".format(k, group))
                else:
                    raise Exception('MultiplePrimaryKeys',
                                    'Group %s has multiple primaryKeys defined, that is not supported' % group)

            elif 'required' in v and v['required'] == True:
                requiredFields.append(k)
                if self.trace and group in self.traceindex:
                    self.logging.debug("[TRACE {}] - Added required field {} to required list.".format(group, k))
                if self.trace and k in self.traceindex:
                    self.logging.debug("[TRACE {}] - Added as a required field for group {}".format(k, group))

            else:
                otherFields.append(k)
                if self.trace and group in self.traceindex:
                    self.logging.debug("[TRACE {}] - Added other field {} to group member list.".format(group, k))
                if self.trace and k in self.traceindex:
                    self.logging.debug("[TRACE {}] - Added as other field for group {}".format(k, group))

            # See if fields have values that can be defined:
            if k not in groupRow['fields']:
                if self.trace and k in self.traceindex:
                    self.logging.debug("[TRACE {}] - Not found in groupRow['fields']; check to see if it is in groupDict ({}).".format(
                                        k, k in self.SchemaConfig[rowType]['fields']))
                # See if we can compose a value from components; look at fields defined in schema config:
                if k in self.SchemaConfig[rowType]['fields'] and 'outputFormat' in self.SchemaConfig[rowType]['fields'][k]:
                    # TODO: This should probably be another ontologyMapping type - perhaps regexComposition?
                    # However, if we can construct a value from its component parts, we should use that:
                    groupRow['fields'][k] = []
                    fieldDict = copy.deepcopy(self.SchemaConfig[rowType]['fields'][k])
                    fieldDict['ReferencedField'] = None
                    fieldDict['ReferencedValue'] = None
                    fieldDict['matchedOntology'] = None
                    Value = self._BuildOutputFormatText(fieldDict, fullNewDict)
                    if self.trace and k in self.traceindex:
                        self.logging.debug("[TRACE {}] - Using composed value {} for groupRow in group {}".format(k, Value, group))
                    fieldDict['NewValue'] = Value
                    groupRow['fields'][k].append(fieldDict)

                    '''
                elif self.SchemaConfig[rowType]['fields'][k]['datatype'] == 'group':
                    fieldDict = copy.deepcopy(self.SchemaConfig[rowType]['fields'][k])
                    fieldDict['ReferencedField'] = None
                    fieldDict['ReferencedValue'] = None
                    fieldDict['matchedOntology'] = None
                    if k in self.traceindex:
                        self.logging.debug("[TRACE {}] - Using composed value {} for groupRow in group {}".format(k, Value, group))
                    fieldDict['Value'] = 'True'
                    fieldDict['ParsedValue'] = True
                    fieldDict['groupedFields'] = []

                    if requiredField in self.traceindex:
                        self.logging.debug("[TRACE {}] - Subgroup of {}...".format(requiredField, group))
                    if group in self.traceindex:
                        self.logging.debug("[TRACE {}] - Required field {} is a subgroup; building.".format(group, requiredField))

                    # TODO: So, at this point, we have a required field which is actually a subgroup, and has no
                    # value of its own. Is it possible to send the entire newDict rather than the fieldGroup subset?
                    # No - the fieldGroup is the dictionary slice that has begun to be built at this execution level.
                    #      instead, we need a way to keep the full set of determined values available - we can either use an instance variable,
                    #      or we can pass the "full" groupDict as an optional variable. For now we will do the latter:
                    self._BuildFieldGroup(DataDictionary, fieldGroup, rowType, k, groupRow,
                                          IndicatorType, fullNewDict = groupDict)
                    '''
                else:
                    self.logging.info("No default value provided for group {} field {}, and no value could be composed from an output format.".format(
                                                                                group, k))

        if primaryKey is None:
            raise Exception('primaryKeyNotDefined', 'primaryKey not defined for group %s' % group)

        if primaryKey not in groupRow['fields']:
            if 'defaultValue' in self.SchemaConfig[rowType]['fields'][primaryKey]:
                if self.trace and group in self.traceindex:
                    self.logging.debug("[TRACE {}] - Primary key for {}, but not defined; Using default value(s).".format(primaryKey, group))
                fieldDict = {}
                fieldDict['matchedOntology'] = None
                fieldDict['NewValue'] = self.SchemaConfig[rowType]['fields'][primaryKey]['defaultValue']
                groupRow['fields'][primaryKey] = [fieldDict]
                if self.trace and group in self.traceindex:
                    self.logging.debug("[TRACE {}] - Primary key {} not defined; using default value {}.".format(group, primaryKey, fieldDict['NewValue']))
                if self.trace and primaryKey in self.traceindex:
                    self.logging.debug("[TRACE {}] - Not found in available fields; using default value {}".format(primaryKey, fieldDict['NewValue']))
            else:
                self.logging.info('primaryKey not found for group %s and no defaultValue defined', group)
                return

        for fieldDict in groupRow['fields'][primaryKey]:
            # Create one group for each dictionary for each unique primary key value
            # Each primary key value will result in a copy of the group dictionary, and will contain
            # all fields marked as 'required' for the group.
            #
            fieldGroup = {}
            fieldGroup[primaryKey] = self.SchemaConfig[rowType]['fields'][primaryKey].copy()
            fieldGroup[primaryKey]['matchedOntology'] = fieldDict['matchedOntology']
            fieldGroup[primaryKey]['Value'] = fieldDict['NewValue']
            if self.trace and primaryKey in self.traceindex:
                self.logging.debug("[TRACE {}] - Creating copy of group {} for value {} ".format(primaryKey, group, fieldGroup[primaryKey]['Value']))
            if self.trace and group in self.traceindex:
                self.logging.debug("[TRACE {}] - Creating copy of group for primary key value {}".format(group, fieldGroup[primaryKey]['Value']))

            if (fieldGroup[primaryKey]['Value'].startswith('&')):
                fieldGroup[primaryKey]['Value'] = self._CalculateFunctionValue(fieldGroup[primaryKey]['Value'],
                                                                               primaryKey, fieldGroup, rowType,
                                                                               fieldGroup, IndicatorType,
                                                                               TransformedData=self.transformed_data)

            self._ValidateField(fieldGroup[primaryKey], primaryKey, rowType)

            groupID = None
            if 'groupID' in fieldDict:
                groupID = fieldDict['groupID']
                if self.trace and primaryKey in self.traceindex:
                    self.logging.debug("[TRACE {}] - Creating group ID {} for group {}, value {}".format(primaryKey, groupID, group, fieldGroup[primaryKey]['Value']))
                if self.trace and group in self.traceindex:
                    self.logging.debug("[TRACE {}] - Group ID {} assigned to PK Value {} = {}".format(group, groupID, primaryKey, fieldGroup[primaryKey]['Value']))

            # Populate the required fields. Pull first from those directly assigned to this group ID;
            #    if that fails, see if there's only one group instance, in that case just lump them all together;
            #    if *that* fails, check to see if the ontology maping type is enumerated, and if so if the enumerated value is intended for this group instance.
            for requiredField in requiredFields:
                if self.trace and requiredField in self.traceindex:
                    self.logging.debug("[TRACE {}] - Identified as required field for group {}; evaluating membership for groupID {}".format(requiredField, group, groupID))
                if requiredField in groupRow['fields']:
                    # Only add required fields if the groupID matches (in the case of multiple group instances)
                    if groupID is not None:
                        for k in groupRow['fields'][requiredField]:
                            if 'groupID' in k and k['groupID'] == groupID:
                                fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()
                                fieldGroup[requiredField]['Value'] = k['NewValue']
                                fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']
                                if self.trace and requiredField in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Adding as required field for group {} ID {} with value {} and ontology ref {}.".format(requiredField, group, groupID, k['NewValue'], k['matchedOntology']))

                    # If there is only one group, assume required fields belong to the same group.
                    elif len(groupRow['fields'][primaryKey]) == 1 and len(groupRow['fields'][requiredField]) == 1:
                        k = groupRow['fields'][requiredField][0]
                        fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()
                        fieldGroup[requiredField]['Value'] = k['NewValue']
                        fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']
                        if self.trace and requiredField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Adding as required field for group {} (only one instance) with value {} and ontology ref {}.".format(requiredField, group, k['NewValue'], k['matchedOntology']))

                    # If there is no group ID for a required field, but there *are* multiple group primary key values,
                    # see if any of the values given for the required field are specified to match this primary key
                    # value.
                    # TODO: Why only for enumerated ontology mapping types?
                    elif self.SchemaConfig[rowType]['fields'][requiredField]['ontologyMappingType'] == 'enum':
                        # Check if the enum value maps back to a specific primary key value
                        if self.trace and requiredField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Could not find a value for group ID {}:{}; checking enumerated ontology values.".format(requiredField, group, groupID))

                        # For each fieldDict associated with this required field
                        for k in groupRow['fields'][requiredField]:
                            # If it was assigned a value, and the value is defined in the set of enum values for this
                            # field definition, then if that enum value defines a primaryKeyMatch which matches *this* one,
                            # use it.
                            if ('NewValue' in k and k['NewValue'] in
                                self.SchemaConfig[rowType]['fields'][requiredField]['enumValues'] and
                                    'primaryKeyMatch' in
                                    self.SchemaConfig[rowType]['fields'][requiredField]['enumValues'][
                                        k['NewValue']]):

                                primaryKeyMatch = \
                                    self.SchemaConfig[rowType]['fields'][requiredField]['enumValues'][k['NewValue']][
                                        'primaryKeyMatch']
                                if primaryKeyMatch == fieldGroup[primaryKey]['Value']:
                                    if requiredField not in fieldGroup:
                                        fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][
                                            requiredField].copy()
                                        fieldGroup[requiredField]['Value'] = k['NewValue']
                                        fieldGroup[requiredField]['matchedOntology'] = k['matchedOntology']
                                    elif subfields[requiredField]['addAdditionalValues']:
                                        additionalValueFields.append({requiredField: k})
                                    else:
                                        break
                                    if self.trace and requiredField in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Populated from enum value {}, with ontology reference {}.".format(requiredField, k['NewValue'], k['matchedOntology']))

                    # TODO [CS] - I think we need to check primaryKeyMatch for simple ontology mappings too?
                    else:
                        self.logging.warning('Required field %s could not be matched to the appropriate group',
                                             requiredField)

                # If the required field is not in the fieldGroup, meaning it hasn't already been populated from
                # somewhere else for this group instantiation:
                if requiredField not in fieldGroup:
                    if self.trace and requiredField in self.traceindex:
                        self.logging.debug("[TRACE {}] - Creating default field definition from schema config for group {}".format(requiredField, group))
                    if self.trace and group in self.traceindex:
                        self.logging.debug("[TRACE {}] - Required field {} not defined by data; using default value.".format(group, requiredField))

                    # Create a new entry for this field, copying from the field definition.
                    fieldGroup[requiredField] = self.SchemaConfig[rowType]['fields'][requiredField].copy()

                    if self.trace and requiredField in self.traceindex:
                        self.logging.debug("[TRACE {}] - primaryKeyMatch? {} primaryKeyMatchValue: {}".format(requiredField, 'primaryKeyMatch' in fieldGroup[requiredField], fieldGroup[requiredField]['primaryKeyMatch']))
                    if 'defaultValue' in fieldGroup[requiredField]:
                        fieldGroup[requiredField]['Value'] = fieldGroup[requiredField]['defaultValue']

                    elif 'primaryKeyMatch' not in fieldGroup[requiredField] or fieldGroup[requiredField]['primaryKeyMatch'] == fieldGroup[primaryKey]['Value']:
                        if fieldGroup[requiredField]['datatype'] == 'group':
                            fieldGroup[requiredField]['Value'] = 'True'
                            fieldGroup[requiredField]['ParsedValue'] = True
                            fieldGroup[requiredField]['groupedFields'] = []

                            if self.trace and requiredField in self.traceindex:
                                self.logging.debug("[TRACE {}] - Subgroup of {}...".format(requiredField, group))
                            if self.trace and group in self.traceindex:
                                self.logging.debug("[TRACE {}] - Required field {} is a subgroup; building.".format(group, requiredField))

                            # TODO: So, at this point, we have a required field which is actually a subgroup, and has no
                            # value of its own. Is it possible to send the entire newDict rather than the fieldGroup subset?
                            # No - the fieldGroup is the dictionary slice that has begun to be built at this execution level.
                            #      instead, we need a way to keep the full set of determined values available - we can either use an instance variable,
                            #      or we can pass the "full" groupDict as an optional variable. For now we will do the latter:
                            self._BuildFieldGroup(DataDictionary, fieldGroup, rowType, requiredField, groupRow,
                                              IndicatorType, fullNewDict = groupDict)
                            continue
                    else:
                        if 'primaryKeyMatch' in fieldGroup[requiredField]:
                            self.logging.debug("Primary key specified in subfield {}: {} does not match group primary key value ({})".format(
                                                                        requiredField, fieldGroup[requiredField], fieldGroup[primaryKey]['Value']))

                        self.logging.error('Field %s for group %s is required, but could not be assigned a value. Early abort will likely result in an invalid document.', requiredField, group)
                        return

                    # Don't validate fields that are set to function names until after the function is processed
                    if fieldGroup[requiredField]['Value'].startswith('&'):
                        fieldGroup[requiredField]['Value'] = self._CalculateFunctionValue(
                                fieldGroup[requiredField]['Value'], requiredField, fieldGroup, rowType, fieldGroup,
                                IndicatorType, TransformedData=None)
                        if self.trace and requiredField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Value was a function; evaluated to: {}".format(requiredField, fieldGroup[requiredField]['Value']))

                    self._ValidateField(fieldGroup[requiredField], requiredField, rowType)

            for otherField in otherFields:
                if self.trace and otherField in self.traceindex:
                    self.logging.debug("[TRACE {}] - Evaluating as non-required member of group {}".format(otherField, group))
                if self.trace and group in self.traceindex:
                    self.logging.debug("[TRACE {}] - Evaluating non-required field {}".format(group, otherField))

                # It will only be in groupRow['fields'] if a default value is set for it:
                if otherField in groupRow['fields']:
                    if self.trace and otherField in self.traceindex:
                        self.logging.debug("[TRACE {}] - Found in groupRow['fields']".format(otherField))
                    # Determine if any of the defined fields match this primary key
                    if groupID is not None:
                        if self.trace and otherField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Checking for matching groupID {}".format(otherField, groupID))
                        # Iterate through the dictionary values assigned to this field in groupRow to see if any of them are intended for this group ID
                        for k in groupRow['fields'][otherField]:
                            if 'groupID' in k and k['groupID'] == groupID:
                                fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                                fieldGroup[otherField]['Value'] = k['NewValue']
                                fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']
                                if self.trace and otherField in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Matched group ID {}:{}".format(otherField, group, groupID))
                                if self.trace and group in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Using field {} for group ID {}".format(group, otherField, groupID))
                                if self.trace and fieldGroup[otherField]['matchedOntology'] in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Mapped to groupID {}:{} to field {} with value {}".format(
                                                                    fieldGroup[otherField]['matchedOntology'],
                                                                    group,
                                                                    groupID,
                                                                    otherField,
                                                                    fieldGroup[otherField]['Value']))

                    elif len(groupRow['fields'][primaryKey]) == 1 and len(groupRow['fields'][otherField]) == 1:
                        # If there is only one group and only one value for otherField, assume it's intended for this group
                        k = groupRow['fields'][otherField][0]
                        fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                        fieldGroup[otherField]['Value'] = k['NewValue']
                        fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']
                        if self.trace and otherField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Using value {} for group {}".format(otherField, k['NewValue'], group))
                        if self.trace and group in self.traceindex:
                            self.logging.debug("[TRACE {}] - Using field {} = {}".format(group, otherField, k['NewValue']))
                        if self.trace and fieldGroup[otherField]['matchedOntology'] in self.traceindex:
                            self.logging.debug("[TRACE {}] - Mapped to group {} (only one group instance), to field {} with value {}".format(
                                                                    fieldGroup[otherField]['matchedOntology'],
                                                                    group,
                                                                    otherField,
                                                                    fieldGroup[otherField]['Value']))

                    # In this case, if the primary key match for the field is given in the schema, see if it matches this group primary key value:
                    # TODO: It may also be because the groupIDs aren't being set for the ACS3.0 marking_structures group?
                    elif fieldGroup and 'primaryKeyMatch' in subfields[otherField]:
                        if self.trace and otherField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Checking for matching primaryKey {}".format(otherField, subfields[otherField]['primaryKeyMatch']))
                        for k in groupRow['fields'][otherField]:
                            if subfields[otherField]['primaryKeyMatch'] == fieldGroup[primaryKey]['Value']:
                                b = True
                                if otherField not in fieldGroup:
                                    fieldGroup[otherField] = self.SchemaConfig[rowType]['fields'][otherField].copy()
                                    fieldGroup[otherField]['Value'] = k['NewValue']
                                    fieldGroup[otherField]['matchedOntology'] = k['matchedOntology']
                                    if self.trace and fieldGroup[otherField]['matchedOntology'] in self.traceindex:
                                        self.logging.debug("[TRACE {}] - Mapped to group {} on primaryKeyMatch {}, to field {} with value {}".format(
                                                                    fieldGroup[otherField]['matchedOntology'],
                                                                    group,
                                                                    fieldGroup[primaryKey]['Value'],
                                                                    otherField,
                                                                    fieldGroup[otherField]['Value']))
                                    b = False
                                elif subfields[otherField]['addAdditionalValues']:
                                    additionalValueFields.append({otherField: k})
                                    b = False
                                else:
                                    self.logging.debug("{} Already in field Group for {}:{}; skipping update.".format(otherField,group,subfields[otherField]['primaryKeyMatch']))
                                if self.trace and otherField in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Primary key matched ({}); using value {}".format(otherField, subfields[otherField]['primaryKeyMatch'], k['NewValue']))
                                if self.trace and group in self.traceindex:
                                    self.logging.debug("[TRACE {}] - Primary key matched ({}) with field {}; using value {}".format(group, subfields[otherField]['primaryKeyMatch'], otherField, k['NewValue']))
                                #TODO: Is this break actually needed?
                                if b:
                                    break
                    else:
                        self.logging.warning('Field %s could not be matched to the group %s', otherField, group)
                elif 'primaryKeyMatch' in subfields[otherField] and subfields[otherField]['primaryKeyMatch'] == fieldGroup[primaryKey]['Value']:
                    # Field didn't have a default value set; could be an optional subgroup data type:
                    if otherField in self.traceindex:
                        self.logging.debug("[TRACE {}] - Checking for matching primaryKey {}".format(otherField, subfields[otherField]['primaryKeyMatch']))
                    newDict = self.SchemaConfig[rowType]['fields'][otherField].copy()
                    if newDict['datatype'] == 'group':
                        newDict['Value'] = 'True'
                        newDict['ParsedValue'] = True
                        newDict['groupedFields'] = []

                        if self.trace and otherField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Optional subgroup of {}...".format(otherField, group))
                        if self.trace and group in self.traceindex:
                            self.logging.debug("[TRACE {}] - Optional field {} matches primaryKey value and is a subgroup; building.".format(group, otherField))

                        # TODO: So, at this point, we have a required field which is actually a subgroup, and has no
                        # value of its own. Is it possible to send the entire newDict rather than the fieldGroup subset?
                        # No - the fieldGroup is the dictionary slice that has begun to be built at this execution level.
                        #      instead, we need a way to keep the full set of determined values available - we can either use an instance variable,
                        #      or we can pass the "full" groupDict as an optional variable. For now we will do the latter:
                        fieldGroup[otherField] = newDict
                        self._BuildFieldGroup(DataDictionary, fieldGroup, rowType, otherField, groupRow,
                                          IndicatorType, fullNewDict = groupDict)
                        continue
                else:
                    self.logging.info("Field {} does not exist in groupRow['fields'] for group {}; cannot add value.".format(otherField, group))

            # If the fieldGroup was successfully defined, add them to the group dictionary!
            if fieldGroup:
                groupDict[group]['groupedFields'].append(fieldGroup)
                # If there are additional value fields, create additional groups for them?
                # TODO: Why?
                if len(additionalValueFields) > 0:
                    for field in additionalValueFields:
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Processing as an additionalValueField for group {}".format(field, group))
                        if self.trace and group in self.traceindex:
                            self.logging.debug("[TRACE {}] - Processing additional value field {}.".format(group, field))
                        for k, v in field.items():
                            newFieldGroup = copy.deepcopy(fieldGroup)
                            newFieldGroup.pop(k)
                            newFieldGroup[k] = self.SchemaConfig[rowType]['fields'][k].copy()
                            newFieldGroup[k]['Value'] = v['NewValue']
                            newFieldGroup[k]['matchedOntology'] = v['matchedOntology']
                            groupDict[group]['groupedFields'].append(newFieldGroup)
        #TODO: Add tracing for all matchedOntology elements as well!

    def _ConvertValueToTargetSchema(self, field, fieldDict, sourceDict, Value):
        '''
        field - Field name
        fieldDict - the target schema field description dictionary
        sourceDict - the source schema field description dictionary
        Value - the source value that needs to be converted

        Convert data formats between source and target schemas
        '''
        new_value = None
        if self.trace and field in self.traceindex:
            self.logging.debug("[TRACE {}] - Converting value {} to target schema".format(field, Value))

        if fieldDict['datatype'] == 'datetime':
            if 'ParsedValue' in sourceDict:
                if fieldDict['dateTimeFormat'] == 'unixtime':
                    # new_value = time.mktime(sourceDict['ParsedValue'].timetuple())
                    new_value = str(sourceDict['ParsedValue'].timestamp)
                else:
                    new_value = sourceDict['ParsedValue'].format(fieldDict['dateTimeFormat'])
                if field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Datetime value converted to {}".format(field, new_value))
            else:
                # TODO: ParsedValue should always exist, but I got errors when testing some CISCP STIX documents, need to test further
                self.logging.error('DateTime data type did not have a ParsedValue defined for field %s (%s)', field,
                                   fieldDict)

        elif fieldDict['datatype'] != sourceDict['datatype']:
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}] - source datatype {} != destination ({})".format(field, sourceDict['datatype'], fieldDict['datatype']))
            if fieldDict['datatype'] == 'string' or fieldDict['datatype'] == 'enum':
                new_value = Value
            else:
                if fieldDict['datatype'] == 'ipv4' and re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', Value):
                    new_value = Value
                else:
                    # FIXME: Process value to appropriate type for target schema
                    self.logging.warning("Cannot convert between data types for field %s (%s, %s)", field,
                                         fieldDict['datatype'], sourceDict['datatype'])
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}] - Converted to new datatype: {} -> {}".format(field, Value, new_value))

        else:
            new_value = Value
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}] - No conversion necessary; using value {}".format(field, new_value))

        return new_value

    def _MapDataToOntology(self, DataRow, DocumentHeaderData, DocumentMetaData, DerivedData):
        '''
        Builds a dictionary that maps each ontology concept to all the values in the source data, and their associated schema field configuration dictionary
        Combines the all the data from the data row, optional document header data and optional document meta data

        Example:
        {
            OntologyConcept = { 'Value': { field: dictionary, field2: data, ... } }
        }
        '''
        if self.trace and len(self.traceindex) > 0:
            self.logging.debug("[TRACE _MapDataToOntology] - Monitoring {} elements".format(len(self.traceindex.keys())))

        # Result data dictionary
        DataDictionary = {}

        # CombinedDataRow aggregates the data from the document header, metadata and the specific data row into one dictionary
        CombinedDataRow = {}

        # Start with the least specific data, which is the derived data
        if DerivedData is not None:
            CombinedDataRow.update(DerivedData)

        # Next, add in the document header data
        if DocumentHeaderData is not None:
            for k, v in DocumentHeaderData.items():
                if self.trace and k in self.traceindex:
                    self.logging.debug("[TRACE {}] - Mapping ontology reference from DocumentHeaderData".format(k))
                if k in CombinedDataRow:
                    self.logging.warning(
                        'Key %s already exists in data row, value %s, overwritten by DocumentHeaderData key with value %s',
                        k, CombinedDataRow[k], v)
            CombinedDataRow.update(DocumentHeaderData)

        # Check to see if any of the header data is overridden by the document metadata.
        if DocumentMetaData is not None:
            for k, v in DocumentMetaData.items():
                if self.trace and k in self.traceindex:
                    self.logging.debug("[TRACE {}] - Mapping ontology reference from DocumentMetaData".format(k))
                if k in CombinedDataRow:
                    self.logging.warning(
                        'Key %s already exists in data row, value %s, overwritten by DocumentMetaData key with value %s',
                        k, CombinedDataRow[k], v)

            CombinedDataRow.update(DocumentMetaData)

        if DataRow is not None:
            # Check to see if the specific data overrides the document header data or document metadata
            for k, v in DataRow.items():
                if self.trace and k in self.traceindex:
                    self.logging.debug("[TRACE {}] - Mapping ontology reference from source DataRow".format(k))
                if k in CombinedDataRow:
                    self.logging.warning(
                        'Key %s already exists in data row, value %s, overwritten by DataRow key with value %s', k,
                        CombinedDataRow[k], v)

            CombinedDataRow.update(DataRow)
        for field, fieldDict in CombinedDataRow.items():
            if 'Value' not in fieldDict:
                self.logging.warning("Field %s has no value", field)
                continue
            if 'discardBeforeTranslation' in fieldDict and fieldDict['discardBeforeTranslation'] == True:
                # TODO - Add logging of ignore flag processed
                continue
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}] - Mapping with value {}".format(field, fieldDict['Value']))

            Values = []

            Values.append(fieldDict['Value'])
            if self.trace and field in self.traceindex:
                self.logging.debug("[TRACE {}] - Appended value {}".format(field, fieldDict['Value']))

            if 'AdditionalValues' in fieldDict:
                Values.extend(fieldDict['AdditionalValues'])
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Appended values from AdditionalValues".format(field))

            for Value in Values:
                if self.trace and field in self.traceindex:
                    self.logging.debug("[TRACE {}] - Getting ontologyMapping for value {}".format(field, Value))
                OntologyReference = None
                AdditionalOntologyReferences = []

                if 'ontologyMappingType' in fieldDict:
                    if fieldDict['ontologyMappingType'] == 'none':
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - No ontology mapping for value {}; skipping.".format(field, Value))
                        continue

                    elif fieldDict['ontologyMappingType'] == 'simple':
                        if fieldDict['ontologyMapping'] != '':
                            OntologyReference = fieldDict['ontologyMapping']
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - {} -> {}".format(field, Value, OntologyReference))

                    elif fieldDict['ontologyMappingType'] == 'multiple':
                        if 'ontologyMappings' in fieldDict:
                            for mapping in fieldDict['ontologyMappings']:
                                if mapping != '':
                                    if OntologyReference is None:
                                        OntologyReference = mapping
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - {} -> {}".format(field, Value, OntologyReference))
                                    else:
                                        AdditionalOntologyReferences.append(mapping)
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - {} -> AdditionalOntologyReferences.append({})".format(field, Value, OntologyReference))

                    #TODO: We should add an 'enumMultiple' mapping type
                    elif fieldDict['ontologyMappingType'] == 'enum':
                        if 'enumValues' in fieldDict:
                            if Value in fieldDict['enumValues']:
                                if fieldDict['enumValues'][Value]['ontologyMapping'] != '':
                                    OntologyReference = fieldDict['enumValues'][Value]['ontologyMapping']
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - {} -> {} from enumValue match".format(
                                                                                field, Value, OntologyReference))

                            else:
                                for eValue in fieldDict['enumValues']:
                                    if '*' in eValue and eValue != '*' and fieldDict['enumValues'][eValue][
                                            'ontologyMapping'] != '':
                                        if eValue.startswith('*'):
                                            if Value.endswith(eValue.strip('*')):
                                                OntologyReference = fieldDict['enumValues'][eValue]['ontologyMapping']
                                                if self.trace and field in self.traceindex:
                                                    self.logging.debug("[TRACE {}] - {} -> {} from enumValue suffix match {}".format(
                                                                                field, Value, OntologyReference, eValue))
                                                break
                                        elif eValue.endswith('*'):
                                            if Value.startswith(eValue.strip('*')):
                                                OntologyReference = fieldDict['enumValues'][eValue]['ontologyMapping']
                                                if self.trace and field in self.traceindex:
                                                    self.logging.debug("[TRACE {}] - {} -> {} from enumValue prefix match {}".format(
                                                                                field, Value, OntologyReference, eValue))
                                                break

                            if OntologyReference is None and "*" in fieldDict['enumValues']:
                                if fieldDict['enumValues']['*']['ontologyMapping'] != '':
                                    OntologyReference = fieldDict['enumValues']['*']['ontologyMapping']
                                    if self.trace and field in self.traceindex:
                                        self.logging.debug("[TRACE {}] - {} -> {} from enumValue wildcard match *".format(
                                                                                field, Value, OntologyReference))

                        else:
                            raise Exception('MissingEnumValues', 'enumValues missing from field %s' % field)

                    elif fieldDict['ontologyMappingType'] == 'referencedEnum':
                        referencedField = fieldDict['ontologyEnumField']
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - References field {} for ontology reference".format(
                                                                                field, referencedField))
                        if self.trace and referencedField in self.traceindex:
                            self.logging.debug("[TRACE {}] - Referenced by field {} for ontology reference".format(
                                                                                referencedField, field))
                        if referencedField in DataRow and 'Value' in DataRow[referencedField]:
                            # TODO: Will this ever need to use ParsedValue?
                            referencedValue = DataRow[referencedField]['Value']
                            if 'ontologyMappingEnumValues' in fieldDict:
                                if referencedValue in fieldDict['ontologyMappingEnumValues']:
                                    if fieldDict['ontologyMappingEnumValues'][referencedValue][
                                            'ontologyMapping'] != '':
                                        OntologyReference = fieldDict['ontologyMappingEnumValues'][referencedValue][
                                            'ontologyMapping']
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Mapping to ontology from referenced field: {}({}) -> {}".format(
                                                                                field, referencedField, referencedValue, OntologyReference))
                                        if self.trace and referencedField in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Referenced by {} -> {}".format(
                                                                                referencedField, field, OntologyReference))

                                else:
                                    for eValue in fieldDict['ontologyMappingEnumValues']:
                                        if ('*' in eValue and eValue != '*' and
                                                    fieldDict['ontologyMappingEnumValues'][eValue][
                                                        'ontologyMapping'] != ''):
                                            if eValue.startswith('*'):
                                                if referencedValue.endswith(eValue.strip('*')):
                                                    OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                        'ontologyMapping']
                                                    if self.trace and field in self.traceindex:
                                                        self.logging.debug("[TRACE {}] - Taking value from enum suffix match in referenced field {}({}): {} -> {}".format(
                                                                                field, referencedField, eValue, referencedValue, OntologyReference))
                                                    if self.trace and referencedField in self.traceindex:
                                                        self.logging.debug("[TRACE {}] - Providing value from enum suffix match for field {}".format(
                                                                                referencedField, field))
                                                    break
                                            elif eValue.endswith('*'):
                                                if referencedValue.startswith(eValue.strip('*')):
                                                    OntologyReference = fieldDict['ontologyMappingEnumValues'][eValue][
                                                        'ontologyMapping']
                                                    if self.trace and field in self.traceindex:
                                                        self.logging.debug("[TRACE {}] - Taking value from enum prefix match in referenced field {}({}): {} -> {}".format(
                                                                                field, referencedField, eValue, referencedValue, OntologyReference))
                                                    if self.trace and referencedField in self.traceindex:
                                                        self.logging.debug("[TRACE {}] - Providing value from enum prefix match for field {}".format(
                                                                                referencedField, field))
                                                    break

                                if OntologyReference is None and "*" in fieldDict['ontologyMappingEnumValues']:
                                    if fieldDict['ontologyMappingEnumValues']['*']['ontologyMapping'] != '':
                                        OntologyReference = fieldDict['ontologyMappingEnumValues']['*'][
                                            'ontologyMapping']
                                        if self.trace and field in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Taking value from wildcard match in referenced field {}(*): {} -> {}".format(
                                                                                field, referencedField, referencedValue, OntologyReference))
                                        if self.trace and referencedField in self.traceindex:
                                            self.logging.debug("[TRACE {}] - Providing value from wildcard match for field {}".format(
                                                                                referencedField, field))
                            else:
                                raise Exception('ontologyMappingEnumValues',
                                                'ontologyMappingEnumValues missing from field %s' % field)
                        elif ('ontologyMappingEnumValues' in fieldDict and '' in fieldDict[
                            'ontologyMappingEnumValues']):
                            OntologyReference = fieldDict['ontologyMappingEnumValues']['']['ontologyMapping']
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Referenced field {} not defined; taking value from blank match".format(
                                                                                field, referencedField))
                            if self.trace and referencedField in self.traceindex:
                                self.logging.debug("[TRACE {}] - Not defined in DataRow even though referenced by {}".format(
                                                                                referencedField, field))

                    else:
                        raise Exception('UnknownOntologyMappingType',
                                        'The OntologyMappingType %s in field %s is undefined' % (
                                        fieldDict['ontologyMappingType'], field))

                else:
                    raise Exception('MissingOntologyMappingType',
                                    'The OntologyMappingType is missing from field %s' % field)

                if OntologyReference is not None:

                    # Some schemas included namespace or other data in the value of the field, which should be stripped before transformation
                    # to the target schema.
                    if 'stripNamespace' in fieldDict:
                        Value = Value.replace(fieldDict['stripNamespace'], '')
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Stripped namespace from value {}".format(
                                                                                field, Value))

                    AdditionalOntologyReferences.insert(0, OntologyReference)
                    for Reference in AdditionalOntologyReferences:
                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Checking additional ontology reference {}".format(
                                                                                field, Reference))
                        if self.trace and Reference in self.traceindex:
                            self.logging.debug("[TRACE {}] - Mapping from field {}".format(
                                                                                Reference, field))
                        if Reference not in DataDictionary:
                            DataDictionary[Reference] = {}
                        elif Value in DataDictionary[Reference]:
                            # self.logging.debug("Value %s is already mapped to Ontology concept %s, skipping new mapping from field %s" % (Value, Reference, field))
                            if self.trace and field in self.traceindex:
                                self.logging.debug("[TRACE {}] - Additional ontology reference {} already mapped to value {}; skipping".format(
                                                                                Reference, field, Value))
                            if self.trace and Reference in self.traceindex:
                                self.logging.debug("[TRACE {}] - Skipping mapping from field {}, existing value {} preserved.".format(
                                                                                Reference, field, Value))
                            continue

                        if self.trace and field in self.traceindex:
                            self.logging.debug("[TRACE {}] - Setting target ontology reference value: DataDictionary[{}][{}]".format(
                                                                                field, Reference, Value))
                        if self.trace and Reference in self.traceindex:
                            self.logging.debug("[TRACE {}] - Setting value from field {}, value {} to dict {}".format(
                                                                                Reference, field, Value, fieldDict))
                        DataDictionary[Reference][Value] = fieldDict

        return DataDictionary

    def _populate_implied_ontology_values(self, DataMapping):
        '''
        Given a dictionary keyed on ontology concepts, will also include concepts which are implied (according to the
        ontology) but not explicitly defined in the source document. For example, mapping TLP:AMBER to the set of restrictions
        implied by the AMBER value.

        TODO: Eventually this needs to be done in the ontology.

        Example:
        {
            OntologyConcept = { 'Value': { field: dictionary, field2: data, ... } }
            ImpliedConcept  = { 'Value': { field: dictionary, field2: data, ... } }
        }
        '''
        # TODO: Move this to the ontology:
        implication_map = {
            'http://www.anl.gov/cfm/transform.owl#HeaderTLPWhiteSemanticConcept':
                [
                    "http://www.anl.gov/cfm/transform.owl#PublicCFM13SharingRestrictionSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#DocumentDefaultSharingPermitSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeAnonymousAccessSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeScopeALLSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeAllowSemanticConcept"
                ],
            'http://www.anl.gov/cfm/transform.owl#HeaderTLPGreenSemanticConcept':
                [
                    "http://www.anl.gov/cfm/transform.owl#NeedToKnowCFM13SharingRestrictionSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#DocumentDefaultSharingDenySemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeAnonymousAccessSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeScopeALLSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeDenySemanticConcept"
                ],
            'http://www.anl.gov/cfm/transform.owl#HeaderTLPAmberSemanticConcept':
                [
                    "http://www.anl.gov/cfm/transform.owl#PrivateCFM13SharingRestrictionSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#DocumentDefaultSharingDenySemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeAnonymousAccessSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeScopeALLSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeDenySemanticConcept"
                ],
            'http://www.anl.gov/cfm/transform.owl#HeaderTLPRedSemanticConcept':
                [
                    "http://www.anl.gov/cfm/transform.owl#PrivateCFM13SharingRestrictionSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#DocumentDefaultSharingDenySemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeAnonymousAccessSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeScopeALLSemanticConcept",
                    "http://www.anl.gov/cfm/transform.owl#AccessPrivilegeDenySemanticConcept"
                ],
            'http://www.anl.gov/cfm/transform.owl#ReconNotAllowedSemanticConcept':
                [
                    "http://www.anl.gov/cfm/transform.owl#DocumentDefaultPrivilegeDenySemanticConcept"
                ],
            'http://www.anl.gov/cfm/transform.owl#ReconAllowedSemanticConcept':
                [
                    "http://www.anl.gov/cfm/transform.owl#DocumentDefaultPrivilegePermitSemanticConcept"
                ]
            }

        for concept in implication_map:
            if concept in DataMapping:
                for impliedConcept in implication_map[concept]:
                    if self.trace and impliedConcept not in DataMapping:
                        self.logging.info("Adding implied concept: {} (from source concept {})".format(impliedConcept,
                                                                                                       concept))
                        DataMapping[impliedConcept] = DataMapping[concept]

    def _BuildOutputFormatText(self, fieldDict, newDict):

        # Build a new value based on the output format, if it exists
        # Regex match returns two values into a set. [0] is anything that isn't a field name and [1] is a field name
        # New value replaces [field] with the value of that field and outputs everything else out directly
        if 'outputFormatCondition' in fieldDict:
            condition = self._outputFormatRE.findall(fieldDict['outputFormatCondition'])
            conditionMet = True
            evalString = ''
            if condition:
                for m in condition:
                    if m[0] != '':
                        evalString += m[0]
                    if m[1] != '':
                        if m[1] in newDict and 'Value' in newDict[m[1]]:
                            evalString += newDict[m[1]]['Value']
                        else:
                            conditionMet = False
                            break

                if conditionMet and evalString:
                    if not eval(evalString):
                        # Condition is not met, do not generate output format
                        return None
            else:
                # Condition is not met, do not generate output format
                return None

        match = self._outputFormatRE.findall(fieldDict['outputFormat'])
        if match:
            Value = ''
            AllFields = True
            for m in match:
                if m[0] != '':
                    #self.logging.debug("Appending value {}".format(m[0]))
                    Value += m[0]
                if m[1] != '':
                    #self.logging.debug("Using value for field {}".format(m[1]))
                    if m[1] in newDict and 'Value' in newDict[m[1]]:
                        Value += newDict[m[1]]['Value']
                        if self.trace and m[1] in self.traceindex:
                            self.logging.debug("[TRACE {}]: Using value {} from newDict in outputFormat {}".format(m[1], newDict[m[1]]['Value'], fieldDict['outputFormat']))
                    elif 'required' in fieldDict and fieldDict['required'] == True:
                        raise Exception('NoDefaultValue', 'Default Value not defined for required field %s' % m[1])
                    else:
                        AllFields = False
                        self.logging.warn("Could not process field {} ; value will not be built.".format(m[1]))
                        break

            # Check that all fields required for the output formated text exist, or delete the field from the results
            if AllFields:
                return Value
        else:
            self.logging.warn("Could not process outputFormat {} (using RE {}); returning None".format(fieldDict['outputFormat'], self._outputFormatRE))

        return None

    def _CalculateFunctionValue(self, value, fieldName, fieldDict, rowType, row=None, IndicatorType=None,
                                TransformedData=None):
        '''
        '''
        if value.startswith('&'):
            if self.trace and fieldName in self.traceindex:
                self.logging.debug("[TRACE {}]: Evaluating function value: {}".format(fieldName, value))
            match = re.match(r'&([^\(]+)\((.*)\)$', value)
            if match:
                function = match.group(1)
                functionarg = match.group(2)

                FunctionScopeValid = self.FunctionManager.get_function_scope(rowType, function)

                if self.trace and fieldName in self.traceindex:
                    self.logging.debug("[TRACE {}]: Extracted function name {}, args {} with scope validity {}".format(
                                                        fieldName, function, functionarg, FunctionScopeValid))

                if FunctionScopeValid:

                    args = {
                        'fieldName': fieldName,
                        'fieldDict': fieldDict,
                        'functionArg': functionarg,
                        'currentRow': row,
                        'indicatorType': IndicatorType,
                        'transformedData': TransformedData
                    }

                    value = self.FunctionManager.execute_transform_function(rowType, function, args)

                else:
                    self.logging.warning('Function %s in field %s is not valid for current document scope %s', function,
                                         fieldName, rowType)
            else:
                raise Exception('InvalidFunctionFormat',
                                'The function reference for field %s, %s, is not valid' % (fieldName, value))
        else:
            self.logging.warning('Value %s is not a function reference', value)

        if self.trace and fieldName in self.traceindex:
            self.logging.debug("[TRACE {}]: Function {}({}) produced value {}".format(
                                                        fieldName, function, functionarg, value))
        return value

    @classmethod
    def FlattenDict(cls, NestedDict, ParentKey='', Sep=';'):
        '''
        Takes a nested dictionary, and rewrites it to a flat dictionary, where each nested key is appended to the
        top level key name, separated with Sep

        For example:
        '''

        items = []
        for k, v in NestedDict.items():
            new_key = ParentKey + Sep + k if ParentKey else k
            if isinstance(v, collections.MutableMapping):
                items.extend(SchemaParser.FlattenDict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @classmethod
    def UnflattenDict(cls, FlatDict, Sep=';'):
        '''
        Reverse the FlattenDict action and expand the dictionary back out

        For example:
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
