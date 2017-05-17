import io
import os
import unittest
import tempfile
import arrow

from lxml import etree

from FlexTransform import FlexTransform
from FlexTransform.test.SampleInputs import CFM13ALERT, STIXACS, KEYVALUE, CFM13ALERTUUID, CRISP


class TestCFM13AlertToSTIXTLP(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None

    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    sightings = "%s indicator:Sightings/" % indicator
    observable = "%s indicator:Observable/" % indicator
    object = "%s cybox:Object/" % observable
    properties = "%s cybox:Properties/" % object
    related_obj = "%s cybox:Related_Objects/cybox:Related_Object/" % object
    coa = "%s indicator:Suggested_COAs/indicator:Suggested_COA/stixCommon:Course_Of_Action/" % indicator

    namespace = {
        'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'PortObj': "http://cybox.mitre.org/objects#PortObject-2",
        'stix': "http://stix.mitre.org/stix-1",
        'stixCommon': "http://stix.mitre.org/common-1",
        'cyboxCommon': "http://cybox.mitre.org/common-2",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'coa': "http://stix.mitre.org/CourseOfAction-1",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.add_parser('stix', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(CFM13ALERT), 'cfm13alert', 'stix', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace)[0], "//node() | //@*")

    def test_tlp_type(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                            namespaces=self.namespace)[0], "tlpMarking:TLPMarkingStructureType")

    def test_tlp_color(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/@color" % self.marking,
                                            namespaces=self.namespace)[0], "AMBER")

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Description/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "Fake National Lab")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Identity/stixCommon:Name/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "Fake")

    def test_information_source_produced_time(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Time/cyboxCommon:Produced_Time/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "2016-02-21T22:50:02+06:00")

    def test_indicator_time_stamp(self):
        test = self.output1.xpath("%s @timestamp" % self.indicator, namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_indicator_xsi_type(self):
        self.assertEqual(self.output1.xpath("%s @xsi:type" % self.indicator,
                                            namespaces=self.namespace)[0], "indicator:IndicatorType")

    def test_indicator_version(self):
        self.assertEqual(self.output1.xpath("%s @version" % self.indicator,
                                            namespaces=self.namespace)[0], "2.1.1")

    def test_indicator_type(self):
        self.assertEqual(self.output1.xpath("%s indicator:Type/text()" % self.indicator,
                                            namespaces=self.namespace)[0], "IP Watchlist")

    def test_indicator_description(self):
        self.assertEqual(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                            namespaces=self.namespace)[0],
                         "SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high")

    def test_indicator_keyword(self):
        self.assertEqual(self.output1.xpath("%s cybox:Keywords/cybox:Keyword/text()" % self.observable,
                                            namespaces=self.namespace)[0], "Scanning")

    def test_indicator_properties_type(self):
        self.assertEqual(self.output1.xpath("%s @xsi:type" % self.properties,
                                            namespaces=self.namespace)[0], "AddressObj:AddressObjectType")

    def test_indicator_properties_category(self):
        self.assertEqual(self.output1.xpath("%s @category" % self.properties,
                                            namespaces=self.namespace)[0], "ipv4-addr")

    def test_indicator_properties_indicator(self):
        self.assertEqual(self.output1.xpath("%s AddressObj:Address_Value/text()" % self.properties,
                                            namespaces=self.namespace)[0], "10.10.10.10")

    def test_indicator_properties_related_objects_properties(self):
        self.assertEqual(self.output1.xpath("%s cybox:Properties/@xsi:type" % self.related_obj,
                                            namespaces=self.namespace)[0], "PortObj:PortObjectType")

    def test_indicator_properties_related_objects_properties_port_value(self):
        self.assertEqual(len(self.output1.xpath("%s cybox:Properties/PortObj:Port_Value" % self.related_obj,
                                                namespaces=self.namespace)), 1)

    def test_indicator_properties_related_objects_properties_port_value_text(self):
        self.assertEqual(self.output1.xpath("%s cybox:Properties/PortObj:Port_Value/text()" % self.related_obj,
                                            namespaces=self.namespace)[0], "22")

    def test_indicator_properties_related_objects_properties_port_protocol(self):
        self.assertEqual(len(self.output1.xpath("%s cybox:Properties/PortObj:Layer4_Protocol" % self.related_obj,
                                                namespaces=self.namespace)), 1)

    def test_indicator_properties_related_objects_properties_port_protocol_text(self):
        self.assertEqual(self.output1.xpath("%s cybox:Properties/PortObj:Layer4_Protocol/text()" % self.related_obj,
                                            namespaces=self.namespace)[0], "TCP")

    def test_indicator_relationship_type(self):
        self.assertEqual(self.output1.xpath("%s cybox:Relationship/@xsi:type" % self.related_obj,
                                            namespaces=self.namespace)[0], "cyboxVocabs:ObjectRelationshipVocab-1.1")

    def test_indicator_relationship(self):
        self.assertEqual(self.output1.xpath("%s cybox:Relationship/text()" % self.related_obj,
                                            namespaces=self.namespace)[0], "Connected_To")

    def test_indicator_course_of_action_xsi(self):
        self.assertEqual(self.output1.xpath("%s @xsi:type" % self.coa,
                                            namespaces=self.namespace)[0], "coa:CourseOfActionType")

    def test_indicator_course_of_action_stage(self):
        self.assertEqual(self.output1.xpath("%s coa:Stage/text()" % self.coa,
                                            namespaces=self.namespace)[0], "Remedy")

    def test_indicator_course_of_action_type(self):
        self.assertEqual(self.output1.xpath("%s coa:Type/text()" % self.coa,
                                            namespaces=self.namespace)[0], "Perimeter Blocking")

    def test_indicator_sightings(self):
        self.assertEqual(self.output1.xpath("%s @sightings_count" % self.sightings,
                                            namespaces=self.namespace)[0], "12")

    def test_indicator_sightings_timestamp(self):
        self.assertEqual(self.output1.xpath("%s indicator:Sighting/@timestamp" % self.sightings,
                                            namespaces=self.namespace)[0], "2016-02-21T22:45:53-04:00")

    def test_indicator_sightings_timestamp_precision(self):
        self.assertEqual(self.output1.xpath("%s indicator:Sighting/@timestamp_precision" % self.sightings,
                                            namespaces=self.namespace)[0], "second")


class TestSTIXACSToSTIXTLP(unittest.TestCase):
    output1 = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    sightings = "%s indicator:Sightings/" % indicator
    observable = "%s indicator:Observable/" % indicator
    object = "%s cybox:Object/" % observable
    properties = "%s cybox:Properties/" % object
    related_obj = "%s cybox:Related_Objects/cybox:Related_Object/" % object
    coa = "%s indicator:Suggested_COAs/indicator:Suggested_COA/stixCommon:Course_Of_Action/" % indicator

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
            transform.add_parser('stixacs', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.add_parser('stix', input_file)
        output1_object = io.StringIO()

        transform.transform(io.StringIO(STIXACS), 'stixacs', 'stix', target_file=output1_object)
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_title(self):
        self.assertEqual(self.output1.xpath("%s stix:Title/text()" % self.header,
                                            namespaces=self.namespace)[0], "ACS-example.pdf")

    def test_package_description(self):
        self.assertEqual(self.output1.xpath("%s stix:Description/text()" % self.header,
                                            namespaces=self.namespace)[0], "Redirects to Malicious Websites")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_tlp_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)), set(["tlpMarking:TLPMarkingStructureType"]))

    def test_tlp_color(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@color" % self.marking,
                                                namespaces=self.namespace)), set(["AMBER"]))

    def test_information_time_produced_time(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Time/cyboxCommon:Produced_Time/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "2015-11-25T01:45:05+00:00")

    def test_indicator_timestamps(self):
        self.assertEqual(set(self.output1.xpath("%s @timestamp" % self.indicator, namespaces=self.namespace)),
                         set(["2015-11-26T00:35:06+00:00"]))

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.indicator, namespaces=self.namespace)),
                         set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("%s @version" % self.indicator, namespaces=self.namespace)),
                         set(["2.1.1"]))

    def test_indicator_title(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Title/text()" % self.indicator,
                                                namespaces=self.namespace)), set(["Original AAA Report Document"]))

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath(
            "%s indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()" % self.indicator,
            namespaces=self.namespace)), set(["Domain Watchlist"]))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                                namespaces=self.namespace)),
                         set(["Sample.pdf", "AAA Report Indicator", "Domain Indicator", "Just Another Indicator"]))

    def test_indicator_properties_xsitype(self):
        self.assertEqual(set(self.output1.xpath("%s cybox:Properties/@xsi:type" % self.object,
                                                namespaces=self.namespace)),
                         set(["DomainNameObj:DomainNameObjectType", "ArtifactObj:ArtifactObjectType"]))

    def test_indicator_properties_type(self):
        if "Domain Name" in self.output1.xpath("%s cybox:Properties/@type" % self.object,
                                               namespaces=self.namespace) or\
                        "fqdn" in self.output1.xpath("//indicator:Observable/cybox:Object/cybox:Properties/@type",
                                                     namespaces=self.namespace):
            self.assertIn("File", set(self.output1.xpath("%s cybox:Properties/@type" % self.object,
                                                         namespaces=self.namespace)))

    def test_indicator_properties_packaging_encoding(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Packaging/ArtifactObj:Encoding/@algorithm" % self.properties,
                                                namespaces=self.namespace)), set(["Base64"]))

    def test_indicator_properties_rawartifact(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Raw_Artifact/text()" % self.properties,
                                                namespaces=self.namespace)), set(["FILLINRAWDATAHERE"]))

    def test_indicator_properties_domainnames(self):
        self.assertEqual(set(self.output1.xpath("%s DomainNameObj:Value[@condition='Equals']/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["goo.gl/peter", "fake.com", "blog.website.net"]))


class TestSTIXACS30ToSTIXTLP(unittest.TestCase):
    output1 = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    sightings = "%s indicator:Sightings/" % indicator
    observable = "%s indicator:Observable/" % indicator
    object = "%s cybox:Object/" % observable
    properties = "%s cybox:Properties/" % object
    related_obj = "%s cybox:Related_Objects/cybox:Related_Object/" % object
    coa = "%s indicator:Suggested_COAs/indicator:Suggested_COA/stixCommon:Course_Of_Action/" % indicator

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

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_acs30.cfg'), 'r') as input_file:
            transform.add_parser('stixacs30', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.add_parser('stix_tlp', input_file)
        output1_object = io.StringIO()

        transform.transform(io.StringIO(STIXACS), 'stixacs30', 'stix_tlp', target_file=output1_object)
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_title(self):
        self.assertEqual(self.output1.xpath("%s stix:Title/text()" % self.header,
                                            namespaces=self.namespace)[0], "ACS-example.pdf")

    def test_package_description(self):
        self.assertEqual(self.output1.xpath("%s stix:Description/text()" % self.header,
                                            namespaces=self.namespace)[0], "Redirects to Malicious Websites")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_tlp_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)), set(["tlpMarking:TLPMarkingStructureType"]))

    def test_tlp_color(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@color" % self.marking,
                                                namespaces=self.namespace)), set(["AMBER"]))

    def test_indicator_timestamps(self):
        self.assertEqual(set(self.output1.xpath("%s @timestamp" % self.indicator, namespaces=self.namespace)),
                         set(["2015-11-26T00:35:06+00:00"]))

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.indicator, namespaces=self.namespace)),
                         set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("%s @version" % self.indicator, namespaces=self.namespace)),
                         set(["2.1.1"]))

    def test_indicator_title(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Title/text()" % self.indicator, namespaces=self.namespace)),
                         set(["Original AAA Report Document"]))

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath(
            "%s indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()" % self.indicator,
            namespaces=self.namespace)), set(["Domain Watchlist"]))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                                namespaces=self.namespace)),
                         set(["Sample.pdf", "AAA Report Indicator", "Domain Indicator", "Just Another Indicator"]))

    def test_indicator_properties_xsitype(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.properties, namespaces=self.namespace)),
                         set(["DomainNameObj:DomainNameObjectType", "ArtifactObj:ArtifactObjectType"]))

    def test_indicator_properties_type(self):
        if "Domain Name" in self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace) or\
                        "fqdn" in self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace):
            self.assertIn("File", set(self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace)))

    def test_indicator_properties_packaging_encoding(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Packaging/ArtifactObj:Encoding/@algorithm" % self.properties,
                                                namespaces=self.namespace)), set(["Base64"]))

    def test_indicator_properties_rawartifact(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Raw_Artifact/text()" % self.properties,
                                                namespaces=self.namespace)), set(["FILLINRAWDATAHERE"]))

    def test_indicator_properties_domainnames(self):
        self.assertEqual(set(self.output1.xpath("%s DomainNameObj:Value[@condition='Equals']/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["goo.gl/peter", "fake.com", "blog.website.net"]))


class TestKeyValueToSTIXTLP(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None

    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    sightings = "%s indicator:Sightings/" % indicator
    observable = "%s indicator:Observable/" % indicator
    object = "%s cybox:Object/" % observable
    properties = "%s cybox:Properties/" % object
    related_obj = "%s cybox:Related_Objects/cybox:Related_Object/" % object
    coa = "%s indicator:Suggested_COAs/indicator:Suggested_COA/stixCommon:Course_Of_Action/" % indicator

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
            transform.add_parser('stix', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.add_parser('keyvalue', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(KEYVALUE), 'keyvalue', 'stix', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                                namespaces=self.namespace)), set(["//node() | //@*"]))

    def test_tlp_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)), set(["tlpMarking:TLPMarkingStructureType"]))

    def test_tlp_color(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@color" % self.marking,
                                                namespaces=self.namespace)), set(["GREEN"]))

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.indicator, namespaces=self.namespace)),
                         set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("%s @version" % self.indicator, namespaces=self.namespace)),
                         set(["2.1.1"]))

    def test_indicator_timestamp(self):
        test = self.output1.xpath("%s @timestamp" % self.indicator, namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath(
            "%s indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()" % self.indicator,
            namespaces=self.namespace)), set(["Domain Watchlist", "IP Watchlist"]))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                                namespaces=self.namespace)),
                         set(['Attacker scanning for SSH, direction:ingress, confidence:0, severity:high',
                              'Attacker scanning for RDP, direction:ingress, confidence:0, severity:high',
                              'HTTP Response code 4xx, suspicious, direction:ingress, confidence:0, severity:low',
                              'Malicious domain, direction:egress, confidence:0, severity:high']))

    def test_indicator_observable_keywords(self):
        self.assertEqual(set(self.output1.xpath("%s cybox:Keywords/cybox:Keyword/text()" % self.observable,
                                                namespaces=self.namespace)),
                         set(['Reconnaissance', 'Scanning', 'Malware Traffic']))

    def test_indicator_properties_type(self):
        if "Domain Name" in self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace) or\
                        "fqdn" in self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace):
            self.assertTrue(True)

    def test_indicator_properties_category(self):
        self.assertEqual(set(self.output1.xpath("% s@category" % self.properties, namespaces=self.namespace)),
                         set(["ipv4-addr", "ipv6-addr"]))

    def test_indicator_properties_domainname(self):
        if "bad.scanning.dom"in self.output1.xpath("%s DomainNameObj:Value/text()" % self.properties,
                                                   namespaces=self.namespace):
            self.assertEqual(set(self.output1.xpath("%s DomainNameObj:Value/text()" % self.properties,
                                                    namespaces=self.namespace)), set(["bad.scanning.dom", "bad.domain"]))
        else:
            self.assertEqual(set(self.output1.xpath("%s DomainNameObj:Value/text()" % self.properties,
                                                    namespaces=self.namespace)), set(["bad.domain"]))

    def test_indicator_properties_address(self):
        if "10.11.12.14" in self.output1.xpath("%s AddressObj:Address_Value/text()" % self.properties,
                                               namespaces=self.namespace):
            self.assertEqual(set(self.output1.xpath("%s AddressObj:Address_Value/text()" % self.properties,
                                                    namespaces=self.namespace)),
                             set(["10.11.12.13", "10.11.12.14", "2001:db8:16::1"]))
        else:
            self.assertEqual(set(self.output1.xpath("%s AddressObj:Address_Value/text()" % self.properties,
                                                    namespaces=self.namespace)), set(["10.11.12.13", "2001:db8:16::1"]))

    def test_indicator_properties_port_value(self):
        self.assertEqual(set(self.output1.xpath("%s cybox:Properties/PortObj:Port_Value/text()" % self.related_obj,
                                                namespaces=self.namespace)), set(["3389", "22"]))

    def test_indicator_properties_port_protocol(self):
        self.assertEqual(set(self.output1.xpath("%s cybox:Properties/PortObj:Layer4_Protocol/text()" % self.related_obj,
                                                namespaces=self.namespace)), set(["TCP"]))

    def test_indicator_relatedobject_relationship(self):
        self.assertEqual(set(self.output1.xpath("%s cybox:Relationship/@xsi:type" % self.related_obj,
                                                namespaces=self.namespace)),
                         set(["cyboxVocabs:ObjectRelationshipVocab-1.1"]))

    def test_indicator_relationship(self):
        self.assertEqual(set(self.output1.xpath("%s cybox:Relationship/text()" % self.related_obj,
                                                namespaces=self.namespace)), set(["Connected_To"]))

    def test_indicator_sightings(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Sighting/@timestamp" % self.sightings,
                                                namespaces=self.namespace)), set(["2012-01-01T07:00:00+00:00"]))

    def test_indicator_sighting_precision(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Sighting/@timestamp_precision" % self.sightings,
                                                namespaces=self.namespace)), set(["second"]))


class TestCFM13DerivedDataTest(unittest.TestCase):
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
            transform.add_parser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.add_parser('stix_tlp', input_file)

        output1_object = io.StringIO()

        with tempfile.NamedTemporaryFile(mode="w+", prefix=CFM13ALERTUUID) as input_file:
            input_file.write(CFM13ALERT)
            input_file.seek(0)
            transform.transform(input_file, 'cfm13alert', 'stix_tlp', target_file=output1_object)

        cls.output1 = etree.XML(output1_object.getvalue())

    def test_cfm13ToStixTLP_uuid(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/@id", namespaces=self.namespace)[0],
                         "CFM:STIXPackage-37880b79-bb9e-4025-9813-94d07981d9ff")


class TestCRSIPToSTIXTLP(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None

    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    sightings = "%s indicator:Sightings/" % indicator
    observable = "%s indicator:Observable/" % indicator
    object = "%s cybox:Object/" % observable
    properties = "%s cybox:Properties/" % object
    related_obj = "%s cybox:Related_Objects/cybox:Related_Object/" % object
    coa = "%s indicator:Suggested_COAs/indicator:Suggested_COA/stixCommon:Course_Of_Action/" % indicator

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
        'DomainNameObj': "http://cybox.mitre.org/objects#DomainNameObject-1",
        'FileObj': "http://cybox.mitre.org/objects#FileObject-2"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/crisp_json.cfg'), 'r') as input_file:
            transform.add_parser('crisp', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.add_parser('stix_tlp', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(CRISP), 'crisp', 'stix_tlp', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_title(self):
        self.assertEqual(self.output1.xpath("%s stix:Title/text()" % self.header,
                                            namespaces=self.namespace)[0], "CRISP-17-1111")

    def test_package_description(self):
        self.assertEqual(self.output1.xpath("%s stix:Description/text()" % self.header,
                                            namespaces=self.namespace)[0], "Fake report Description")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Identity/stixCommon:Name/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "PNNL")

    def test_information_source_produced_time(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Time/cyboxCommon:Produced_Time/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "2017-04-10T20:31:02+00:00")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_tlp_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)), set(["tlpMarking:TLPMarkingStructureType"]))

    def test_tlp_color(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@color" % self.marking,
                                                namespaces=self.namespace)), set(["AMBER"]))

    def test_indicator_timestamp(self):
        test = self.output1.xpath("%s @timestamp" % self.indicator, namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.indicator, namespaces=self.namespace)),
                         set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("%s @version" % self.indicator, namespaces=self.namespace)),
                         set(["2.1.1"]))

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath(
            "%s indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()" % self.indicator,
            namespaces=self.namespace)), set(["IP Watchlist", "File Hash Watchlist", "Malicious E-mail"]))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                                namespaces=self.namespace)),
                         set(["CRISP Report Indicator"]))

    def test_indicator_address_values(self):
        self.assertEqual(set(self.output1.xpath("%s AddressObj:Address_Value/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["10.10.10.11", "10.11.12.13", "fakeEmail@fake.com"]))

    def test_indicator_properties_xsitype(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.properties, namespaces=self.namespace)),
                         set(["FileObj:FileObjectType", "AddressObj:AddressObjectType"]))

    def test_indicator_properties_category(self):
        self.assertEqual(set(self.output1.xpath("%s @category" % self.properties, namespaces=self.namespace)),
                         set(["ipv4-addr", "e-mail"]))

    def test_indicator_properties_type(self):
        if "Domain Name" in self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace) or\
                        "fqdn" in self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace):
            self.assertIn("File", set(self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace)))

    def test_indicator_hash_values(self):
        self.assertEqual(set(self.output1.xpath("%s FileObj:Hashes/cyboxCommon:Hash/cyboxCommon:Simple_Hash_Value/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["9e107d9d372bb6826bd81d3542a419d6", "ae147d9d372bb6826bd81d3542a419d65c29f2",
                              "e7ff9d32ab4c018dd32fff98376826bd81ae147d352bb68207d9da7a",
                              "32fff98ff9d32a6bd81da419d65ce147d352bb682018dd9d372bb6826bde107f",
                              "fff98fdd32ff147d9d372bb682d372bb6819d65c299d372bb6826b976826b47d352bb681da419dd32fff98376826bd8b",
                              "a879bac79a89e9f890a8c0a87c7b778da99ad879c79b8787aa0279b98abd89c78e09e880ff97a0870ae87b7089c07d070ab89378ad79ab79c78d9a0987c890d7"]))

    def test_indicator_hash_type(self):
        self.assertEqual(set(self.output1.xpath("%s FileObj:Hashes/cyboxCommon:Hash/cyboxCommon:Type/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["SHA1", "MD5", "SHA224", "SHA256", "SHA384", "SHA512"]))

    def test_indicator_file_path(self):
        self.assertEqual(set(self.output1.xpath("%s FileObj:File_Path/text()" % self.properties,
                                                namespaces=self.namespace)), set(["test"]))

    def test_indicator_file_name(self):
        self.assertEqual(set(self.output1.xpath("%s FileObj:File_Name/text()" % self.properties,
                                                namespaces=self.namespace)), set(["Test_File_Name"]))

    def test_indicator_hash_xsi_type(self):
        self.assertEqual(self.output1.xpath("%s FileObj:Hashes/cyboxCommon:Hash/cyboxCommon:Type/@xsi:type" % self.properties,
                                            namespaces=self.namespace)[0], "cyboxVocabs:HashNameVocab-1.0")

if __name__ == '__main__':
    unittest.main()
