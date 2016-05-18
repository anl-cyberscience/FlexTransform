import io
import os
import unittest

from FlexTransform.test.SampleInputs import STIXTLP, STIXACS, CFM13ALERT
from FlexTransform import FlexTransform

class TestCFM13AlertToKeyValue(unittest.TestCase):
    output1 = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.AddParser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.AddParser('keyvalue', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(CFM13ALERT), 'cfm13alert', 'keyvalue', targetFileName=output1_object)
        cls.output1 = []
        output1_object.seek(0)
        for line in output1_object.read().splitlines():
            cls.output1.append(line.split('&'))

    def test_duration(self):
        self.assertIn('duration=86400', self.output1[0])

    def test_serviceport(self):
        self.assertIn('service_port=22', self.output1[0])

    def test_category_name(self):
        self.assertIn("category_name='SSH Attack'", self.output1[0])

    def test_category(self):
        self.assertIn("category='Scanning'", self.output1[0])

    def test_severity(self):
        self.assertIn("severity='unknown'", self.output1[0])

    def test_prior_offenses(self):
        self.assertIn('prior_offenses=11', self.output1[0])

    def test_category_description(self):
        self.assertIn("category_description='SSH Attack'", self.output1[0])

    def test_serviceprotocol(self):
        self.assertIn("service_protocol='TCP'", self.output1[0])

    def test_comment(self):
        self.assertIn("comment='No Comment'", self.output1[0])

    def test_confidence(self):
        self.assertIn('confidence=0', self.output1[0])

    def test_direction(self):
        self.assertIn("direction='unknown'", self.output1[0])

    def test_ipv4(self):
        self.assertIn('ipv4=10.10.10.10', self.output1[0])

    def test_combined_comment(self):
        self.assertIn("combined_comment='SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high'", self.output1[0])

class TestSTIXTLPToKeyValue(unittest.TestCase):
    output1 = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.AddParser('stixtlp', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.AddParser('keyvalue', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(STIXTLP), 'stixtlp', 'keyvalue', targetFileName=output1_object)
        cls.output1 = []
        output1_object.seek(0)
        for line in output1_object.read().splitlines():
            cls.output1 += line.split('&')

    def test_category(self):
        self.assertIs(5, self.output1.count("category='Unspecified'"))

    def test_category_name(self):
        self.assertIs(5, self.output1.count("category_name='Unspecified'"))

    def test_severity(self):
        self.assertIs(5, self.output1.count("severity='unknown'"))

    def test_comment(self):
        self.assertIs(5, self.output1.count("comment='No Comment'"))

    def test_confidence(self):
        self.assertIs(5, self.output1.count('confidence=0'))

    def test_direction(self):
        self.assertIs(5, self.output1.count("direction='unknown'"))

    def test_ipv4(self):
        self.assertIn('ipv4=10.10.10.10', self.output1)
        self.assertIn('ipv4=11.11.11.11', self.output1)
        self.assertIn('ipv4=12.12.12.12', self.output1)
        self.assertIn('ipv4=13.13.13.13', self.output1)
        self.assertIn('ipv4=14.14.14.14', self.output1)

    def test_combined_comment(self):
        self.assertIs(5, self.output1.count("combined_comment='CRISP Report Indicator'"))

class TestSTIXACSToKeyValue(unittest.TestCase):
    output1 = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.AddParser('stixacs', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.AddParser('keyvalue', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(STIXACS), 'stixacs', 'keyvalue', targetFileName=output1_object)
        cls.output1 = []
        output1_object.seek(0)
        for line in output1_object.read().splitlines():
            cls.output1 += line.split('&')

    def test_category(self):
        self.assertIs(3, self.output1.count("category='Unspecified'"))

    def test_category_name(self):
        self.assertIs(3, self.output1.count("category_name='Unspecified'"))

    def test_severity(self):
        self.assertIs(3, self.output1.count("severity='unknown'"))

    def test_comment(self):
        self.assertIs(3, self.output1.count("comment='No Comment'"))

    def test_confidence(self):
        self.assertIs(3, self.output1.count('confidence=0'))

    def test_direction(self):
        self.assertIs(3, self.output1.count("direction='unknown'"))

    def test_fqdn(self):
        self.assertIn("fqdn='blog.website.net'", self.output1)
        self.assertIn("fqdn='fake.com'", self.output1)
        self.assertIn("fqdn='goo.gl/peter'", self.output1)

    def test_combined_comment(self):
        self.assertIn("combined_comment='AAA Report Indicator'", self.output1)
        self.assertIn("combined_comment='Domain Indicator'", self.output1)
        self.assertIn("combined_comment='Just Another Indicator'", self.output1)

if __name__ == '__main__':
    unittest.main()