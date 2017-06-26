import io
import os
import unittest
import arrow
import json
from lxml import etree

from FlexTransform.test.SampleInputs import STIXTLP, STIXACS, KEYVALUE, IIDCOMBINEDRECENT, IIDACTIVEBADHOST, IIDDYNAMICBADHOST, IIDBADIPV4
from FlexTransform import FlexTransform
from FlexTransform.test.utils import dynamic_time_change


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

class TestIIDCombinedRecentToCFM13Alert(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    alert = "/xmlns:IDMEF-Message/xmlns:Alert/"
    additional = "{} xmlns:AdditionalData".format(alert)
    address = "{} xmlns:Source/xmlns:Node/xmlns:Address".format(alert)
    classification = "{} xmlns:Classification".format(alert)
    service = "{} xmlns:Target/xmlns:Service".format(alert)
    node = "{} xmlns:Source/xmlns:Node".format(alert)

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

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_combined_recent.cfg'), 'r') as input_file:
            transform.add_parser('iid_combined_recent', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        transform.transform(io.StringIO(IIDCOMBINEDRECENT), 'iid_combined_recent', 'cfm13alert', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/@analyzerid".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:location/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:name/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "Test User, 555-555-1212, test@test.int")

    def test_alert_analyzer_time(self):
        test = self.output1.xpath("{} xmlns:AnalyzerTime/text()".format(self.alert), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_alert_create_time(self):
        self.assertEqual(self.output1.xpath("{} xmlns:CreateTime/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "2017-05-11T20:00:39+00:00")

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='number of alerts in this report']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "13")

    def test_alert_AD_report_ouo(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report ouo']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "0")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report schedule']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report type']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report start time']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "2017-05-11T19:55:39+00:00")

    def test_alert_address_category(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:Source//xmlns:Node//xmlns:Address//xmlns:address/text()",
                                            namespaces=self.namespace)),
                         set(["http://79.96.154.154/Porigin/imgs/c/absaa/index.htm", "http://distri7.com/libraries/mill/centurylink/index.php",
                            "http://distri7.com/libraries/mill/centurylink/login.html", "http://www.indonesianwonderagate.com/zee/validate.htm",
                            "http://indonesianwonderagate.com/zee/validate.htm?utm_campaign=tr.im/1e0rQ&utm_content=direct_input&utm_medium=no_referer&utm_source=tr.im",
                            "http://www.applesupport.2fh.me/?ID=login&Key=920134ac4988da998ba1a66123463b58&login&path=/signin/?referrer",
                            "http://primavista-solusi.com/css/.https-www3/sellercentral.amazon.com/ap/signin/cafb30ac87e9c152b70349406227a9bc/auth.php?l=InboxLightaspxn._10&ProductID=DD9E53-&fid=KIBBLDI591KIBBLDI725&fav=1BF807E6036718-UserID&userid=&InboxLight.aspx?n=KIBBLDI591KIBBLDI725&Key=31c5c3553bd4565deab9f760f283b3d6",
                            "http://distri7.com/libraries/mill/centurylink/index.php", "http://omstraders.com/system/storage/logs/wp/",
                            "http://td6hb.net/gdocs/box/box/GoogleDrive-verfications/yahoo.html", "http://ihtjo.ga/3a///yh/en/index.php",
                            "http://ivanasr.com/wp-admin/91042/28fde9335169c98810ca8dcfaaaf840b/", "http://indonesianwonderagate.com/zee/validate.htm?utm_source=tr.im&utm_medium=www.tr.im&utm_campaign=tr.im%252F1e0rQ&utm_content=link_click",
                            "http://mail.applesupport.2fh.me/?ID=login&Key=1f104cbd258114b9790b1618d88560b2&login&path=/signin/?referrer"]))

    def test_alert_classification(self):
        self.assertEqual(set(self.output1.xpath("{} /@text".format(self.classification), namespaces=self.namespace)),
                         set(["URL Block: Phishing, ABSA BANK", "URL Block: Phishing, CENTURYLINK", "URL Block: Phishing, APPLE ID",
                              "URL Block: Phishing, YAHOO.COM", "URL Block: Phishing, AMAZON", "URL Block: Phishing, SUNTRUST"]))

    def test_duration_time(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:AdditionalData[@meaning='duration']/text()", namespaces=self.namespace)),
                         set(["0"]))


class TestIIDActiveBadHostToCFM13Alert(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    alert = "/xmlns:IDMEF-Message/xmlns:Alert/"
    additional = "{} xmlns:AdditionalData".format(alert)
    address = "{} xmlns:Source/xmlns:Node/xmlns:Address".format(alert)
    classification = "{} xmlns:Classification".format(alert)
    service = "{} xmlns:Target/xmlns:Service".format(alert)
    node = "{} xmlns:Source/xmlns:Node".format(alert)

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

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_host_active.cfg'), 'r') as input_file:
            transform.add_parser('iid_host_active', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        transform.transform(io.StringIO(IIDACTIVEBADHOST), 'iid_host_active', 'cfm13alert', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/@analyzerid".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:location/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:name/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "Test User, 555-555-1212, test@test.int")

    def test_alert_analyzer_time(self):
        test = self.output1.xpath("{} xmlns:AnalyzerTime/text()".format(self.alert), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_alert_create_time(self):
        self.assertEqual(self.output1.xpath("{} xmlns:CreateTime/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "2014-05-19T21:12:12+00:00")

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='number of alerts in this report']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "8")

    def test_alert_AD_report_ouo(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report ouo']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "0")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report schedule']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report type']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report start time']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "2014-01-22T14:49:40+00:00")

    def test_alert_address_category(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:Source//xmlns:Node[@category='dns']//xmlns:name/text()",
                                            namespaces=self.namespace)),
                         set(["007panel.no-ip.biz", "00aa8i2wmwym.upaskitv1.org", "00black00.is-with-theband.com",
                              "00c731dah9of.sentencemc.uni.me", "00dcc4f3azhuei.judiciaryfair.uni.me", "00.e04.d502008.aeaf6fb.f7b.f8.34c48.b90.xwnfgthbe.onesplacing.pw",
                              "00hnumc.wsysinfonet.su", "00j.no-ip.info"]))

    def test_alert_classification(self):
        self.assertEqual(set(self.output1.xpath("{} /@text".format(self.classification), namespaces=self.namespace)),
                         set(["Domain Block: Malware_C2, Backdoor_RAT", "Domain Block: Exploit_Kit, Exploit_Kit",
                              "Domain Block: Exploit_Kit, Magnitude"]))

    def test_duration_time(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:AdditionalData[@meaning='duration']/text()", namespaces=self.namespace)),
                         set(["0"]))


class TestIIDDynamicBadHostToCFM13Alert(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    alert = "/xmlns:IDMEF-Message/xmlns:Alert/"
    additional = "{} xmlns:AdditionalData".format(alert)
    address = "{} xmlns:Source/xmlns:Node/xmlns:Address".format(alert)
    classification = "{} xmlns:Classification".format(alert)
    service = "{} xmlns:Target/xmlns:Service".format(alert)
    node = "{} xmlns:Source/xmlns:Node".format(alert)

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

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_host_dynamic.cfg'), 'r') as input_file:
            transform.add_parser('iid_host_dynamic', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        output1_object = io.StringIO()

        new_IIDDYNAMICBADHOST = dynamic_time_change(IIDDYNAMICBADHOST)
        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        transform.transform(io.StringIO(new_IIDDYNAMICBADHOST), 'iid_host_dynamic', 'cfm13alert', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/@analyzerid".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:location/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:name/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "Test User, 555-555-1212, test@test.int")

    def test_alert_analyzer_time(self):
        test = self.output1.xpath("{} xmlns:AnalyzerTime/text()".format(self.alert), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_alert_create_time(self):
        test =self.output1.xpath("{} xmlns:CreateTime/text()".format(self.alert), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='number of alerts in this report']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "12")

    def test_alert_AD_report_ouo(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report ouo']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "0")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report schedule']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report type']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        test = self.output1.xpath("{} [@meaning='report start time']/text()".format(self.additional), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_alert_address_category(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:Source//xmlns:Node[@category='dns']//xmlns:name/text()",
                                            namespaces=self.namespace)),
                         set(["1001k04xl19cylqw6nr194ei4b.net", "1001nsa1dxw3sxwrfqee1t7xddm.biz", "10024iajyfsh65e6axy12bsh7l.org",
                              "1002cxm19ukeqp1l29lxosdfsig.net", "1003xa01nbjxku1tilmja1lob2ee.net", "1004b2a155bhg3lieod8ea14rm.com",
                              "clsg.mu", "clshftfs.org", "clshoc.mn", "clshpwgywbimuok.ru", "clsisxplrhiqycklx.su", "clsitmhauaqfwmvk.org"]))

    def test_alert_classification(self):
        self.assertEqual(set(self.output1.xpath("{} /@text".format(self.classification), namespaces=self.namespace)),
                         set(["Domain Block: MalwareC2DGA, MalwareC2DGA_CryptoLocker", "Domain Block: MalwareC2DGA, MalwareC2DGA_Ranbyus",
                              "Domain Block: MalwareC2DGA, MalwareC2DGA_GameoverZeus", "Domain Block: MalwareC2DGA, MalwareC2DGA_Qakbot",
                              "Domain Block: MalwareC2DGA, ConfickerC", "Domain Block: MalwareC2DGA, ConfickerA"]))

    def test_duration_time(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:AdditionalData[@meaning='duration']/text()", namespaces=self.namespace)),
                         set(["3600", "345600", "0"]))


class TestIIDBadIPV4ToCFM13Alert(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    alert = "/xmlns:IDMEF-Message/xmlns:Alert/"
    additional = "{} xmlns:AdditionalData".format(alert)
    address = "{} xmlns:Source/xmlns:Node/xmlns:Address".format(alert)
    classification = "{} xmlns:Classification".format(alert)
    service = "{} xmlns:Target/xmlns:Service".format(alert)
    node = "{} xmlns:Source/xmlns:Node".format(alert)

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

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_ipv4_recent.cfg'), 'r') as input_file:
            transform.add_parser('iid_ipv4_recent', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        transform.transform(io.StringIO(IIDBADIPV4), 'iid_ipv4_recent', 'cfm13alert', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZ")
        output1_object.seek(0)
        output1_object.readline()
        cls.output1 = etree.parse(output1_object)

    def test_alert_analyzerid(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/@analyzerid".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_location(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:location/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "TEST")

    def test_alert_analyzer_node_name(self):
        self.assertEqual(self.output1.xpath("{} xmlns:Analyzer/xmlns:Node/xmlns:name/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "Test User, 555-555-1212, test@test.int")

    def test_alert_analyzer_time(self):
        test = self.output1.xpath("{} xmlns:AnalyzerTime/text()".format(self.alert), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_alert_create_time(self):
        self.assertEqual(self.output1.xpath("{} xmlns:CreateTime/text()".format(self.alert),
                                            namespaces=self.namespace)[0], "2017-05-11T20:00:02+00:00")

    def test_alert_AD_number_alerts(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='number of alerts in this report']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "6")

    def test_alert_AD_report_ouo(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report ouo']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "0")

    def test_alert_AD_report_schedule(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report schedule']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "NoValue")

    def test_alert_AD_report_type(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report type']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "alerts")

    def test_alert_AD_start_time(self):
        self.assertEqual(self.output1.xpath("{} [@meaning='report start time']/text()".format(self.additional),
                                            namespaces=self.namespace)[0], "2017-05-11T20:00:00+00:00")

    def test_alert_address_category(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:Source//xmlns:Node//xmlns:Address//xmlns:address/text()",
                                            namespaces=self.namespace)),
                         set(["101.203.174.209", "103.11.103.105", "103.12.196.177", "103.13.28.73", "103.16.115.18", "103.17.131.150"]))

    def test_alert_classification(self):
        self.assertEqual(set(self.output1.xpath("{} /@text".format(self.classification), namespaces=self.namespace)),
                         set(["Spam_Bot, Bot Cutwail", "Spam_Bot, Bot Kelihos"]))

    def test_duration_time(self):
        self.assertEqual(set(self.output1.xpath("//xmlns:Alert//xmlns:AdditionalData[@meaning='duration']/text()", namespaces=self.namespace)),
                         set(["0"]))

if __name__ == '__main__':
    unittest.main()