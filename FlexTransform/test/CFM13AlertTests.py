import io
import os
import unittest
from lxml import etree

from FlexTransform.test.SampleInputs  import CFM13ALERT
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
        'xsi': "http://www.w3.org/2001/XMLSchema-instance"
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

if __name__ == '__main__':
    unittest.main()