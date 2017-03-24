import io
import os
import unittest
import json
import arrow

from FlexTransform.test.SampleInputs import CFM20ALERT, CFM13ALERT, STIXTLP
from FlexTransform import FlexTransform


@unittest.skip
class TestCFM13AlertToLQMT(unittest.TestCase):
    output1 = None
    output2 = None
    json_file = None
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
            #transform.AddParser('cfm13alert', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            #transform.AddParser('lqmtools', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('lqmtools', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm20alert.cfg'), 'r') as input_file:
            #transform.AddParser('cfm20alert', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('cfm20alert', input_file)
        output1_object = io.StringIO()
        output2_object = io.StringIO()

        #transform.TransformFile(io.StringIO(CFM13ALERT), 'cfm13alert', 'lqmtools', targetFileName=output1_object) Used for master branch since it still uses TransformFile & targetFileName= (3/22/2017)
        transform.transform(io.StringIO(CFM13ALERT), 'cfm13alert', 'lqmtools', target_file=output1_object)
        #transform.TransformFile(io.StringIO(CFM20ALERT), 'cfm20alert', 'lqmtools', targetFileName=output2_object) Used for master branch since it still uses TransformFile & targetFileName= (3/22/2017)
        transform.transform(io.StringIO(CFM20ALERT), 'cfm20alert', 'lqmtools', target_file=output2_object)
        output1_object.seek(0)
        output1_object.readline()
        output2_object.seek(0)
        output2_object.readline()
        # print(output1_object.getvalue())
        cls.json_file = output1_object.getvalue()
        cls.json_file2 = output2_object.getvalue()

    # CFM13 format tests
    # def test_cfm13_content_returned(self):
    #     self.assertEqual(len(self.cfm13_parsed_data), 1)

    def test_cfm13_indicator(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['indicator'], '10.10.10.10')

    # def test_cfm13_indicator(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._indicator, "10.10.10.10")

    def test_cfm13_inidcator_type(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['indicatorType'], 'IPv4Address')

    # def test_cfm13_indicator_type(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._indicatorType, "IPv4Address")

    def test_cfm13_action1(self):
       decoded = json.loads(self.json_file)
       self.assertEqual(decoded[0]['action1'], 'Block')

    # def test_cfm13_action(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._action1, "Block")

    def test_cfm13_detectedTime(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['detectedTime'], 1456109153) #14561163.0

    # def test_cfm13_detectedTime(self):
    #     pass
    #     # self.assertEquals(self.cfm13_parsed_data[0]._detectedTime, 1456116353.0)

    def test_cfm13_duration(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['duration1'], '86400')
        # self.assertIsNone(decoded[0]['duration2'], '86400')

    # def test_cfm13_duration(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._duration1, "86400")
    #     self.assertIsNone(self.cfm13_parsed_data[0]._duration2, "86400")

    def test_cfm13_sensitivity(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['sensitivity'], 'noSensitivity')

    # def test_cfm13_sensitivity(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._sensitivity, "noSensitivity")

    def test_cfm13_restriction(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['restriction'], 'AMBER')

    #Added from Sean's Test

    def test_cfm13_directSource(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['directSource'], 'Fake')

    def test_cfm13_recon(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['reconAllowed'], '1')

    def test_cfm13_reason(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['reason1'], 'SSH Attack')

    def test_cfm13_majorTags(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['majorTags'], 'Scanning')

    # def test_cfm13_processedTime(self):
    #     decoded = json.loads(self.json_file)
    #     self.assertEqual(decoded[0]['processedTime'], (gets current time)) # 1489087521

    def test_cfm13_prior(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['priors'], '11')

    # def test_cfm13_restriction(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._restriction, "AMBER")

    def test_cfm13_comment(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['comment'], 'SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high')

    def test_cfm13_fileHasMore(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['fileHasMore'], '0')

    def test_cfm13_reference(self):
        decoded = json.loads(self.json_file)
        self.assertEqual(decoded[0]['reference1'], 'user-specific')





    # # CFM20 format tests

    def test_cfm20_indicator(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['indicator'], '8675:a289:5:102c::bd8:baac')

    # def test_cfm20_content_returned(self):
    #     self.assertEquals(len(self.cfm20_parsed_data), 1)
    #
    # def test_cfm20_indicator(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._indicator, "8675:a289:5:102c::bd8:baac")

    def test_cfm20_indicator_type(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['indicatorType'], 'IPv6Address')

    # def test_cfm20_indicator_type(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._indicatorType, "IPv6Address")

    def test_cfm20_action(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['action1'], 'Block')

    # def test_cfm20_action(self):
    #     self.assertEquals(self.cfm13_parsed_data[0]._action1, "Block")

    def test_cfm20_detectedTime(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['detectedTime'], 1468350602)

    # def test_cfm20_detectedTime(self):
    #     pass

    def test_cfm20_duration(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['duration1'], '86400')

    # def test_cfm20_duration(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._duration1, "86400")
    #     self.assertIsNone(self.cfm20_parsed_data[0]._duration2)

    def test_cfm20_sensitivity(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['sensitivity'], 'noSensitivity')

    # def test_cfm20_sensitivity(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._sensitivity, "noSensitivity")

    # def test_cfm20_restriction(self):
    #     decoded = json.loads(self.json_file2)
    #     self.assertIsNone(decoded['restriction'])

    # def test_cfm20_restriction(self):
    #     self.assertIsNone(self.cfm20_parsed_data[0]._restriction)

    # Added

    def test_cfm20_comment(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['comment'], 'The WAF detected a scan for vulnerable web applications')

    def test_cfm20_dataItemID(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['dataItemID'], '1cdf6f8f-20da-488e-9132-bbf850621418')

    def test_cfm20_fileHasMore(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['fileHasMore'], '0')

    def test_cfm20_reason(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['reason1'], 'Exploit')

    def test_cfm20_recon(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['reconAllowed'], '1')

    def test_cfm20_majorTags(self):
        decoded = json.loads(self.json_file2)
        self.assertEqual(decoded[0]['majorTags'], 'Exploit')



class STIXTLPtoLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
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
            # transform.AddParser('cfm13alert', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('stixtlp', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            # transform.AddParser('lqmtools', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(STIXTLP), 'stixtlp', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()


    def test_stixtlp_entry0(self):
        decoded = json.loads(self.json_file)
        utc_now = int(decoded[0]['processedTime'])
        self.assertEqual(decoded[0]['action1'], 'Block')
        self.assertEqual(decoded[0]['comment'], 'CRISP Report Indicator')
        self.assertEqual(decoded[0]['dataItemID'], 'CFM:Indicator-3e732203-d463-50ba-b6c2-26c11032a204')
        self.assertEqual(decoded[0]['detectedTime'], 1458737105)
        self.assertEqual(decoded[0]['directSource'], 'Fake')
        self.assertEqual(decoded[0]['duration1'], '86400')
        self.assertEqual(decoded[0]['fileHasMore'], '0')
        self.assertEqual(decoded[0]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(decoded[0]['indicator'], '10.10.10.10')
        self.assertEqual(decoded[0]['indicatorType'], 'IPv4Address')
        self.assertEqual(decoded[0]['reconAllowed'], '1')
        self.assertEqual(decoded[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= int(utc_now) and int(utc_now) <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")


    def test_stixtlp_entry1(self):
        decoded = json.loads(self.json_file)
        utc_now = int(decoded[1]['processedTime'])
        self.assertEqual(decoded[1]['action1'], 'Block')
        self.assertEqual(decoded[1]['comment'], 'CRISP Report Indicator')
        self.assertEqual(decoded[1]['dataItemID'], 'CFM:Indicator-82b0c3f9-95d4-5ec7-9e09-30b0bf87cfcd')
        self.assertEqual(decoded[1]['detectedTime'], 1458737105)
        self.assertEqual(decoded[1]['directSource'], 'Fake')
        self.assertEqual(decoded[1]['duration1'], '86400')
        self.assertEqual(decoded[1]['fileHasMore'], '0')
        self.assertEqual(decoded[1]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(decoded[1]['indicator'], '13.13.13.13')
        self.assertEqual(decoded[1]['indicatorType'], 'IPv4Address')
        self.assertEqual(decoded[1]['reconAllowed'], '1')
        self.assertEqual(decoded[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= int(utc_now) and int(utc_now) <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")


    def test_stixtlp_entry2(self):
        decoded = json.loads(self.json_file)
        utc_now = int(decoded[2]['processedTime'])
        self.assertEqual(decoded[2]['action1'], 'Block')
        self.assertEqual(decoded[2]['comment'], 'CRISP Report Indicator')
        self.assertEqual(decoded[2]['dataItemID'], 'CFM:Indicator-52c46f7c-cca9-5d2e-9d3b-a3b1744dcf52')
        self.assertEqual(decoded[2]['detectedTime'], 1458737105)
        self.assertEqual(decoded[2]['directSource'], 'Fake')
        self.assertEqual(decoded[2]['duration1'], '86400')
        self.assertEqual(decoded[2]['fileHasMore'], '0')
        self.assertEqual(decoded[2]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(decoded[2]['indicator'], '12.12.12.12')
        self.assertEqual(decoded[2]['indicatorType'], 'IPv4Address')
        self.assertEqual(decoded[2]['reconAllowed'], '1')
        self.assertEqual(decoded[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= int(utc_now) and int(utc_now) <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")


    def test_stixtlp_entry3(self):
        decoded = json.loads(self.json_file)
        utc_now = int(decoded[3]['processedTime'])
        self.assertEqual(decoded[3]['action1'], 'Block')
        self.assertEqual(decoded[3]['comment'], 'CRISP Report Indicator')
        self.assertEqual(decoded[3]['dataItemID'], 'CFM:Indicator-052c65e0-c667-5e4c-9970-ac9ddd3511b3')
        self.assertEqual(decoded[3]['detectedTime'], 1458737105)
        self.assertEqual(decoded[3]['directSource'], 'Fake')
        self.assertEqual(decoded[3]['duration1'], '86400')
        self.assertEqual(decoded[3]['fileHasMore'], '0')
        self.assertEqual(decoded[3]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(decoded[3]['indicator'], '11.11.11.11')
        self.assertEqual(decoded[3]['indicatorType'], 'IPv4Address')
        self.assertEqual(decoded[3]['reconAllowed'], '1')
        self.assertEqual(decoded[3]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= int(utc_now) and int(utc_now) <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 3.")


    def test_stixtlp_entry4(self):
        decoded = json.loads(self.json_file)
        utc_now = int(decoded[4]['processedTime'])
        self.assertEqual(decoded[4]['action1'], 'Block')
        self.assertEqual(decoded[4]['comment'], 'CRISP Report Indicator')
        self.assertEqual(decoded[4]['dataItemID'], 'CFM:Indicator-1cf2d34d-007a-5a50-b7c1-cce9faf6f968')
        self.assertEqual(decoded[4]['detectedTime'], 1458737105)
        self.assertEqual(decoded[4]['directSource'], 'Fake')
        self.assertEqual(decoded[4]['duration1'], '86400')
        self.assertEqual(decoded[4]['fileHasMore'], '0')
        self.assertEqual(decoded[4]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(decoded[4]['indicator'], '14.14.14.14')
        self.assertEqual(decoded[4]['indicatorType'], 'IPv4Address')
        self.assertEqual(decoded[4]['reconAllowed'], '1')
        self.assertEqual(decoded[4]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= int(utc_now) and int(utc_now) <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 4.")


    def test_stixtlp_entry5(self):
        decoded = json.loads(self.json_file)
        utc_now = int(decoded[5]['processedTime'])
        self.assertEqual(decoded[5]['action1'], 'Block')
        self.assertEqual(decoded[5]['comment'], 'CRISP Report Indicator')
        self.assertEqual(decoded[5]['dataItemID'], 'CFM:Indicator-2e95d2ac-1b08-5f38-8522-2f4b2ef3686c')
        self.assertEqual(decoded[5]['detectedTime'], 1458737105)
        self.assertEqual(decoded[5]['directSource'], 'Fake')
        self.assertEqual(decoded[5]['duration1'], '86400')
        self.assertEqual(decoded[5]['fileHasMore'], '0')
        self.assertEqual(decoded[5]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(decoded[5]['indicator'], 'bad.domain.be/poor/path')
        self.assertEqual(decoded[5]['indicatorType'], 'URL')
        self.assertEqual(decoded[5]['reconAllowed'], '1')
        self.assertEqual(decoded[5]['secondaryIndicatorType'], 'URL')
        self.assertEqual(decoded[5]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= int(utc_now) and int(utc_now) <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 5.")


    def test_stixtlp_entry6(self):
        decoded = json.loads(self.json_file)
        utc_now = int(decoded[6]['processedTime'])
        self.assertEqual(decoded[6]['action1'], 'Block')
        self.assertEqual(decoded[6]['comment'], 'CRISP Report Indicator')
        self.assertEqual(decoded[6]['dataItemID'], 'CFM:Indicator-5fd6c616-d923-5e70-916d-dca3a2d1ee02')
        self.assertEqual(decoded[6]['detectedTime'], 1458737105)
        self.assertEqual(decoded[6]['directSource'], 'Fake')
        self.assertEqual(decoded[6]['duration1'], '86400')
        self.assertEqual(decoded[6]['fileHasMore'], '0')
        self.assertEqual(decoded[6]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(decoded[6]['indicator'], 'fake.site.com/malicious.js')
        self.assertEqual(decoded[6]['indicatorType'], 'URL')
        self.assertEqual(decoded[6]['reconAllowed'], '1')
        self.assertEqual(decoded[6]['secondaryIndicatorType'], 'URL')
        self.assertEqual(decoded[6]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= int(utc_now) and int(utc_now) <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 6.")


if __name__ == '__main__':
    unittest.main()