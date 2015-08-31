'''
Created on Jun 1, 2015

@author: ahoying
'''
import unittest
import os

import logging
import json

from FlexTransform import FlexTransform
from .TestData import CFM13Data

class CFM13Tests(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s', level=logging.DEBUG)
        
        self.Transform = FlexTransform.FlexTransform()  # @UndefinedVariable
        
        currentdir = os.path.dirname(__file__)
        Cfm13AlertConfig = open(os.path.join(currentdir,'../resources/sampleConfigurations/cfm13.cfg'), 'r')
        self.Transform.AddParser('Cfm13Alert', Cfm13AlertConfig)
        
        LQMToolsConfig = open(os.path.join(currentdir,'../resources/sampleConfigurations/lqmtools.cfg'), 'r')
        self.Transform.AddParser('LQMTools', LQMToolsConfig)
        
        StixConfig = open(os.path.join(currentdir,'../resources/sampleConfigurations/stix_cfm.cfg'), 'r')
        self.Transform.AddParser('STIX', StixConfig)
        
        self.CFM13Data = CFM13Data()

    def test_cfm13_to_lqmtools(self):
        
        sample_cfm13_file = self.CFM13Data.getFile()
        
        ExpectedDataList  = [{"action1": "Block", 
                              "comment": "WEBattack", 
                              "detectedTime": "1432998480", 
                              "directSource": "TEST", 
                              "duration1": "2592000", 
                              "fileHasMore": "0", 
                              "indicator": "192.168.123.231", 
                              "indicatorType": "IPv4Address", 
                              "priors": "1", 
                              "reason1": "unknown", 
                              "reconAllowed": "1", 
                              "reference1": "unknown", 
                              "reportedTime": "1432998645", 
                              "restriction": "AMBER", 
                              "secondaryIndicator": "badsite.example.int", 
                              "secondaryIndicatorType": "DNSDomainName", 
                              "sensitivity": "noSensitivity"},
                             {"action1": "Block", 
                              "comment": "Netflow port or host scan", 
                              "detectedTime": "1432998540", 
                              "directSource": "TEST", 
                              "duration1": "36000", 
                              "fileHasMore": "0", 
                              "indicator": "172.20.40.120", 
                              "indicatorType": "IPv4Address", 
                              "majorTags": "Scanning", 
                              "priors": "2", 
                              "reason1": "Netflow port or host scan", 
                              "reconAllowed": "1", 
                              "reference1": "user-specific", 
                              "reportedTime": "1432998645", 
                              "restriction": "AMBER", 
                              "secondaryIndicator": "another.evil.site", 
                              "secondaryIndicatorType": "DNSDomainName", 
                              "sensitivity": "noSensitivity"},
                              {"action1": "Block",
                              "comment": "MSSQL scans against multiple hosts, direction:ingress, confidence:77, severity:medium",
                              "detectedTime": "1432998560",
                              "directSource": "TEST",
                              "duration1": "86400",
                              "fileHasMore": "0",
                              "indicator": "172.17.17.172",
                              "indicatorType": "IPv4Address",
                              "majorTags": "Scanning",
                              "priors": "5",
                              "reason1": "Scanning",
                              "reconAllowed": "1",
                              "reference1": "user-specific",
                              "reportedTime": "1432998645",
                              "restriction": "AMBER",
                              "sensitivity": "noSensitivity"},
                             {"action1": "Notify",
                              "comment": "URL Block: Random String",
                              "detectedTime": "1432998540",
                              "directSource": "TEST",
                              "duration1": "0",
                              "fileHasMore": "0",
                              "indicator": "http://bad.domain.url/?ref=RANDOM_STRING",
                              "indicatorType": "URL",
                              "majorTags": "Phishing",
                              "priors": "0",
                              "reason1": "target: bad.domain.url",
                              "reconAllowed": "0",
                              "reference1": "user-specific",
                              "reportedTime": "1432998645",
                              "restriction": "AMBER",
                              "sensitivity": "ouo"},
                             {"action1": "Notify",
                              "comment": "Domain Block: malicious",
                              "detectedTime": "1432998360",
                              "directSource": "TEST",
                              "duration1": "0",
                              "fileHasMore": "0",
                              "indicator": "malicious.domain",
                              "indicatorType": "DNSDomainName",
                              "priors": "0",
                              "reason1": "unknown",
                              "reconAllowed": "0",
                              "reference1": "unknown",
                              "reportedTime": "1432998645",
                              "restriction": "AMBER",
                              "sensitivity": "ouo"}]

        FinalizedData = self.Transform.TransformFile(sourceFileName=sample_cfm13_file, sourceParserName='Cfm13Alert', targetParserName='LQMTools')
         
        self.assertEqual(len(ExpectedDataList),len(FinalizedData))
        
        for idx, val in enumerate(ExpectedDataList) :
            # The processedTime key changes with each run, so ignore it
            FinalizedData[idx].pop('processedTime')
            self.assertDictEqual(val,FinalizedData[idx])

    def test_cfm13_to_stix(self):
        
        sample_cfm13_file = self.CFM13Data.getFile()

        ExpectedDataDict = {'DocumentHeaderData': {'handling': [{'controlled_structure': '//node()',
                                                                  'marking_structures': [{'color': 'AMBER',
                                                                                          'xsi:type': 'tlpMarking:TLPMarkingStructureType'}]}],
                                                    'id': '',
                                                    'information_source': {'description': 'TEST',
                                                                           'identity': {'name': 'TEST'},
                                                                           'time': {'produced_time': '2015-05-30T09:10:45+0000'}},
                                                    'package_intents': [{'value': 'Indicators',
                                                                         'xsi:type': 'stixVocabs:PackageIntentVocab-1.0'}],
                                                    'version': '1.1.1'},
                             'IndicatorData': [{'IndicatorType': 'IPv4-Address-Block',
                                                'description': 'WEBattack',
                                                'handling': [{'controlled_structure': 'ancestor-or-self::stix:Indicator//node()',
                                                'marking_structures': [{'statement': 'OUO=False, '
                                                                                     'ReconAllowed=True, '
                                                                                     'SharingRestrictions=private',
                                                                        'xsi:type': 'simpleMarking:SimpleMarkingStructureType'}]}],
                                                'indicator_types': [{'value': 'IP Watchlist',
                                                                     'xsi:type': 'stixVocabs:IndicatorTypeVocab-1.1'}],
                                                'observable': {'object': {'properties': {'address_value': {'condition': 'Equals',
                                                                                                           'value': '192.168.123.231'},
                                                                                         'category': 'ipv4-addr',
                                                                                         'xsi:type': 'AddressObjectType'},
                                                                          'related_objects': [{'properties': {'value': {'condition': 'Equals',
                                                                                                                        'value': 'badsite.example.int'},
                                                                                                              'xsi:type': 'DomainNameObjectType'},
                                                                                               'relationship': 'Resolved_To'}]},
                                                               'sighting_count': '1'},
                                                'sightings': {'sightings': [{'timestamp': '2015-05-30T09:08:00',
                                                                             'timestamp_precision': 'second'}],
                                                              'sightings_count': '2'},
                                                'suggested_coas': {'suggested_coas': [{'course_of_action': {'description': 'Blocked '
                                                                                                                           'for '
                                                                                                                           '2592000 '
                                                                                                                           'seconds',
                                                                                                            'stage': 'Remedy',
                                                                                                            'type': 'Perimeter '
                                                                                                                    'Blocking'}}]},
                                                'version': '2.1.1'},
                                               {'IndicatorType': 'IPv4-Address-Block',
                                                'description': 'Netflow port or host scan',
                                                'handling': [{'controlled_structure': 'ancestor-or-self::stix:Indicator//node()',
                                                              'marking_structures': [{'statement': 'OUO=False, ReconAllowed=True, SharingRestrictions=private',
                                                                                      'xsi:type': 'simpleMarking:SimpleMarkingStructureType'}]}],
                                                'indicator_types': [{'value': 'IP Watchlist',
                                                                     'xsi:type': 'stixVocabs:IndicatorTypeVocab-1.1'}],
                                                'observable': {'keywords': ['Scanning'],
                                                               'object': {'properties': {'address_value': {'condition': 'Equals',
                                                                                                           'value': '172.20.40.120'},
                                                                                         'category': 'ipv4-addr',
                                                                                         'xsi:type': 'AddressObjectType'},
                                                                          'related_objects': [{'properties': {'value': {'condition': 'Equals',
                                                                                                                        'value': 'another.evil.site'},
                                                                                                              'xsi:type': 'DomainNameObjectType'},
                                                                                               'relationship': 'Resolved_To'},
                                                                                              {'properties': {'port_value': '22',
                                                                                                              'xsi:type': 'PortObjectType'},
                                                                                               'relationship': 'Connected_To'}]}},
                                                'sightings': {'sightings': [{'timestamp': '2015-05-30T09:09:00',
                                                                             'timestamp_precision': 'second'}],
                                                              'sightings_count': '3'},
                                                'suggested_coas': {'suggested_coas': [{'course_of_action': {'description': 'Host '
                                                                                                                           'scan',
                                                                                                            'stage': 'Remedy',
                                                                                                            'type': 'Perimeter '
                                                                                                                    'Blocking'}}]},
                                                'version': '2.1.1'},
                                               {'IndicatorType': 'IPv4-Address-Block',
                                                'description': 'MSSQL scans against multiple hosts, '
                                                               'direction:ingress, confidence:77, '
                                                               'severity:medium',
                                                'handling': [{'controlled_structure': 'ancestor-or-self::stix:Indicator//node()',
                                                              'marking_structures': [{'statement': 'OUO=False, ReconAllowed=True, SharingRestrictions=public',
                                                                                      'xsi:type': 'simpleMarking:SimpleMarkingStructureType'}]}],
                                                'indicator_types': [{'value': 'IP Watchlist',
                                                                     'xsi:type': 'stixVocabs:IndicatorTypeVocab-1.1'}],
                                                'observable': {'keywords': ['Scanning'],
                                                               'object': {'properties': {'address_value': {'condition': 'Equals',
                                                                                                           'value': '172.17.17.172'},
                                                                                         'category': 'ipv4-addr',
                                                                                         'xsi:type': 'AddressObjectType'},
                                                                          'related_objects': [{'properties': {'layer4_protocol': 'TCP',
                                                                                                              'port_value': '3306',
                                                                                                              'xsi:type': 'PortObjectType'},
                                                                                               'relationship': 'Connected_To'},
                                                                                              {'properties': {'layer4_protocol': 'TCP',
                                                                                                              'port_value': '1433',
                                                                                                              'xsi:type': 'PortObjectType'},
                                                                                               'relationship': 'Connected_To'}]}},
                                                'sightings': {'sightings': [{'timestamp': '2015-05-30T09:09:20',
                                                                             'timestamp_precision': 'second'}],
                                                              'sightings_count': '6'},
                                                'suggested_coas': {'suggested_coas': [{'course_of_action': {'stage': 'Remedy',
                                                                                                            'type': 'Perimeter '
                                                                                                                    'Blocking'}}]},
                                                'version': '2.1.1'},
                                               {'IndicatorType': 'URL-Block',
                                                'description': 'URL Block: Random String',
                                                'handling': [{'controlled_structure': 'ancestor-or-self::stix:Indicator//node()',
                                                              'marking_structures': [{'statement': 'OUO=True, ReconAllowed=False, SharingRestrictions=private',
                                                                                      'xsi:type': 'simpleMarking:SimpleMarkingStructureType'}]}],
                                                'indicator_types': [{'value': 'URL Watchlist',
                                                                     'xsi:type': 'stixVocabs:IndicatorTypeVocab-1.1'}],
                                                'observable': {'keywords': ['Phishing'],
                                                               'object': {'properties': {'type': 'URL',
                                                                                         'value': {'condition': 'Equals',
                                                                                                   'value': 'http://bad.domain.url/?ref=RANDOM_STRING'},
                                                                                         'xsi:type': 'URIObjectType'}},
                                                               'sighting_count': '1'},
                                                'sightings': {'sightings': [{'timestamp': '2015-05-30T09:09:00',
                                                                             'timestamp_precision': 'second'}],
                                                              'sightings_count': '1'},
                                                'suggested_coas': {'suggested_coas': [{'course_of_action': {'stage': 'Remedy',
                                                                                                            'type': 'Monitoring'}}]},
                                                'version': '2.1.1'},
                                               {'IndicatorType': 'DNS-Hostname-Block',
                                                'description': 'Domain Block: malicious',
                                                'handling': [{'controlled_structure': 'ancestor-or-self::stix:Indicator//node()',
                                                              'marking_structures': [{'statement': 'OUO=True, ReconAllowed=False, SharingRestrictions=private',
                                                                                      'xsi:type': 'simpleMarking:SimpleMarkingStructureType'}]}],
                                                'indicator_types': [{'value': 'Domain Watchlist',
                                                                     'xsi:type': 'stixVocabs:IndicatorTypeVocab-1.1'}],
                                                'observable': {'object': {'properties': {'type': 'FQDN',
                                                                                         'value': {'condition': 'Equals',
                                                                                                   'value': 'malicious.domain'},
                                                                                         'xsi:type': 'DomainNameObjectType'}},
                                                               'sighting_count': '255'},
                                                'sightings': {'sightings': [{'timestamp': '2015-05-30T09:06:00',
                                                                             'timestamp_precision': 'second'}],
                                                              'sightings_count': '1'},
                                                'suggested_coas': {'suggested_coas': [{'course_of_action': {'description': 'observe_and_report',
                                                                                                            'stage': 'Remedy',
                                                                                                            'type': 'Monitoring'}}]},
                                                'version': '2.1.1'}]}
        
        
        with self.assertLogs('FlexTransform.SchemaParser', 'INFO') as cm:
            FinalizedData = self.Transform.TransformFile(sourceFileName=sample_cfm13_file, sourceParserName='Cfm13Alert', targetParserName='STIX')
        
        self.assertEqual(cm.output, ["INFO:FlexTransform.SchemaParser:Validation failed for observable_sighting_count, ('DataOutOfRange', 'The value for field observable_sighting_count is outside of the allowed range(1-65535): 0')"])
        
        FinalizedData['DocumentHeaderData'].pop('timestamp')
        self.assertDictEqual(deep_sort(ExpectedDataDict['DocumentHeaderData']),deep_sort(FinalizedData['DocumentHeaderData']))
        
        self.assertEqual(len(ExpectedDataDict['IndicatorData']),len(FinalizedData['IndicatorData']))
        
        for idx, val in enumerate(ExpectedDataDict['IndicatorData']) :
            # The processedTime key changes with each run, so ignore it
            FinalizedData['IndicatorData'][idx].pop('timestamp')
            self.assertDictEqual(deep_sort(val),deep_sort(FinalizedData['IndicatorData'][idx]))


def deep_sort(obj):
    """
    Recursively sort list or dict nested lists
    Based on code from http://stackoverflow.com/questions/18464095/how-to-achieve-assertdictequal-with-assertsequenceequal-applied-to-values
    """

    if isinstance(obj, dict):
        _sorted = {}
        for key in sorted(obj):
            _sorted[key] = deep_sort(obj[key])

    elif isinstance(obj, list):
        new_list = []
        isdict = False
        for val in obj:
            if (not isdict and isinstance(val, dict)) :
                isdict = True
                
            new_list.append(deep_sort(val))
            
        if (isdict) :
            # Sort lists of dictionaries by the hash value of the data in the dictionary
            _sorted = sorted(new_list, key=lambda d: hash(json.dumps(d, ensure_ascii = True, sort_keys = True)))                
        else :
            _sorted = sorted(new_list)

    else:
        _sorted = obj

    return _sorted

if __name__ == "__main__":
    unittest.main()