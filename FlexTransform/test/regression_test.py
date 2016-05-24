import io
import os
import unittest
from lxml import etree

from FlexTransform.test.SampleInputs import STIXTLP
from FlexTransform import FlexTransform

class regression_tests(unittest.TestCase):
    output1 = None
    namespace = {
        'cybox'         : "http://cybox.mitre.org/cybox-2",
        'indicator'     : "http://stix.mitre.org/Indicator-2",
        'marking'       : "http://data-marking.mitre.org/Marking-1",
        'PortObj'       : "http://cybox.mitre.org/objects#PortObject-2",
        'stix'          : "http://stix.mitre.org/stix-1",
        'stixCommon'    : "http://stix.mitre.org/common-1",
        'stixVocabs'    : "http://stix.mitre.org/default_vocabularies-1",
        'xsi'           : "http://www.w3.org/2001/XMLSchema-instance",
        'cyboxVocabs'   : "http://cybox.mitre.org/default_vocabularies-2",
        'AddressObj'    : "http://cybox.mitre.org/objects#AddressObject-2",
        'ArtifactObj'   : "http://cybox.mitre.org/objects#ArtifactObject-2",
        'FileObj'       : "http://cybox.mitre.org/objects#FileObject-2",
        'URIObj'        : "http://cybox.mitre.org/objects#URIObject-2",
        'tlpMarking'    : "http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1",
        'CFM'           : "http://www.anl.gov/cfm/stix",
        'xmlns'         : "http://www.anl.gov/cfm/1.3/IDMEF-Message"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, './TestData/cfm13_multiple_site.cfg'), 'r') as input_file:
            transform.AddParser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.AddParser('stix', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(STIXTLP), 'stix', 'cfm13alert', targetFileName=output1_object)
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)
        print(output1_object.getvalue())

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:Analyzer/@analyzerid", namespaces=self.namespace)[0], "Fake")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:Analyzer/xmlns:Node/xmlns:location/text()", namespaces=self.namespace)[0], "Sand Worm Dave, Arrakeen, Dune 54321")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:Analyzer/xmlns:Node/xmlns:name/text()", namespaces=self.namespace)[0], "Test User, 555-867-5309, test@test.int")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:AdditionalData[@meaning='report schedule']/text()", namespaces=self.namespace)[0], "5 minutes")

    def test_alert_AD_duration(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:AdditionalData[@meaning='duration']/text()", namespaces=self.namespace)), set(['86400']))

    def test_reference_origin(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Reference/@origin", namespaces=self.namespace)), set(['user-specific']))