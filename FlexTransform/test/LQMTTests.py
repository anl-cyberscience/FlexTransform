import io
import os
import unittest
from lxml import etree

from FlexTransform.test.SampleInputs import CFM13ALERT2
from FlexTransform import FlexTransform

class TestCFM13AlertToLQMT(unittest.TestCase):
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

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.AddParser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.AddParser('lqmtools', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(CFM13ALERT2), 'cfm13alert', 'lqmtools', targetFileName=output1_object)
        output1_object.seek(0)
        output1_object.readline()
        print(output1_object.getvalue())


    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:Analyzer/@analyzerid", namespaces=self.namespace)[0], "Fake")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:Analyzer/xmlns:Node/xmlns:location/text()", namespaces=self.namespace)[0], "1600 Pennslyvania Ave, Washington DC 20005")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:Analyzer/xmlns:Node/xmlns:name/text()", namespaces=self.namespace)[0], "Nicholas Hendersen, 555-867-5309, nietzsche@doe.gov")

    def test_alert_analyzer_time(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:AnalyzerTime/text()", namespaces=self.namespace)[0], "2016-03-23T16:45:05+0000")

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:AdditionalData[@meaning='number of alerts in this report']/text()", namespaces=self.namespace)[0], "7")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:AdditionalData[@meaning='report schedule']/text()", namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:AdditionalData[@meaning='report type']/text()", namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        self.assertEqual(self.output1.xpath("/xmlns:IDMEF-Message/xmlns:Alert/xmlns:AdditionalData[@meaning='report start time']/text()", namespaces=self.namespace)[0], "2016-03-23T16:45:05+0000")

    def test_source_node_address_ipv4(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Address[@category='ipv4-addr']/xmlns:address/text()", namespaces=self.namespace)), set(["10.10.10.10", "11.11.11.11", "12.12.12.12", "13.13.13.13", "14.14.14.14"]))

    def test_source_node_address_url(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Address[not(@category='ipv4-addr')]/xmlns:address/text()", namespaces=self.namespace)),  set(["fake.site.com/malicious.js", "bad.domain.be/poor/path"]))

    def test_alert_AD_OUO(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:AdditionalData[@meaning='OUO']/text()", namespaces=self.namespace)), set(['0']))

    def test_alert_AD_restriction(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:AdditionalData[@meaning='restriction']/text()", namespaces=self.namespace)),set(['public']))

    def test_alert_AD_duration(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:AdditionalData[@meaning='duration']/text()", namespaces=self.namespace)), set(['0']))

    def test_alert_AD_recon(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:AdditionalData[@meaning='recon']/text()", namespaces=self.namespace)), set(['0']))

    def test_alert_assessment_action(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Action/@category", namespaces=self.namespace)), set(["block-installed"]))

    def test_alert_classification_reference_name(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Reference/xmlns:name/text()", namespaces=self.namespace)), set(["unknown"]))

    def test_alert_classification_reference_url_false(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:url/text()", namespaces=self.namespace)), set([" "]))

if __name__ == '__main__':
    unittest.main()