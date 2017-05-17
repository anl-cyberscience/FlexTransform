import io
import os
import unittest
from lxml import etree

from FlexTransform.test.SampleInputs import STIXTLP, STIXACS, KEYVALUE
from FlexTransform import FlexTransform


class TestSTIXTLPToCFM13Alert(unittest.TestCase):
    output1 = None
    alert = "/xmlns:IDMEF-Message/xmlns:Alert/"
    additional = "%s xmlns:AdditionalData" % alert
    address = "%s xmlns:Source/xmlns:Node/xmlns:Address" % alert
    classification = "%s xmlns:Classification" % alert

    namespace = {
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'PortObj': "http://cybox.mitre.org/objects#PortObject-2",
        'stix': "http://stix.mitre.org/stix-1",
        'stixCommon': "http://stix.mitre.org/common-1",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'cyboxVocabs': "http://cybox.mitre.org/default_vocabularies-2",
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2",
        'FileObj': "http://cybox.mitre.org/objects#FileObject-2",
        'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
        'tlpMarking': "http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1",
        'CFM': "http://www.anl.gov/cfm/stix",
        'xmlns': "http://www.anl.gov/cfm/1.3/IDMEF-Message"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.add_parser('stixtlp', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        output1_object = io.StringIO()

        transform.transform(io.StringIO(STIXTLP), 'stixtlp', 'cfm13alert', target_file=output1_object)
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/@analyzerid" % self.alert,
                                            namespaces=self.namespace)[0], "Fake")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/xmlns:Node/xmlns:location/text()" % self.alert,
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/xmlns:Node/xmlns:name/text()" % self.alert,
                                            namespaces=self.namespace)[0], "Test User, 555-555-1212, test@test.int")

    def test_alert_analyzer_time(self):
        self.assertEqual(self.output1.xpath("%s xmlns:AnalyzerTime/text()" % self.alert,
                                            namespaces=self.namespace)[0], "2016-03-23T16:45:05+0400")

    def test_alert_create_time(self):
        self.assertEqual(self.output1.xpath("%s xmlns:CreateTime/text()" % self.alert,
                                            namespaces=self.namespace)[0], "2016-03-23T16:45:05+0400")

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='number of alerts in this report']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "7")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report schedule']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report type']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report start time']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "2016-03-23T16:45:05+0400")

    def test_alert_address_category(self):
        self.assertEqual(self.output1.xpath("%s /@category" % self.address,
                                            namespaces=self.namespace)[0], "ipv4-addr")

    def test_source_node_address_ipv4(self):
        self.assertEqual(set(self.output1.xpath("%s [@category='ipv4-addr']/xmlns:address/text()" % self.address,
                                                namespaces=self.namespace)),
                         set(["10.10.10.10", "11.11.11.11", "12.12.12.12", "13.13.13.13", "14.14.14.14"]))

    def test_alert_classification(self):
        self.assertEqual(set(self.output1.xpath("%s /@text" % self.classification, namespaces=self.namespace)),
                         set(["CRISP Report Indicator", "URL Block: CRISP Report Indicator"]))

    def test_alert_reference_meaning(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/@meaning" % self.classification,
                                                namespaces=self.namespace)), set(["Unspecified"]))

    def test_alert_reference_origin(self):
        self.assertEqual(set(self.output1.xpath("%s xmlns:Classification/xmlns:Reference/@origin" % self.alert,
                                                namespaces=self.namespace)), set(["unknown"]))

    def test_source_node_address_url(self):
        self.assertEqual(set(self.output1.xpath("%s [not(@category='ipv4-addr')]/xmlns:address/text()" % self.address,
                                                namespaces=self.namespace)),
                         set(["fake.site.com/malicious.js", "bad.domain.be/poor/path"]))

    def test_alert_AD_OUO(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='OUO']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_AD_restriction(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='restriction']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['public']))

    def test_alert_AD_duration(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='duration']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_AD_recon(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='recon']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_assessment_action(self):
        self.assertEqual(set(self.output1.xpath("%s xmlns:Assessment/xmlns:Action/@category" % self.alert,
                                                namespaces=self.namespace)), set(["block-installed"]))

    def test_alert_classification_reference_name(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/xmlns:name/text()" % self.classification,
                                                namespaces=self.namespace)), set(["unknown"]))

    def test_alert_classification_reference_url_false(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/xmlns:url/text()" % self.classification,
                                                namespaces=self.namespace)), set([" "]))


class TestSTIXACSToCFM13Alert(unittest.TestCase):
    output1 = None
    alert = "/xmlns:IDMEF-Message/xmlns:Alert/"
    additional = "%s xmlns:AdditionalData" % alert
    address = "%s xmlns:Source/xmlns:Node/xmlns:Address" % alert
    classification = "%s xmlns:Classification" % alert

    namespace = {
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'PortObj': "http://cybox.mitre.org/objects#PortObject-2",
        'stix': "http://stix.mitre.org/stix-1",
        'stixCommon': "http://stix.mitre.org/common-1",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'cyboxVocabs': "http://cybox.mitre.org/default_vocabularies-2",
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2",
        'FileObj': "http://cybox.mitre.org/objects#FileObject-2",
        'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
        'tlpMarking': "http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1",
        'CFM': "http://www.anl.gov/cfm/stix",
        'xmlns': "http://www.anl.gov/cfm/1.3/IDMEF-Message"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        output1_object = io.StringIO()

        transform.transform(io.StringIO(STIXACS), 'stixacs', 'cfm13alert', target_file=output1_object)
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/@analyzerid" % self.alert,
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/xmlns:Node/xmlns:location/text()" % self.alert,
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/xmlns:Node/xmlns:name/text()" % self.alert,
                                            namespaces=self.namespace)[0], "Test User, 555-555-1212, test@test.int")

    def test_alert_analyzer_time(self):
        self.assertEqual(self.output1.xpath("%s xmlns:AnalyzerTime/text()" % self.alert,
                                            namespaces=self.namespace)[0], "2015-11-25T01:45:05+0000")

    def test_alert_create_time(self):
        self.assertEqual(self.output1.xpath("%s xmlns:CreateTime/text()" % self.alert,
                                            namespaces=self.namespace)[0], "2015-11-25T01:45:05+0000")

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='number of alerts in this report']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "3")

    def test_alert_AD_report_ouo(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report ouo']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "0")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report schedule']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report type']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report start time']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "2015-11-25T01:45:05+0000")

    def test_source_node_name_dns(self):
        self.assertEqual(set(self.output1.xpath("%s xmlns:Source/xmlns:Node[@category='dns']/xmlns:name/text()" % self.alert,
                                                namespaces=self.namespace)),
                         set(["blog.website.net", "fake.com", "goo.gl/peter"]))

    def test_alert_classification(self):
        self.assertEqual(set(self.output1.xpath("%s /@text" % self.classification, namespaces=self.namespace)),
                         set(["Domain Block: AAA Report Indicator",
                              "Domain Block: Just Another Indicator",
                              "Domain Block: Domain Indicator"]))

    def test_alert_reference_meaning(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/@meaning" % self.classification,
                                                namespaces=self.namespace)), set(["Unspecified"]))

    def test_alert_reference_origin(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/@origin" % self.classification,
                                                namespaces=self.namespace)), set(["unknown"]))

    def test_alert_AD_OUO(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='OUO']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_AD_restriction(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='restriction']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['public']))

    def test_alert_AD_duration(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='duration']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_AD_recon(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='recon']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_assessment_action(self):
        self.assertEqual(set(self.output1.xpath("%s xmlns:Assessment/xmlns:Action/@category" % self.alert,
                                                namespaces=self.namespace)), set(["block-installed"]))

    def test_alert_classification_text(self):
        self.assertEqual(set(self.output1.xpath("%s /@text" % self.classification, namespaces=self.namespace)),
                         set(["Domain Block: AAA Report Indicator",
                              "Domain Block: Domain Indicator",
                              "Domain Block: Just Another Indicator"]))

    def test_alert_classification_reference_meaning(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/@meaning" % self.classification,
                                                namespaces=self.namespace)), set(["Unspecified"]))

    def test_alert_classification_reference_origin(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/@origin" % self.classification,
                                                namespaces=self.namespace)), set(["unknown"]))

    def test_alert_classification_reference_name(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/xmlns:name/text()" % self.classification,
                                                namespaces=self.namespace)), set(["unknown"]))

    def test_alert_classification_reference_url_false(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/xmlns:url/text()" % self.classification,
                                                namespaces=self.namespace)), set([" "]))


class TestKeyValueToCFM13Alert(unittest.TestCase):
    output1 = None
    alert = "/xmlns:IDMEF-Message/xmlns:Alert/"
    additional = "%s xmlns:AdditionalData" % alert
    address = "%s xmlns:Source/xmlns:Node/xmlns:Address" % alert
    classification = "%s xmlns:Classification" % alert
    service = "%s xmlns:Target/xmlns:Service" % alert
    node = "%s xmlns:Source/xmlns:Node" % alert

    namespace = {
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'PortObj': "http://cybox.mitre.org/objects#PortObject-2",
        'stix': "http://stix.mitre.org/stix-1",
        'stixCommon': "http://stix.mitre.org/common-1",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'cyboxVocabs': "http://cybox.mitre.org/default_vocabularies-2",
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2",
        'FileObj': "http://cybox.mitre.org/objects#FileObject-2",
        'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
        'tlpMarking': "http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1",
        'CFM': "http://www.anl.gov/cfm/stix",
        'xmlns': "http://www.anl.gov/cfm/1.3/IDMEF-Message"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.add_parser('keyvalue', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        output1_object = io.StringIO()

        transform.transform(io.StringIO(KEYVALUE), 'keyvalue', 'cfm13alert', target_file=output1_object)
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/@analyzerid" % self.alert,
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/xmlns:Node/xmlns:location/text()" % self.alert,
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("%s xmlns:Analyzer/xmlns:Node/xmlns:name/text()" % self.alert,
                                            namespaces=self.namespace)[0], "Test User, 555-555-1212, test@test.int")

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='number of alerts in this report']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "3")

    def test_alert_AD_report_ouo(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report ouo']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "0")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report schedule']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report type']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        self.assertEqual(self.output1.xpath("%s [@meaning='report start time']/text()" % self.additional,
                                            namespaces=self.namespace)[0], "2012-01-01T07:00:00+00:00")

    def test_alert_create_time(self):
        self.assertEqual(set(self.output1.xpath("%s xmlns:CreateTime/text()" % self.alert,
                                                namespaces=self.namespace)), set(["2012-01-01T07:00:00+00:00"]))

    def test_source_node_address_ipv4(self):
        self.assertEqual(set(self.output1.xpath("%s [@category='ipv4-addr']/xmlns:address/text()" % self.address,
                                                namespaces=self.namespace)), set(["10.11.12.13", "10.11.12.14"]))

    def test_target_port(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:port/text()" % self.service,
                                                namespaces=self.namespace)), set(["3389", "22"]))

    def test_target_protocol(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:protocol/text()" % self.service,
                                                namespaces=self.namespace)), set(["TCP"]))

    def test_source_node_name_dns(self):
        if "bad.scanning.dom" in self.output1.xpath("%s [@category='dns']/xmlns:name/text()" % self.node,
                                                    namespaces=self.namespace):
            self.assertEqual(set(self.output1.xpath("%s [@category='dns']/xmlns:name/text()" % self.node,
                                                    namespaces=self.namespace)), set(["bad.scanning.dom","bad.domain"]))
        else:
            self.assertEqual(set(self.output1.xpath("%s [@category='dns']/xmlns:name/text()" % self.node,
                                                    namespaces=self.namespace)), set(["bad.domain"]))

    def test_alert_AD_OUO(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='OUO']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_AD_restriction(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='restriction']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['public']))

    def test_alert_AD_duration(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='duration']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_AD_recon(self):
        self.assertEqual(set(self.output1.xpath("%s [@meaning='recon']/text()" % self.additional,
                                                namespaces=self.namespace)), set(['0']))

    def test_alert_assessment_action(self):
        self.assertEqual(set(self.output1.xpath("%s xmlns:Assessment/xmlns:Action/@category" % self.alert,
                                                namespaces=self.namespace)), set(["block-installed"]))

    def test_alert_classification(self):
        self.assertEqual(set(self.output1.xpath("%s /@text" % self.classification, namespaces=self.namespace)),
                         set(["Attacker scanning for RDP, direction:ingress, confidence:0, severity:high",
                              "Domain Block: Malicious domain, direction:egress, confidence:0, severity:high",
                              "Attacker scanning for SSH, direction:ingress, confidence:0, severity:high"]))

    def test_alert_classification_reference_meaning(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/@meaning" % self.classification,
                                                namespaces=self.namespace)), set(["Scanning", "Malware Traffic"]))

    def test_alert_classification_reference_origin(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/@origin" % self.classification,
                                                namespaces=self.namespace)), set(["unknown"]))

    def test_alert_classification_reference_name(self):
        if "Scanning" in self.output1.xpath("%s /xmlns:Reference/xmlns:name/text()" % self.classification,
                                            namespaces=self.namespace):
            self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/xmlns:name/text()" % self.classification,
                                                    namespaces=self.namespace)), set(["Scanning", "Malware Traffic"]))
        else:
            self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/xmlns:name/text()" % self.classification,
                                                    namespaces=self.namespace)), set(["Malware Traffic"]))

    def test_alert_classification_reference_url_false(self):
        self.assertEqual(set(self.output1.xpath("%s /xmlns:Reference/xmlns:url/text()" % self.classification,
                                                namespaces=self.namespace)), set([" "]))

if __name__ == '__main__':
    unittest.main()