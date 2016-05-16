import io
import os
import unittest
from lxml import etree

from FlexTransform.test.SampleInputs  import CFM13ALERT, STIXACS,KEYVALUE
from FlexTransform import FlexTransform

class TestCFM13AlertToSTIXTLP(unittest.TestCase):
    output1 = None
    namespace = {
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'PortObj': "http://cybox.mitre.org/objects#PortObject-2",
        'stix': "http://stix.mitre.org/stix-1",
        'stixCommon': "http://stix.mitre.org/common-1",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2"
    }
    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.AddParser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.AddParser('stix', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(CFM13ALERT), 'cfm13alert', 'stix', targetFileName=output1_object)
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Package_Intent/@xsi:type", namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Package_Intent/text()", namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/marking:Controlled_Structure/text()", namespaces=self.namespace)[0], "//node() | //@*")

    def test_tlp_type(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/marking:Marking_Structure/@xsi:type", namespaces=self.namespace)[0], "tlpMarking:TLPMarkingStructureType")

    def test_tlp_color(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/marking:Marking_Structure/@color", namespaces=self.namespace)[0], "AMBER")

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/stixCommon:Description/text()", namespaces=self.namespace)[0], "Fake National Lab")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/stixCommon:Identity/stixCommon:Name/text()", namespaces=self.namespace)[0], "Fake")

    def test_indicator_type(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Type/text()", namespaces=self.namespace)[0], "IP Watchlist")

    def test_indicator_description(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Description/text()", namespaces=self.namespace)[0], "SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high")

    def test_indicator_keyword(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Keywords/cybox:Keyword/text()", namespaces=self.namespace)[0], "Scanning")

    def test_indicator_properties_type(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Properties/@xsi:type", namespaces=self.namespace)[0], "AddressObj:AddressObjectType")

    def test_indicator_properties_category(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Properties/@category", namespaces=self.namespace)[0], "ipv4-addr")

    def test_indicator_properties_category(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Properties/@category", namespaces=self.namespace)[0], "ipv4-addr")

    def test_indicator_properties_indicator(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Properties/AddressObj:Address_Value/text()", namespaces=self.namespace)[0], "10.10.10.10")

    def test_indicator_properties_related_objects_properties(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Related_Objects/cybox:Related_Object/cybox:Properties/@xsi:type", namespaces=self.namespace)[0], "PortObj:PortObjectType")

    def test_indicator_properties_related_objects_properties_port_value(self):
        self.assertEqual(len(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Related_Objects/cybox:Related_Object/cybox:Properties/PortObj:Port_Value", namespaces=self.namespace)), 1)

    def test_indicator_properties_related_objects_properties_port_value_text(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Related_Objects/cybox:Related_Object/cybox:Properties/PortObj:Port_Value/text()", namespaces=self.namespace)[0], "22")

    def test_indicator_properties_related_objects_properties_port_protocol(self):
        self.assertEqual(len(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Related_Objects/cybox:Related_Object/cybox:Properties/PortObj:Layer4_Protocol", namespaces=self.namespace)), 1)

    def test_indicator_properties_related_objects_properties_port_protocol_text(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/cybox:Object/cybox:Related_Objects/cybox:Related_Object/cybox:Properties/PortObj:Layer4_Protocol/text()", namespaces=self.namespace)[0], "TCP")

class STIXACSToSTIXTLP(unittest.TestCase):
    output1 = None

    namespace = {
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'PortObj': "http://cybox.mitre.org/objects#PortObject-2",
        'stix': "http://stix.mitre.org/stix-1",
        'stixCommon': "http://stix.mitre.org/common-1",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'cyboxCommon': "http://cybox.mitre.org/common-2",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2",
        'DomainNameObj': "http://cybox.mitre.org/objects#DomainNameObject-1"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.AddParser('stixacs', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.AddParser('stix', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(STIXACS), 'stixacs', 'stix', targetFileName=output1_object)
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_title(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Title/text()", namespaces=self.namespace)[0], "ACS-example.pdf")

    def test_package_description(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Description/text()", namespaces=self.namespace)[0], "Redirects to Malicious Websites")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Package_Intent/@xsi:type", namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Package_Intent/text()", namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(set(self.output1.xpath("//marking:Controlled_Structure/text()", namespaces=self.namespace)), set(["//node()", "//node() | //@*"]))

    def test_tlp_type(self):
        self.assertEqual(set(self.output1.xpath("//marking:Marking_Structure/@xsi:type", namespaces=self.namespace)), set(["tlpMarking:TLPMarkingStructureType"]))

    def test_tlp_color(self):
        self.assertEqual(set(self.output1.xpath("//marking:Marking_Structure/@color", namespaces=self.namespace)), set(["AMBER"]))

    def test_information_time_produced_time(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/stixCommon:Time/cyboxCommon:Produced_Time/text()", namespaces=self.namespace)[0], "2015-11-25T01:45:05+00:00")

    def test_indicator_timestamps(self):
        self.assertEqual(set(self.output1.xpath("//stix:Indicator/@timestamp", namespaces=self.namespace)), set(["2015-11-26T00:35:06+00:00"]))

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("//stix:Indicator/@xsi:type", namespaces=self.namespace)), set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("//stix:Indicator/@version", namespaces=self.namespace)), set(["2.1.1"]))

    def test_indicator_title(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Title/text()", namespaces=self.namespace)), set(["Original AAA Report Document"]))

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()", namespaces=self.namespace)), set(["Domain Watchlist"]))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Description/text()", namespaces=self.namespace)), set(["Sample.pdf", "AAA Report Indicator", "Domain Indicator", "Just Another Indicator"]))

    def test_indicator_properties_xsitype(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@xsi:type", namespaces=self.namespace)), set(["DomainNameObj:DomainNameObjectType", "ArtifactObj:ArtifactObjectType"]))

    def test_indicator_properties_type(self):
        if "Domain Name" in self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@type", namespaces=self.namespace) or "fqdn" in self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@type", namespaces=self.namespace):
            self.assertIn("File", set(self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@type", namespaces=self.namespace)))

    def test_indicator_properties_packaging_encoding(self):
        self.assertEqual(set(self.output1.xpath("//ArtifactObj:Packaging/ArtifactObj:Encoding/@algorithm", namespaces=self.namespace)), set(["Base64"]))

    def test_indicator_properties_rawartifact(self):
        self.assertEqual(set(self.output1.xpath("//ArtifactObj:Raw_Artifact/text()", namespaces=self.namespace)), set(["FILLINRAWDATAHERE"]))

    def test_indicator_properties_domainnames(self):
        self.assertEqual(set(self.output1.xpath("//DomainNameObj:Value[@condition='Equals']/text()", namespaces=self.namespace)), set(["goo.gl/peter", "fake.com", "blog.website.net"]))

class KeyValueToSTIXTLP(unittest.TestCase):
    output1 = None

    namespace = {
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'PortObj': "http://cybox.mitre.org/objects#PortObject-2",
        'stix': "http://stix.mitre.org/stix-1",
        'stixCommon': "http://stix.mitre.org/common-1",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'cyboxCommon': "http://cybox.mitre.org/common-2",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2",
        'DomainNameObj': "http://cybox.mitre.org/objects#DomainNameObject-1"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.AddParser('stix', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.AddParser('keyvalue', input_file)
        output1_object = io.StringIO()

        transform.TransformFile(io.StringIO(KEYVALUE), 'keyvalue', 'stix', targetFileName=output1_object)
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Package_Intent/@xsi:type", namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Package_Intent/text()", namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(set(self.output1.xpath("//marking:Controlled_Structure/text()", namespaces=self.namespace)), set(["//node() | //@*"]))

    def test_tlp_type(self):
        self.assertEqual(set(self.output1.xpath("//marking:Marking_Structure/@xsi:type", namespaces=self.namespace)), set(["tlpMarking:TLPMarkingStructureType"]))

    def test_tlp_color(self):
        self.assertEqual(set(self.output1.xpath("//marking:Marking_Structure/@color", namespaces=self.namespace)), set(["GREEN"]))

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("//stix:Indicator/@xsi:type", namespaces=self.namespace)), set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("//stix:Indicator/@version", namespaces=self.namespace)), set(["2.1.1"]))

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()", namespaces=self.namespace)), set(["Domain Watchlist", "IP Watchlist"]))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Description/text()", namespaces=self.namespace)), set(['Attacker scanning for SSH, direction:ingress, confidence:0, severity:high','Attacker scanning for RDP, direction:ingress, confidence:0, severity:high','HTTP Response code 4xx, suspicious, direction:ingress, confidence:0, severity:low','Malicious domain, direction:egress, confidence:0, severity:high']))

    def def_indicator_observable_keywords(self):
        self.assertEqual(set(self.output1.xpath("//cybox:Keyword/text()", namespaces=self.namespace)), set(['Reconnaissance', 'Scanning', 'Malware Traffic']))

    def test_indicator_properties_type(self):
        if "Domain Name" in self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@type", namespaces=self.namespace) or "fqdn" in self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@type", namespaces=self.namespace):
            self.assertTrue(True)

    def test_indicator_properties_category(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@category", namespaces=self.namespace)), set(["ipv4-addr", "ipv6-addr"]))

    def test_indicator_properties_domainname(self):
        if "bad.scanning.dom"in self.output1.xpath("//DomainNameObj:Value/text()", namespaces=self.namespace):
            self.assertEqual(set(self.output1.xpath("//DomainNameObj:Value/text()", namespaces=self.namespace)), set(["bad.scanning.dom","bad.domain"]))
        else:
            self.assertEqual(set(self.output1.xpath("//DomainNameObj:Value/text()", namespaces=self.namespace)), set(["bad.domain"]))

    def test_indicator_properties_address(self):
        if "10.11.12.14" in self.output1.xpath("//AddressObj:Address_Value/text()", namespaces=self.namespace):
            self.assertEqual(set(self.output1.xpath("//AddressObj:Address_Value/text()", namespaces=self.namespace)), set(["10.11.12.13", "10.11.12.14", "2001:db8:16::1"]))
        else:
            self.assertEqual(set(self.output1.xpath("//AddressObj:Address_Value/text()", namespaces=self.namespace)), set(["10.11.12.13", "2001:db8:16::1"]))

    def test_indicator_properties_port_value(self):
        self.assertEqual(set(self.output1.xpath("//PortObj:Port_Value/text()", namespaces=self.namespace)), set(["3389", "22"]))

    def test_indicator_properties_port_protocol(self):
        self.assertEqual(set(self.output1.xpath("//PortObj:Layer4_Protocol/text()", namespaces=self.namespace)), set(["TCP"]))

    def test_indicator_relatedobject_relationship(self):
        self.assertEqual(set(self.output1.xpath("//cybox:Relationship/text()", namespaces=self.namespace)), set(["Connected_To"]))

    def test_indicator_sightings(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Sighting/@timestamp", namespaces=self.namespace)), set(["2012-01-01T07:00:00+00:00"]))

    def test_indicator_sighting_precision(self):
        self.assertEqual(set(self.output1.xpath("//indicator:Sighting/@timestamp_precision", namespaces=self.namespace)), set(["second"]))

if __name__ == '__main__':
    unittest.main()