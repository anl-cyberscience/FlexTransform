'''
Created on Aug 25, 2015

@author: ahoying
'''
import unittest
import os
import io

import logging
# import json

from FlexTransform import FlexTransform
from .TestData import CFM13Data

class InlineSchemaTests(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s', level=logging.DEBUG)
        self.Transform = FlexTransform.FlexTransform()  # @UndefinedVariable
        
        currentdir = os.path.dirname(__file__)
        
        Cfm13AlertConfig = open(os.path.join(currentdir,'../resources/sampleConfigurations/cfm13.cfg'), 'r')
        self.Transform.AddParser('Cfm13Alert', Cfm13AlertConfig)
        
        StixConfig = open(os.path.join(currentdir,'../resources/sampleConfigurations/stix_cfm.cfg'), 'r')
        self.Transform.AddParser('STIX', StixConfig)
        
        InlineConfig = open(os.path.join(currentdir,'./InlineSchemaTest.cfg'), 'r')
        self.Transform.AddParser('InlineSchema', InlineConfig)
        
        self.CFM13Data = CFM13Data()

    def test_inline_schema(self):
        sample_cfm13_file = self.CFM13Data.getFile()
        target_csv_file = io.StringIO()
        
        ExpectedData = "Block 192.168.123.231 1432998645 2592000 N/A Federated 1 TEST  noSensitivity 1 private\r\n" + \
                       "Block 172.20.40.120 1432998645 36000 N/A Federated 1 TEST Scanning noSensitivity 1 private\r\n" + \
                       "Block 172.17.17.172 1432998645 86400 N/A Federated 0 TEST Scanning noSensitivity 1 public\r\n"
        
        with self.assertLogs('FlexTransform.SchemaParser', 'ERROR') as cm:
            FinalizedData = self.Transform.TransformFile(sourceFileName=sample_cfm13_file, targetFileName=target_csv_file, sourceParserName='Cfm13Alert', targetParserName='InlineSchema')  # @UnusedVariable
            
        self.assertEqual(cm.output, ["ERROR:FlexTransform.SchemaParser:('UnknownIndicatorType', 'The Indicator Type URL-Block is not known by the target schema')", "ERROR:FlexTransform.SchemaParser:('UnknownIndicatorType', 'The Indicator Type DNS-Hostname-Block is not known by the target schema')"])
        
        contents = target_csv_file.getvalue()
        self.assertEqual(contents,ExpectedData)


if __name__ == "__main__":
    unittest.main()