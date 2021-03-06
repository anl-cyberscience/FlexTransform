import io
import os
import unittest
import arrow

from lxml import etree

from FlexTransform import FlexTransform
from FlexTransform.test.SampleInputs import CFM13ALERT, STIXTLP, KEYVALUE, STIXACS, CRISP, IIDBADIPV4, IIDDYNAMICBADHOST,\
    IIDACTIVEBADHOST, IIDCOMBINEDRECENT


class TestCFM13Alert1ToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    observable = "/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/"
    object = "%s cybox:Object/" % observable
    related_object_properties = "%s cybox:Related_Objects/cybox:Related_Object/cybox:Properties/" % object
    sightings = "%s indicator:Sightings/" % indicator

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
        'edh2': "urn:edm:edh:v2",
        'ArtifactObj': "http://cybox.mitre.org/objects#ArtifactObject-2"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            transform.add_parser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stix_acs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(CFM13ALERT), 'cfm13alert', 'stix_acs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_package_profile(self):
        self.assertEqual(self.output1.xpath("%s stix:Profiles/stixCommon:Profile/text()" % self.header,
                                            namespaces=self.namespace)[0], "ISA Profile v1.0")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace)[0], "//node() | //@*")

    def test_indicator_information_source_description(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Description/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "U.S. Department of Energy")

    def test_indicator_information_source_name(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Identity/stixCommon:Name/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "DOE")

    def test_marking_type(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                            namespaces=self.namespace)[0], "edh2cyberMarking:ISAMarkingsType")
        # "edh2cyberMarkingAssert:ISAMarkingsAssertionType"]))

    def test_marking_isam_version(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/@isam_version" % self.marking,
                                            namespaces=self.namespace)[0], "1.0")

    def test_marking_most_restricitive(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/@most_restrictive" % self.marking,
                                            namespaces=self.namespace)[0], "true")

    def test_marking_create_date_time(self):
        test = self.output1.xpath("%s marking:Marking_Structure/edh2:CreateDateTime/text()" % self.marking,
                                  namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_marking_responsible_entity(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/edh2:ResponsibleEntity/text()" % self.marking,
                                            namespaces=self.namespace)[0], "CUST:USA.DOE")

    def test_marking_policy_ref(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/edh2:PolicyRef/text()" % self.marking,
                                            namespaces=self.namespace)[0],
                         "urn:isa:policy:acs:ns:v2.0?privdefault=permit")

    def test_marking_control_set(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/edh2:ControlSet/text()" % self.marking,
                                            namespaces=self.namespace)[0], "CLS:U CUI:FOUO")

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
        self.assertEqual(self.output1.xpath("%s cybox:Properties/@xsi:type" % self.object,
                                            namespaces=self.namespace)[0], "AddressObj:AddressObjectType")

    def test_indicator_properties_category(self):
        self.assertEqual(self.output1.xpath("%s cybox:Properties/@category" % self.object,
                                            namespaces=self.namespace)[0], "ipv4-addr")

    def test_indicator_properties_indicator(self):
        self.assertEqual(self.output1.xpath("%s cybox:Properties/AddressObj:Address_Value/text()" % self.object,
                                            namespaces=self.namespace)[0], "10.10.10.10")

    def test_indicator_properties_related_objects_properties(self):
        self.assertEqual(self.output1.xpath("%s @xsi:type" % self.related_object_properties,
                                            namespaces=self.namespace)[0], "PortObj:PortObjectType")

    def test_indicator_properties_related_objects_properties_port_value(self):
        self.assertEqual(len(self.output1.xpath("%s PortObj:Port_Value" % self.related_object_properties,
                                                namespaces=self.namespace)), 1)

    def test_indicator_properties_related_objects_properties_port_value_text(self):
        self.assertEqual(self.output1.xpath("%s PortObj:Port_Value/text()" % self.related_object_properties,
                                            namespaces=self.namespace)[0], "22")

    def test_indicator_properties_related_objects_properties_port_protocol(self):
        self.assertEqual(len(self.output1.xpath("%s PortObj:Layer4_Protocol" % self.related_object_properties,
                                                namespaces=self.namespace)), 1)

    def test_indicator_properties_related_objects_properties_port_protocol_text(self):
        self.assertEqual(self.output1.xpath("%s PortObj:Layer4_Protocol/text()" % self.related_object_properties,
                                            namespaces=self.namespace)[0], "TCP")

    def test_indicator_sightings_count(self):
        self.assertEqual(self.output1.xpath("%s indicator:Sightings/@sightings_count" % self.indicator,
                                            namespaces=self.namespace)[0], "12")

    def test_indicator_sightings_sighting_timestamp(self):
        self.assertEqual(self.output1.xpath("%s indicator:Sighting/@timestamp" % self.sightings,
                                            namespaces=self.namespace)[0], "2016-02-21T22:45:53-04:00")

    def test_indicator_sightings_sighting_timestamp_seconds(self):
        self.assertEqual(self.output1.xpath("%s indicator:Sighting/@timestamp_precision" % self.sightings,
                                            namespaces=self.namespace)[0], "second")


class TestSTIXTLPToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    properties = "%s indicator:Observable/cybox:Object/cybox:Properties/" % indicator
    hash = "%s FileObj:Hashes/cyboxCommon:Hash/" % properties

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
        'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
        'FileObj': "http://cybox.mitre.org/objects#FileObject-2",
        'edh2': "urn:edm:edh:v2",
        'edh2cyberMarking': "http://www.us-cert.gov/essa/Markings/ISAMarkings",
        'edh2cyberMarkingAssert': "xmlns:edh2cyberMarkingAssert",

    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            transform.add_parser('stixtlp', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        output1_object = io.StringIO()
        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(STIXTLP), 'stixtlp', 'stixacs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_title(self):
        self.assertEqual(self.output1.xpath("%s stix:Title/text()" % self.header,
                                            namespaces=self.namespace)[0], "Test PDF")

    def test_description(self):
        self.assertEqual(self.output1.xpath("%s stix:Description/text()" % self.header,
                                            namespaces=self.namespace)[0], "Ransomware Update")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_profile(self):
        self.assertEqual(self.output1.xpath("%s stix:Profiles/stixCommon:Profile/text()" % self.header,
                                            namespaces=self.namespace)[0], "ISA Profile v1.0")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_marking_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)),
                         set(['edh2cyberMarking:ISAMarkingsType', 'edh2cyberMarkingAssert:ISAMarkingsAssertionType']))

    def test_marking_isam_version(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@isam_version" % self.marking,
                                                namespaces=self.namespace)), set(['1.0']))

    def test_marking_create_date_time(self):
        test = self.output1.xpath("%s marking:Marking_Structure/edh2:CreateDateTime/text()" % self.marking,
                                  namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_marking_responsible_entity(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:ResponsibleEntity/text()" % self.marking,
                                                namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:PolicyRef/text()" % self.marking,
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:ControlSet/text()" % self.marking,
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_marking_most_restrictive(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@most_restrictive" % self.marking,
                                                namespaces=self.namespace)), set(['true']))

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Description/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "U.S. Department of Energy")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Identity/stixCommon:Name/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "DOE")

    def test_information_time_produced_time(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Time/cyboxCommon:Produced_Time/text()" % self.information_source,
                                            namespaces=self.namespace)[0], '2016-03-23T16:45:05+04:00')

    def test_indicator_timestamps(self):
        self.assertEqual(set(self.output1.xpath("%s @timestamp" % self.indicator, namespaces=self.namespace)),
                         set(['2016-03-29T19:33:13+00:00', '2016-03-29T19:33:13+06:00',
                              '2016-03-29T19:33:13+05:00', '2016-03-29T19:33:13+01:00',
                              '2016-03-29T19:33:13+07:00', '2016-03-29T19:33:13+08:00', '2016-03-29T19:33:13+02:00']))

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.indicator, namespaces=self.namespace)),
                         set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("%s @version" % self.indicator, namespaces=self.namespace)),
                         set(["2.1.1"]))

    def test_indicator_title(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Title/text()" % self.indicator, namespaces=self.namespace)),
                         set(["Original CRISP Report Document"]))

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath(
            "%s indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()" % self.indicator,
            namespaces=self.namespace)),
                         set(['IP Watchlist', 'URL Watchlist', 'File Hash Watchlist']))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                                namespaces=self.namespace)),
                         set(['CRISP-16-307.pdf', 'Energy Sector Indicator']))

    def test_indicator_properties_xsitype(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.properties,
                                                namespaces=self.namespace)),
                         set(["AddressObj:AddressObjectType", "URIObj:URIObjectType",
                              "FileObj:FileObjectType", "ArtifactObj:ArtifactObjectType"]))

    def test_indicator_properties_type(self):
        self.assertEqual(set(self.output1.xpath("%s @type" % self.properties,
                                                namespaces=self.namespace)), set(["File", "URL"]))

    def test_indicator_properties_category(self):
        self.assertEqual(set(self.output1.xpath("%s @category" % self.properties, namespaces=self.namespace)),
                         set(["ipv4-addr"]))

    def test_indicator_properties_packaging_encoding(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Packaging/ArtifactObj:Encoding/@algorithm" % self.properties,
                                                namespaces=self.namespace)), set(["Base64"]))

    def test_indicator_properties_rawartifact(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Raw_Artifact/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA+PgpzdHJlYW0KeAErVAhUKFQwNAIhUwsLVPRgo="]))

    def test_indicator_address_values(self):
        self.assertEqual(set(self.output1.xpath("%s AddressObj:Address_Value[@condition='Equals']/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["10.10.10.10", "13.13.13.13", "12.12.12.12", "11.11.11.11", "14.14.14.14"]))

    def test_indicator_file_values(self):
        self.assertEqual(set(self.output1.xpath("%s FileObj:File_Path[@condition='Equals']/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["C://window32/tst.dat", "webmail.p55.be", "/user/strange/object.sh", "D://replacement.exe"]))

    def test_indicator_URI_values(self):
        self.assertEqual(set(self.output1.xpath("%s URIObj:Value[@condition='Equals']/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["bad.domain.be/poor/path", "fake.site.com/malicious.js"]))

    def test_indicator_hash_xsitype(self):
        self.assertEqual(set(self.output1.xpath("%s cyboxCommon:Type[@condition='Equals']/@xsi:type" % self.hash,
                                                namespaces=self.namespace)), set(["cyboxVocabs:HashNameVocab-1.0"]))

    def test_indicator_hash_type(self):
        self.assertEqual(set(self.output1.xpath("%s cyboxCommon:Type[@condition='Equals']/text()" % self.hash,
                                                namespaces=self.namespace)), set(["MD5"]))


class TestSTIXACS30ToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    properties = "%s indicator:Observable/cybox:Object/cybox:Properties/" % indicator
    hash = "%s FileObj:Hashes/cyboxCommon:Hash/" % properties

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
        'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
        'FileObj': "http://cybox.mitre.org/objects#FileObject-2",
        'edh2': "urn:edm:edh:v2",
        'edh2cyberMarking': "http://www.us-cert.gov/essa/Markings/ISAMarkings",
        'edh2cyberMarkingAssert': "xmlns:edh2cyberMarkingAssert",
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_acs30.cfg'), 'r') as input_file:
            transform.add_parser('stixacs30', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(STIXACS), 'stixacs30', 'stixacs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_title(self):
        self.assertEqual(self.output1.xpath("%s stix:Title/text()" % self.header,
                                            namespaces=self.namespace)[0], "ACS-example.pdf")

    def test_description(self):
        self.assertEqual(self.output1.xpath("%s stix:Description/text()" % self.header,
                                            namespaces=self.namespace)[0], "Redirects to Malicious Websites")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_profile(self):
        self.assertEqual(self.output1.xpath("%s stix:Profiles/stixCommon:Profile/text()" % self.header,
                                            namespaces=self.namespace)[0], "ISA Profile v1.0")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_marking_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)),
                         set(['edh2cyberMarking:ISAMarkingsType', 'edh2cyberMarkingAssert:ISAMarkingsAssertionType']))

    def test_marking_isam_version(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@isam_version" % self.marking,
                                                namespaces=self.namespace)), set(['1.0']))

    def test_marking_most_restrictive(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@most_restrictive" % self.marking,
                                                namespaces=self.namespace)), set(['true']))

    def test_marking_create_date_time(self):
        test = self.output1.xpath("%s marking:Marking_Structure/edh2:CreateDateTime/text()" % self.marking,
                                  namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_marking_responsible_entity(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:ResponsibleEntity/text()" % self.marking,
                                                namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:PolicyRef/text()" % self.marking,
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:ControlSet/text()" % self.marking,
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_information_source_description(self):
        self.assertEqual(set(self.output1.xpath("%s stixCommon:Description/text()" % self.information_source,
                                                namespaces=self.namespace)), set(["U.S. Department of Energy"]))

    def test_information_source_name(self):
        self.assertEqual(set(self.output1.xpath("%s stixCommon:Identity/stixCommon:Name/text()" % self.information_source,
                                                namespaces=self.namespace)), set(["DOE"]))

    def test_information_time_produced_time(self):
        test = self.output1.xpath("%s stixCommon:Time/cyboxCommon:Produced_Time/text()" % self.information_source,
                                  namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_indicator_timestamps(self):
        self.assertEqual(set(self.output1.xpath("%s @timestamp" % self.indicator,
                                                namespaces=self.namespace)), set(['2015-11-26T00:35:06+00:00']))

    def test_indicator_types(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.indicator,
                                                namespaces=self.namespace)), set(["indicator:IndicatorType"]))

    def test_indicator_version(self):
        self.assertEqual(set(self.output1.xpath("%s @version" % self.indicator,
                                                namespaces=self.namespace)), set(["2.1.1"]))

    def test_indicator_title(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Title/text()" % self.indicator,
                                                namespaces=self.namespace)), set(["Original AAA Report Document"]))

    def test_indicator_type(self):
        self.assertEqual(set(self.output1.xpath(
            "%s indicator:Type[@xsi:type='stixVocabs:IndicatorTypeVocab-1.1']/text()" % self.indicator,
            namespaces=self.namespace)), set(['Domain Watchlist']))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                                namespaces=self.namespace)),
                         set(['Domain Indicator', 'AAA Report Indicator', 'Sample.pdf', 'Just Another Indicator']))

    def test_indicator_properties_xsitype(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.properties, namespaces=self.namespace)),
                         set(["DomainNameObj:DomainNameObjectType", "ArtifactObj:ArtifactObjectType"]))

    def test_indicator_properties_type(self):
        self.assertEqual(set(self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace)),
                         set(["File", "FQDN"]))

    def test_indicator_properties_packaging_encoding(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Packaging/ArtifactObj:Encoding/@algorithm" % self.properties,
                                                namespaces=self.namespace)), set(["Base64"]))

    def test_indicator_properties_rawartifact(self):
        self.assertEqual(set(self.output1.xpath("%s ArtifactObj:Raw_Artifact/text()" % self.properties,
                                                namespaces=self.namespace)), set(["FILLINRAWDATAHERE"]))

    def test_indicator_domain_values(self):
        self.assertEqual(set(self.output1.xpath("%s DomainNameObj:Value/text()" % self.properties,
                                                namespaces=self.namespace)),
                         set(["goo.gl/peter", "fake.com", "blog.website.net"]))

    def test_indicator_sightings_count(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Sightings/@sightings_count" % self.indicator,
                                                namespaces=self.namespace)), set(["2", "4"]))


class TestKeyValueToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    properties = "%s indicator:Observable/cybox:Object/cybox:Properties/" % indicator
    sightings = "%s indicator:Sightings/" % indicator
    observable = "/stix:STIX_Package/stix:Indicators/stix:Indicator/indicator:Observable/"
    object = "%s cybox:Object/" % observable
    related_obj = "%s cybox:Related_Objects/cybox:Related_Object/" % object

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
        'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
        'FileObj': "http://cybox.mitre.org/objects#FileObject-2",
        'edh2': "urn:edm:edh:v2",
        'edh2cyberMarking': "http://www.us-cert.gov/essa/Markings/ISAMarkings",
        'edh2cyberMarkingAssert': "xmlns:edh2cyberMarkingAssert",
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.add_parser('keyvalue', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(KEYVALUE), 'keyvalue', 'stixacs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_profile(self):
        self.assertEqual(self.output1.xpath("%s stix:Profiles/stixCommon:Profile/text()" % self.header,
                                            namespaces=self.namespace)[0], "ISA Profile v1.0")

    def test_controlled_structure_text(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                                namespaces=self.namespace)), set(["//node() | //@*"]))

    def test_marking_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)),
                         set(['edh2cyberMarking:ISAMarkingsType', 'edh2cyberMarkingAssert:ISAMarkingsAssertionType']))

    def test_marking_isam_version(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@isam_version" % self.marking,
                                                namespaces=self.namespace)), set(['1.0']))

    def test_marking_most_restrictive(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@most_restrictive" % self.marking,
                                                namespaces=self.namespace)), set(['true']))

    def test_marking_create_date_time(self):
        test = self.output1.xpath("%s marking:Marking_Structure/edh2:CreateDateTime/text()" % self.marking,
                                  namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_marking_responsible_entity(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:ResponsibleEntity/text()" % self.marking,
                                                namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:PolicyRef/text()" % self.marking,
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:ControlSet/text()" % self.marking,
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_information_source_description(self):
        self.assertEqual(set(self.output1.xpath("%s stixCommon:Description/text()" % self.information_source,
                                                namespaces=self.namespace)), set(["U.S. Department of Energy"]))

    def test_information_source_name(self):
        self.assertEqual(set(self.output1.xpath("%s stixCommon:Identity/stixCommon:Name/text()" % self.information_source,
                                                namespaces=self.namespace)), set(["DOE"]))

    def test_information_time_produced_time(self):
        test = self.output1.xpath("%s stixCommon:Time/cyboxCommon:Produced_Time/text()" % self.information_source,
                                  namespaces=self.namespace)[0]
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
            namespaces=self.namespace)), set(['IP Watchlist', 'Domain Watchlist']))

    def test_indicator_description(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Description/text()" % self.indicator,
                                                namespaces=self.namespace)),
                         set(['Malicious domain, direction:egress, confidence:0, severity:high',
                              'HTTP Response code 4xx, suspicious, direction:ingress, confidence:0, severity:low',
                              'Attacker scanning for SSH, direction:ingress, confidence:0, severity:high',
                              'Attacker scanning for RDP, direction:ingress, confidence:0, severity:high']))

    def test_indicator_observable_keywords(self):
        self.assertEqual(set(self.output1.xpath("%s cybox:Keywords/cybox:Keyword/text()" % self.observable,
                                                namespaces=self.namespace)),
                         set(['Reconnaissance', 'Scanning', 'Malware Traffic']))

    def test_indicator_properties_xsitype(self):
        self.assertEqual(set(self.output1.xpath("%s @xsi:type" % self.properties, namespaces=self.namespace)),
                         set(["AddressObj:AddressObjectType", "DomainNameObj:DomainNameObjectType"]))

    def test_indicator_properties_type(self):
        self.assertEqual(set(self.output1.xpath("%s @type" % self.properties, namespaces=self.namespace)),
                         set(["FQDN"]))

    def test_indicator_properties_category(self):
        self.assertEqual(set(self.output1.xpath("%s @category" % self.properties, namespaces=self.namespace)),
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
        self.assertEqual(set(self.output1.xpath("%s cybox:Relationship/text()" % self.related_obj,
                                                namespaces=self.namespace)), set(["Connected_To"]))

    def test_indicator_sightings(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Sighting/@timestamp" % self.sightings,
                                                namespaces=self.namespace)), set(["2012-01-01T07:00:00+00:00"]))

    def test_indicator_sighting_precision(self):
        self.assertEqual(set(self.output1.xpath("%s indicator:Sighting/@timestamp_precision" % self.sightings,
                                                namespaces=self.namespace)), set(["second"]))

class TestCRSIPToSTIXACS(unittest.TestCase):
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
        'edh2': "urn:edm:edh:v2",
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
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stix_acs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(CRISP), 'crisp', 'stix_acs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_package_title(self):
        self.assertEqual(self.output1.xpath("%s stix:Title/text()" % self.header,
                                            namespaces=self.namespace)[0], "CRISP-17-1111")

    def test_package_description(self):
        self.assertEqual(self.output1.xpath("%s stix:Description/text()" % self.header,
                                            namespaces=self.namespace)[0], "Fake report Description")

    def test_package_profiles(self):
        self.assertEqual(self.output1.xpath("%s stix:Profiles/stixCommon:Profile/text()" % self.header,
                                            namespaces=self.namespace)[0], "ISA Profile v1.0")

    def test_acs30_type(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@xsi:type" % self.marking,
                                                namespaces=self.namespace)),
                         set(["edh2cyberMarking:ISAMarkingsType", "edh2cyberMarkingAssert:ISAMarkingsAssertionType"]))

    def test_acs30_isam_version(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/@isam_version" % self.marking,
                                                namespaces=self.namespace)), set(["1.0"]))

    def test_marking_create_date_time(self):
        test = self.output1.xpath("%s marking:Marking_Structure/edh2:CreateDateTime/text()" % self.marking,
                                  namespaces=self.namespace)[0]
        if test == self.utc_before:
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_marking_responsible_entity(self):
        self.assertEqual(
            set(self.output1.xpath("%s marking:Marking_Structure/edh2:ResponsibleEntity/text()" % self.marking,
                                   namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:PolicyRef/text()" % self.marking,
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("%s marking:Marking_Structure/edh2:ControlSet/text()" % self.marking,
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_most_restrictive(self):
        self.assertEqual(self.output1.xpath("%s marking:Marking_Structure/@most_restrictive" % self.marking,
                                            namespaces=self.namespace)[0], "true")

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Description/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "U.S. Department of Energy")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("%s stixCommon:Identity/stixCommon:Name/text()" % self.information_source,
                                            namespaces=self.namespace)[0], "DOE")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/@xsi:type" % self.header,
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("%s stix:Package_Intent/text()" % self.header,
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("%s marking:Controlled_Structure/text()" % self.marking,
                                            namespaces=self.namespace), ["//node() | //@*"])

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
                         set(["Energy Sector Indicator"]))

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


class TestIIDCombinedRecentToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    properties = "{} indicator:Observable/cybox:Object/cybox:Properties/".format(indicator)
    hash = "{} FileObj:Hashes/cyboxCommon:Hash/".format(properties)

    namespace = {
    'cyboxCommon': "http://cybox.mitre.org/common-2",
    'cybox': "http://cybox.mitre.org/cybox-2",
    'cyboxVocabs': "http://cybox.mitre.org/default_vocabularies-2",
    'URIObj': "http://cybox.mitre.org/objects#URIObject-2",
    'marking': "http://data-marking.mitre.org/Marking-1",
    'indicator': "http://stix.mitre.org/Indicator-2",
    'stixCommon': "http://stix.mitre.org/common-1",
    'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
    'stix': "http://stix.mitre.org/stix-1",
    'isa': "http://www.us-cert.gov/essa",
    'edh2cyberMarkingAssert': "http://www.us-cert.gov/essa/Markings/ISAMarkingAssertions",
    'edh2cyberMarking': "http://www.us-cert.gov/essa/Markings/ISAMarkings",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'edh2': "urn:edm:edh:v2"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_combined_recent.cfg'), 'r') as input_file:
            transform.add_parser('iid_combined_recent', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(STIXACS), 'iid_combined_recent', 'stixacs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_most_restrictive(self):
        self.assertEqual(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                            namespaces=self.namespace)[0], "true")

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Description/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "U.S. Department of Energy")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Identity/stixCommon:Name/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "DOE")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/@xsi:type".format(self.header),
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/text()".format(self.header),
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("{} marking:Controlled_Structure/text()".format(self.marking),
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_indicator_timestamp(self):
        test = self.output1.xpath("{} @timestamp".format(self.indicator), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_acs_type(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@xsi:type".format(self.marking),
                                                namespaces=self.namespace)), set(["edh2cyberMarking:ISAMarkingsType",
                                                                                  "edh2cyberMarkingAssert:ISAMarkingsAssertionType"]))

    def test_acs_version(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@isam_version".format(self.marking),
                                                namespaces=self.namespace)), set(["1.0"]))

    def test_acs_most_restriction(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                                namespaces=self.namespace)), set(["true"]))

    def test_responsible_enity(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarking:ISAMarkingsType']/edh2:ResponsibleEntity/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))



class TestIIDActiveHostToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    properties = "{} indicator:Observable/cybox:Object/cybox:Properties/".format(indicator)
    hash = "{} FileObj:Hashes/cyboxCommon:Hash/".format(properties)

    namespace = {
        'cyboxCommon': "http://cybox.mitre.org/common-2",
        'cybox': "http://cybox.mitre.org/cybox-2",
        'cyboxVocabs': "http://cybox.mitre.org/default_vocabularies-2",
        'DomainNameObj': "http://cybox.mitre.org/objects#DomainNameObject-1",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'stixCommon': "http://stix.mitre.org/common-1",
        'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
        'stix': "http://stix.mitre.org/stix-1",
        'isa': "http://www.us-cert.gov/essa",
        'edh2cyberMarkingAssert': "http://www.us-cert.gov/essa/Markings/ISAMarkingAssertions",
        'edh2cyberMarking': "http://www.us-cert.gov/essa/Markings/ISAMarkings",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'edh2': "urn:edm:edh:v2"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_host_active.cfg'), 'r') as input_file:
            transform.add_parser('iid_host_active', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(STIXACS), 'iid_host_active', 'stixacs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_most_restrictive(self):
        self.assertEqual(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                            namespaces=self.namespace)[0], "true")

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Description/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "U.S. Department of Energy")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Identity/stixCommon:Name/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "DOE")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/@xsi:type".format(self.header),
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/text()".format(self.header),
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("{} marking:Controlled_Structure/text()".format(self.marking),
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_indicator_timestamp(self):
        test = self.output1.xpath("{} @timestamp".format(self.indicator), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_acs_type(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@xsi:type".format(self.marking),
                                                namespaces=self.namespace)), set(["edh2cyberMarking:ISAMarkingsType",
                                                                                  "edh2cyberMarkingAssert:ISAMarkingsAssertionType"]))

    def test_acs_version(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@isam_version".format(self.marking),
                                                namespaces=self.namespace)), set(["1.0"]))

    def test_acs_most_restriction(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                                namespaces=self.namespace)), set(["true"]))

    def test_responsible_enity(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarking:ISAMarkingsType']/edh2:ResponsibleEntity/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

class TestIIDDynamicHostToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    properties = "{} indicator:Observable/cybox:Object/cybox:Properties/".format(indicator)
    hash = "{} FileObj:Hashes/cyboxCommon:Hash/".format(properties)

    namespace = {
        'cyboxCommon': "http://cybox.mitre.org/common-2",
	    'cybox': "http://cybox.mitre.org/cybox-2",
	    'cyboxVocabs': "http://cybox.mitre.org/default_vocabularies-2",
	    'DomainNameObj': "http://cybox.mitre.org/objects#DomainNameObject-1",
	    'marking': "http://data-marking.mitre.org/Marking-1",
	    'indicator': "http://stix.mitre.org/Indicator-2",
	    'stixCommon': "http://stix.mitre.org/common-1",
	    'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
	    'stix': "http://stix.mitre.org/stix-1",
	    'isa': "http://www.us-cert.gov/essa",
	    'edh2cyberMarkingAssert': "http://www.us-cert.gov/essa/Markings/ISAMarkingAssertions",
	    'edh2cyberMarking': "http://www.us-cert.gov/essa/Markings/ISAMarkings",
	    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
	    'edh2': "urn:edm:edh:v2"
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_host_dynamic.cfg'), 'r') as input_file:
            transform.add_parser('iid_host_dynamic', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(STIXACS), 'iid_host_dynamic', 'stixacs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_most_restrictive(self):
        self.assertEqual(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                            namespaces=self.namespace)[0], "true")

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Description/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "U.S. Department of Energy")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Identity/stixCommon:Name/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "DOE")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/@xsi:type".format(self.header),
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/text()".format(self.header),
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("{} marking:Controlled_Structure/text()".format(self.marking),
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_indicator_timestamp(self):
        test = self.output1.xpath("{} @timestamp".format(self.indicator), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_acs_type(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@xsi:type".format(self.marking),
                                                namespaces=self.namespace)), set(["edh2cyberMarking:ISAMarkingsType",
                                                                                  "edh2cyberMarkingAssert:ISAMarkingsAssertionType"]))

    def test_acs_version(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@isam_version".format(self.marking),
                                                namespaces=self.namespace)), set(["1.0"]))

    def test_acs_most_restriction(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                                namespaces=self.namespace)), set(["true"]))

    def test_responsible_enity(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarking:ISAMarkingsType']/edh2:ResponsibleEntity/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))


class TestIIDBadIPV4ToSTIXACS(unittest.TestCase):
    output1 = None
    utc_before = None
    utc_after = None
    header = "/stix:STIX_Package/stix:STIX_Header/"
    marking = "/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/"
    information_source = "/stix:STIX_Package/stix:STIX_Header/stix:Information_Source/"
    indicator = "/stix:STIX_Package/stix:Indicators/stix:Indicator/"
    properties = "{} indicator:Observable/cybox:Object/cybox:Properties/".format(indicator)
    hash = "{} FileObj:Hashes/cyboxCommon:Hash/".format(properties)

    namespace = {
        'cyboxCommon': "http://cybox.mitre.org/common-2",
	    'cybox': "http://cybox.mitre.org/cybox-2",
	    'cyboxVocabs': "http://cybox.mitre.org/default_vocabularies-2",
	    'AddressObj': "http://cybox.mitre.org/objects#AddressObject-2",
	    'marking': "http://data-marking.mitre.org/Marking-1",
	    'indicator': "http://stix.mitre.org/Indicator-2",
	    'stixCommon': "http://stix.mitre.org/common-1",
	    'stixVocabs': "http://stix.mitre.org/default_vocabularies-1",
	    'stix': "http://stix.mitre.org/stix-1",
	    'isa': "http://www.us-cert.gov/essa",
	    'edh2cyberMarkingAssert': "http://www.us-cert.gov/essa/Markings/ISAMarkingAssertions",
	    'edh2cyberMarking': "http://www.us-cert.gov/essa/Markings/ISAMarkings",
	    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
	    'edh2': "urn:edm:edh:v2",
    }

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_host_dynamic.cfg'), 'r') as input_file:
            transform.add_parser('iid_host_dynamic', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stixacs', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        transform.transform(io.StringIO(STIXACS), 'iid_host_dynamic', 'stixacs', target_file=output1_object)
        cls.utc_after = arrow.utcnow().format("YYYY-MM-DDTHH:mm:ssZZ")
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_marking_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)),
                         set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_marking_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

    def test_most_restrictive(self):
        self.assertEqual(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                            namespaces=self.namespace)[0], "true")

    def test_information_source_description(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Description/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "U.S. Department of Energy")

    def test_information_source_name(self):
        self.assertEqual(self.output1.xpath("{} stixCommon:Identity/stixCommon:Name/text()".format(self.information_source),
                                            namespaces=self.namespace)[0], "DOE")

    def test_package_intent_type(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/@xsi:type".format(self.header),
                                            namespaces=self.namespace)[0], "stixVocabs:PackageIntentVocab-1.0")

    def test_package_intent_text(self):
        self.assertEqual(self.output1.xpath("{} stix:Package_Intent/text()".format(self.header),
                                            namespaces=self.namespace)[0], "Indicators")

    def test_controlled_structure_text(self):
        self.assertEqual(self.output1.xpath("{} marking:Controlled_Structure/text()".format(self.marking),
                                            namespaces=self.namespace), ["//node() | //@*"])

    def test_indicator_timestamp(self):
        test = self.output1.xpath("{} @timestamp".format(self.indicator), namespaces=self.namespace)[0]
        if(test == self.utc_before):
            self.assertEqual(test, self.utc_before)
        else:
            self.assertEqual(test, self.utc_after)

    def test_acs_type(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@xsi:type".format(self.marking),
                                                namespaces=self.namespace)), set(["edh2cyberMarking:ISAMarkingsType",
                                                                                  "edh2cyberMarkingAssert:ISAMarkingsAssertionType"]))

    def test_acs_version(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@isam_version".format(self.marking),
                                                namespaces=self.namespace)), set(["1.0"]))

    def test_acs_most_restriction(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure/@most_restrictive".format(self.marking),
                                                namespaces=self.namespace)), set(["true"]))

    def test_responsible_enity(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarking:ISAMarkingsType']/edh2:ResponsibleEntity/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CUST:USA.DOE"]))

    def test_policy_ref(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:PolicyRef/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["urn:isa:policy:acs:ns:v2.0?privdefault=permit"]))

    def test_control_set(self):
        self.assertEqual(set(self.output1.xpath("{} marking:Marking_Structure[@xsi:type='edh2cyberMarkingAssert:ISAMarkingsAssertionType']/edh2:ControlSet/text()".format(self.marking),
                                                namespaces=self.namespace)), set(["CLS:U CUI:FOUO"]))

if __name__ == '__main__':
    unittest.main()