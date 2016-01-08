'''
Created on Jun 1, 2015

@author: ahoying
'''
import unittest
import os

import logging

from FlexTransform import FlexTransform
from .TestData import KeyValueData
from .utils import deep_sort

class KeyValueTests(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s', level=logging.DEBUG)
        
        self.Transform = FlexTransform.FlexTransform()  # @UndefinedVariable
        
        currentdir = os.path.dirname(__file__)
        Cfm13AlertConfig = open(os.path.join(currentdir,'../resources/sampleConfigurations/cfm13.cfg'), 'r')
        self.Transform.AddParser('Cfm13Alert', Cfm13AlertConfig)
        
        KeyValueConfig = open(os.path.join(currentdir,'../resources/sampleConfigurations/keyvalue_mbl.cfg'), 'r')
        self.Transform.AddParser('KeyValue', KeyValueConfig)
        
        self.KeyValueData = KeyValueData()

    def test_kv_to_cfm13(self):
        sample_kv_file = self.KeyValueData.getFile()
        
        ExpectedDataDict = {'DocumentHeaderData': {'AdditionalData': {'number of alerts in this report': '3',
                                                                       'report schedule': 'NoValue',
                                                                       'report start time': '2012-01-01T07:00:00+0000',
                                                                       'report type': 'alerts'},
                                                    'Analyzer': {'@analyzerid': 'TEST',
                                                                 'Node': {'location': 'TEST',
                                                                          'name': 'Test User, 555-555-1212, test@test.int'}}},
                             'IndicatorData': [{'AdditionalData': {'OUO': '0',
                                                                   'duration': '0',
                                                                   'recon': '0',
                                                                   'restriction': 'public'},
                                                'Assessment': {'Action': {'@category': 'block-installed'}},
                                                'Classification': {'@text': 'Malicious domain, direction:egress, confidence:0, severity:high',
                                                                   'Reference': {'@meaning': 'Malware Traffic',
                                                                                 '@origin': 'unknown',
                                                                                 'name': 'Malware Traffic',
                                                                                 'url': ' '}},
                                                'CreateTime': '2012-01-01T07:00:00+0000',
                                                'IndicatorType': 'DNS-Hostname-Block',
                                                'Source': {'Node': {'@category': 'dns',
                                                                    'name': 'bad.domain'}}},
                                               {'AdditionalData': {'OUO': '0',
                                                                   'duration': '0',
                                                                   'recon': '0',
                                                                   'restriction': 'public'},
                                                'Assessment': {'Action': {'@category': 'block-installed'}},
                                                'Classification': {'@text': 'Attacker scanning for RDP, direction:ingress, confidence:0, severity:high',
                                                                   'Reference': {'@meaning': 'Scanning',
                                                                                 '@origin': 'unknown',
                                                                                 'name': 'Scanning',
                                                                                 'url': ' '}},
                                                'CreateTime': '2012-01-01T07:00:00+0000',
                                                'IndicatorType': 'IPv4-Address-Block',
                                                'Source': {'Node': {'Address': {'@category': 'ipv4-addr',
                                                                                'address': '10.11.12.13'}}},
                                                'Target': {'Service': {'port': '3389',
                                                                       'protocol': 'TCP'}}},
                                               {'AdditionalData': {'OUO': '0',
                                                                   'duration': '0',
                                                                   'recon': '0',
                                                                   'restriction': 'public'},
                                                'Assessment': {'Action': {'@category': 'block-installed'}},
                                                'Classification': {'@text': 'Attacker scanning for SSH, direction:ingress, confidence:0, severity:high',
                                                                   'Reference': {'@meaning': 'Scanning',
                                                                                 '@origin': 'unknown',
                                                                                 'name': 'Scanning',
                                                                                 'url': ' '}},
                                                'CreateTime': '2012-01-01T07:00:00+0000',
                                                'IndicatorType': 'IPv4-Address-Block',
                                                'Source': {'Node': {'@category': 'dns',
                                                                    'Address': {'@category': 'ipv4-addr',
                                                                                'address': '10.11.12.14'},
                                                                    'name': 'bad.scanning.dom'}},
                                                'Target': {'Service': {'port': '22', 'protocol': 'TCP'}}}]}

        
        with self.assertLogs('FlexTransform.SchemaParser', 'INFO') as cm:
            FinalizedData = self.Transform.TransformFile(sourceFileName=sample_kv_file, sourceParserName='KeyValue', targetParserName='Cfm13Alert')
            
        self.assertEqual(cm.output, ["ERROR:FlexTransform.SchemaParser:('UnknownIndicatorType', 'The Indicator Type IPv6-Address-Block is not known by the target schema')"])
        
        FinalizedData['DocumentHeaderData'].pop('AnalyzerTime')
        self.assertDictEqual(deep_sort(ExpectedDataDict['DocumentHeaderData']),deep_sort(FinalizedData['DocumentHeaderData']))
        
        for idx, val in enumerate(ExpectedDataDict['IndicatorData']) :
            self.assertDictEqual(deep_sort(val),deep_sort(FinalizedData['IndicatorData'][idx]))

if __name__ == "__main__":
    unittest.main()