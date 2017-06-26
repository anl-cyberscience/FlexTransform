import io
import os
import unittest
import json
import arrow
import csv

from FlexTransform.test.SampleInputs import CFM20ALERT, CFM13ALERT, STIXTLP, STIXACS, KEYVALUE, IIDCOMBINEDRECENT, IIDACTIVEBADHOST, IIDDYNAMICBADHOST, IIDBADIPV4
from FlexTransform import FlexTransform
from FlexTransform.test.utils import dynamic_time_change


class TestCFM13AlertToLQMT(unittest.TestCase):
    output1 = None
    output2 = None
    json_file = None
    decoded_cfm13_1 = None
    decoded_cfm13_2 = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            # transform.AddParser('cfm13alert', input_file)
            # Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('cfm13alert', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            # transform.AddParser('lqmtools', input_file)
            # Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('lqmtools', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/cfm20alert.cfg'), 'r') as input_file:
            # transform.AddParser('cfm20alert', input_file)
            # Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('cfm20alert', input_file)
        output1_object = io.StringIO()
        output2_object = io.StringIO()

        # transform.TransformFile(io.StringIO(CFM13ALERT), 'cfm13alert', 'lqmtools', targetFileName=output1_object)
        # Used for master branch since it still uses TransformFile & targetFileName= (3/22/2017)
        transform.transform(io.StringIO(CFM13ALERT), 'cfm13alert', 'lqmtools', target_file=output1_object)
        # transform.TransformFile(io.StringIO(CFM20ALERT), 'cfm20alert', 'lqmtools', targetFileName=output2_object)
        # Used for master branch since it still uses TransformFile & targetFileName= (3/22/2017)
        transform.transform(io.StringIO(CFM20ALERT), 'cfm20alert', 'lqmtools', target_file=output2_object)
        output1_object.seek(0)
        output1_object.readline()
        output2_object.seek(0)
        output2_object.readline()
        # print(output1_object.getvalue())
        cls.json_file = output1_object.getvalue()
        cls.json_file2 = output2_object.getvalue()

        cls.decoded_cfm13_1 = json.loads(cls.json_file)
        cls.decoded_cfm13_2 = json.loads(cls.json_file2)

    # CFM13 format tests
    # def test_cfm13_content_returned(self):
    #     self.assertEqual(len(self.cfm13_parsed_data), 1)

    def test_cfm13_indicator(self):
        self.assertEqual(self.decoded_cfm13_1[0]['indicator'], '10.10.10.10')

    # def test_cfm13_indicator(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._indicator, "10.10.10.10")

    def test_cfm13_inidcator_type(self):
        self.assertEqual(self.decoded_cfm13_1[0]['indicatorType'], 'IPv4Address')

    # def test_cfm13_indicator_type(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._indicatorType, "IPv4Address")

    def test_cfm13_action1(self):
        self.assertEqual(self.decoded_cfm13_1[0]['action1'], 'Block')

    # def test_cfm13_action(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._action1, "Block")

    def test_cfm13_detectedTime(self):
        self.assertEqual(self.decoded_cfm13_1[0]['detectedTime'], '1456109153')  # 14561163.0

    # def test_cfm13_detectedTime(self):
    #     pass
    #     # self.assertEquals(self.cfm13_parsed_data[0]._detectedTime, 1456116353.0)

    def test_cfm13_duration(self):
        self.assertEqual(self.decoded_cfm13_1[0]['duration1'], '86400')
        # self.assertIsNone(self.decoded[0]['duration2'], '86400')

    # def test_cfm13_duration(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._duration1, "86400")
    #     self.assertIsNone(self.cfm13_parsed_data[0]._duration2, "86400")

    def test_cfm13_sensitivity(self):
        self.assertEqual(self.decoded_cfm13_1[0]['sensitivity'], 'noSensitivity')

    # def test_cfm13_sensitivity(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._sensitivity, "noSensitivity")

    def test_cfm13_restriction(self):
        self.assertEqual(self.decoded_cfm13_1[0]['restriction'], 'AMBER')

    # Added from Sean's Test

    def test_cfm13_directSource(self):
        self.assertEqual(self.decoded_cfm13_1[0]['directSource'], 'Fake')

    def test_cfm13_recon(self):
        self.assertEqual(self.decoded_cfm13_1[0]['reconAllowed'], '1')

    def test_cfm13_reason(self):
        self.assertEqual(self.decoded_cfm13_1[0]['reason1'], 'SSH Attack')

    def test_cfm13_majorTags(self):
        self.assertEqual(self.decoded_cfm13_1[0]['majorTags'], 'Scanning')

    # def test_cfm13_processedTime(self):
    #     decoded = json.loads(self.json_file)
    #     self.assertEqual(self.decoded[0]['processedTime'], (gets current time)) # 1489087521

    def test_cfm13_prior(self):
        self.assertEqual(self.decoded_cfm13_1[0]['priors'], '11')

    # def test_cfm13_restriction(self):
    #     self.assertEqual(self.cfm13_parsed_data[0]._restriction, "AMBER")

    def test_cfm13_comment(self):
        self.assertEqual(self.decoded_cfm13_1[0]['comment'],
                         'SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high')

    def test_cfm13_fileHasMore(self):
        self.assertEqual(self.decoded_cfm13_1[0]['fileHasMore'], '0')

    def test_cfm13_reference(self):
        self.assertEqual(self.decoded_cfm13_1[0]['reference1'], 'user-specific')

    # CFM20 format tests

    def test_cfm20_indicator(self):
        self.assertEqual(self.decoded_cfm13_2[0]['indicator'], '8675:a289:5:102c::bd8:baac')

    # def test_cfm20_content_returned(self):
    #     self.assertEquals(len(self.cfm20_parsed_data), 1)
    #
    # def test_cfm20_indicator(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._indicator, "8675:a289:5:102c::bd8:baac")

    def test_cfm20_indicator_type(self):
        self.assertEqual(self.decoded_cfm13_2[0]['indicatorType'], 'IPv6Address')

    # def test_cfm20_indicator_type(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._indicatorType, "IPv6Address")

    def test_cfm20_action(self):
        self.assertEqual(self.decoded_cfm13_2[0]['action1'], 'Block')

    # def test_cfm20_action(self):
    #     self.assertEquals(self.cfm13_parsed_data[0]._action1, "Block")

    def test_cfm20_detectedTime(self):
        self.assertEqual(self.decoded_cfm13_2[0]['detectedTime'], '1468350602')

    # def test_cfm20_detectedTime(self):
    #     pass

    def test_cfm20_duration(self):
        self.assertEqual(self.decoded_cfm13_2[0]['duration1'], '86400')

    # def test_cfm20_duration(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._duration1, "86400")
    #     self.assertIsNone(self.cfm20_parsed_data[0]._duration2)

    def test_cfm20_sensitivity(self):
        self.assertEqual(self.decoded_cfm13_2[0]['sensitivity'], 'noSensitivity')

    # def test_cfm20_sensitivity(self):
    #     self.assertEquals(self.cfm20_parsed_data[0]._sensitivity, "noSensitivity")

    # def test_cfm20_restriction(self):
    #     decoded = json.loads(self.json_file2)
    #     self.assertIsNone(self.decoded['restriction'])

    # def test_cfm20_restriction(self):
    #     self.assertIsNone(self.cfm20_parsed_data[0]._restriction)

    # Added

    def test_cfm20_comment(self):
        self.assertEqual(self.decoded_cfm13_2[0]['comment'], 'The WAF detected a scan for vulnerable web applications')

    def test_cfm20_dataItemID(self):
        self.assertEqual(self.decoded_cfm13_2[0]['dataItemID'], '1cdf6f8f-20da-488e-9132-bbf850621418')

    def test_cfm20_fileHasMore(self):
        self.assertEqual(self.decoded_cfm13_2[0]['fileHasMore'], '0')

    def test_cfm20_reason(self):
        self.assertEqual(self.decoded_cfm13_2[0]['reason1'], 'Exploit')

    def test_cfm20_recon(self):
        self.assertEqual(self.decoded_cfm13_2[0]['reconAllowed'], '1')

    def test_cfm20_majorTags(self):
        self.assertEqual(self.decoded_cfm13_2[0]['majorTags'], 'Exploit')


class TestSTIXTLPToLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_tlp = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_tlp.cfg'), 'r') as input_file:
            # transform.AddParser('cfm13alert', input_file)
            # Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('stix_tlp', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            # transform.AddParser('lqmtools', input_file)
            # Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(STIXTLP), 'stix_tlp', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_tlp = json.loads(cls.json_file)

    def test_stixtlp_entry0(self):
        utc_now = int(self.decoded_tlp[0]['processedTime'])
        self.assertEqual(self.decoded_tlp[0]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[0]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[0]['dataItemID'], 'CFM:Indicator-3e732203-d463-50ba-b6c2-26c11032a204')
        self.assertEqual(self.decoded_tlp[0]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[0]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[0]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[0]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[0]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[0]['indicator'], '10.10.10.10')
        self.assertEqual(self.decoded_tlp[0]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[0]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    def test_stixtlp_entry1(self):
        utc_now = int(self.decoded_tlp[1]['processedTime'])
        self.assertEqual(self.decoded_tlp[1]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[1]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[1]['dataItemID'], 'CFM:Indicator-82b0c3f9-95d4-5ec7-9e09-30b0bf87cfcd')
        self.assertEqual(self.decoded_tlp[1]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[1]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[1]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[1]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[1]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[1]['indicator'], '13.13.13.13')
        self.assertEqual(self.decoded_tlp[1]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[1]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    def test_stixtlp_entry2(self):
        utc_now = int(self.decoded_tlp[2]['processedTime'])
        self.assertEqual(self.decoded_tlp[2]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[2]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[2]['dataItemID'], 'CFM:Indicator-52c46f7c-cca9-5d2e-9d3b-a3b1744dcf52')
        self.assertEqual(self.decoded_tlp[2]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[2]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[2]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[2]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[2]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[2]['indicator'], '12.12.12.12')
        self.assertEqual(self.decoded_tlp[2]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[2]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")

    def test_stixtlp_entry3(self):
        utc_now = int(self.decoded_tlp[3]['processedTime'])
        self.assertEqual(self.decoded_tlp[3]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[3]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[3]['dataItemID'], 'CFM:Indicator-052c65e0-c667-5e4c-9970-ac9ddd3511b3')
        self.assertEqual(self.decoded_tlp[3]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[3]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[3]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[3]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[3]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[3]['indicator'], '11.11.11.11')
        self.assertEqual(self.decoded_tlp[3]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[3]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[3]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 3.")

    def test_stixtlp_entry4(self):
        utc_now = int(self.decoded_tlp[4]['processedTime'])
        self.assertEqual(self.decoded_tlp[4]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[4]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[4]['dataItemID'], 'CFM:Indicator-1cf2d34d-007a-5a50-b7c1-cce9faf6f968')
        self.assertEqual(self.decoded_tlp[4]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[4]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[4]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[4]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[4]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[4]['indicator'], '14.14.14.14')
        self.assertEqual(self.decoded_tlp[4]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[4]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[4]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 4.")
    
    def test_stixtlp_entry5(self):
        utc_now = int(self.decoded_tlp[5]['processedTime'])
        self.assertEqual(self.decoded_tlp[5]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[5]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[5]['dataItemID'], 'CFM:Indicator-92130d2c-c3e6-5ed9-bcdc-c826c5d2c5b4')
        self.assertEqual(self.decoded_tlp[5]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[5]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[5]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[5]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[5]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[5]['indicator'], 'D://replacement.exe')
        self.assertEqual(self.decoded_tlp[5]['indicatorType'], 'FilePath')
        self.assertEqual(self.decoded_tlp[5]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[5]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 6.")
    
    def test_stixtlp_entry6(self):
        utc_now = int(self.decoded_tlp[6]['processedTime'])
        self.assertEqual(self.decoded_tlp[6]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[6]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[6]['dataItemID'], 'CFM:Indicator-1bed1aca-30e1-5ad3-8bee-6c1dfbff157d')
        self.assertEqual(self.decoded_tlp[6]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[6]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[6]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[6]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[6]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[6]['indicator'], '/user/strange/object.sh')
        self.assertEqual(self.decoded_tlp[6]['indicatorType'], 'FilePath')
        self.assertEqual(self.decoded_tlp[6]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[6]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 6.")
    
    def test_stixtlp_entry7(self):
        utc_now = int(self.decoded_tlp[7]['processedTime'])
        self.assertEqual(self.decoded_tlp[7]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[7]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[7]['dataItemID'], 'CFM:Indicator-8b3ac40a-8595-50fe-bea1-fbd1d85cc428')
        self.assertEqual(self.decoded_tlp[7]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[7]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[7]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[7]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[7]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[7]['indicator'], 'C://window32/tst.dat')
        self.assertEqual(self.decoded_tlp[7]['indicatorType'], 'FilePath')
        self.assertEqual(self.decoded_tlp[7]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[7]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 7.")
    
    def test_stixtlp_entry8(self):
        utc_now = int(self.decoded_tlp[8]['processedTime'])
        self.assertEqual(self.decoded_tlp[8]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[8]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[8]['dataItemID'], 'CFM:Indicator-a9b071be-fa18-5b49-9d15-e487836adb49')
        self.assertEqual(self.decoded_tlp[8]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[8]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[8]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[8]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[8]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[8]['indicator'], 'webmail.p55.be')
        self.assertEqual(self.decoded_tlp[8]['indicatorType'], 'FilePath')
        self.assertEqual(self.decoded_tlp[8]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[8]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 8.")
        
    def test_stixtlp_entry9(self):
        utc_now = int(self.decoded_tlp[9]['processedTime'])
        self.assertEqual(self.decoded_tlp[9]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[9]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[9]['dataItemID'], 'CFM:Indicator-2e95d2ac-1b08-5f38-8522-2f4b2ef3686c')
        self.assertEqual(self.decoded_tlp[9]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[9]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[9]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[9]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[9]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[9]['indicator'], 'bad.domain.be/poor/path')
        self.assertEqual(self.decoded_tlp[9]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[9]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[9]['secondaryIndicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[9]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 9.")

    def test_stixtlp_entry10(self):
        utc_now = int(self.decoded_tlp[10]['processedTime'])
        self.assertEqual(self.decoded_tlp[10]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[10]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[10]['dataItemID'], 'CFM:Indicator-5fd6c616-d923-5e70-916d-dca3a2d1ee02')
        self.assertEqual(self.decoded_tlp[10]['detectedTime'], '1458737105')
        self.assertEqual(self.decoded_tlp[10]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[10]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[10]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[10]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[10]['indicator'], 'fake.site.com/malicious.js')
        self.assertEqual(self.decoded_tlp[10]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[10]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[10]['secondaryIndicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[10]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 10.")


class TestSTIXACSToLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_acs = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_essa.cfg'), 'r') as input_file:
            transform.add_parser('stix_acs', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(STIXACS), 'stix_acs', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_acs = json.loads(cls.json_file)

    def test_stixacs_entry0(self):
        utc_now = int(self.decoded_acs[0]['processedTime'])
        self.assertEqual(self.decoded_acs[0]['action1'], 'Block')
        self.assertEqual(self.decoded_acs[0]['comment'], 'AAA Report Indicator')
        self.assertEqual(self.decoded_acs[0]['dataItemID'],
                         'isa:guide.999191.Indicator-3312fec8-9504-51ad-bd9f-e43017af4a10')
        self.assertEqual(self.decoded_acs[0]['duration1'], '86400')
        self.assertEqual(self.decoded_acs[0]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs[0]['fileID'],
                         'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs[0]['indicator'], 'blog.website.net')
        self.assertEqual(self.decoded_acs[0]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs[0]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    def test_stixacs_entry1(self):
        utc_now = int(self.decoded_acs[1]['processedTime'])
        self.assertEqual(self.decoded_acs[1]['action1'], 'Block')
        self.assertEqual(self.decoded_acs[1]['comment'], 'Domain Indicator')
        self.assertEqual(self.decoded_acs[1]['dataItemID'],
                         'isa:guide.999191.Indicator-60742920-231d-508d-8f75-d361f24a5fb0')
        self.assertEqual(self.decoded_acs[1]['duration1'], '86400')
        self.assertEqual(self.decoded_acs[1]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs[1]['fileID'],
                         'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs[1]['indicator'], 'fake.com')
        self.assertEqual(self.decoded_acs[1]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs[1]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    def test_stixacs_entry2(self):
        utc_now = int(self.decoded_acs[2]['processedTime'])
        self.assertEqual(self.decoded_acs[2]['action1'], 'Block')
        self.assertEqual(self.decoded_acs[2]['comment'], 'Just Another Indicator')
        self.assertEqual(self.decoded_acs[2]['dataItemID'],
                         'isa:guide.999191.Indicator-f2911c1d-a14d-50de-a211-33a8beb7c7e6')
        self.assertEqual(self.decoded_acs[2]['duration1'], '86400')
        self.assertEqual(self.decoded_acs[2]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs[2]['fileID'],
                         'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs[2]['indicator'], 'goo.gl/peter')
        self.assertEqual(self.decoded_acs[2]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs[2]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")


class TestSTIXACS30ToLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_acs30 = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/stix_acs30.cfg'), 'r') as input_file:
            transform.add_parser('stix_acs30', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(STIXACS), 'stix_acs30', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_acs30 = json.loads(cls.json_file)

    def test_stixacs30_entry0(self):
        utc_now = int(self.decoded_acs30[0]['processedTime'])
        self.assertEqual(self.decoded_acs30[0]['action1'], 'Block')
        self.assertEqual(self.decoded_acs30[0]['comment'], 'AAA Report Indicator')
        self.assertEqual(self.decoded_acs30[0]['dataItemID'],
                         'isa:guide.999191.Indicator-3312fec8-9504-51ad-bd9f-e43017af4a10')
        self.assertEqual(self.decoded_acs30[0]['duration1'], '86400')
        self.assertEqual(self.decoded_acs30[0]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs30[0]['fileID'],
                         'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs30[0]['indicator'], 'blog.website.net')
        self.assertEqual(self.decoded_acs30[0]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs30[0]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs30[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    def test_stixacs30_entry1(self):
        utc_now = int(self.decoded_acs30[1]['processedTime'])
        self.assertEqual(self.decoded_acs30[1]['action1'], 'Block')
        self.assertEqual(self.decoded_acs30[1]['comment'], 'Domain Indicator')
        self.assertEqual(self.decoded_acs30[1]['dataItemID'],
                         'isa:guide.999191.Indicator-60742920-231d-508d-8f75-d361f24a5fb0')
        self.assertEqual(self.decoded_acs30[1]['duration1'], '86400')
        self.assertEqual(self.decoded_acs30[1]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs30[1]['fileID'],
                         'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs30[1]['indicator'], 'fake.com')
        self.assertEqual(self.decoded_acs30[1]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs30[1]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs30[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    def test_stixacs30_entry2(self):
        utc_now = int(self.decoded_acs30[2]['processedTime'])
        self.assertEqual(self.decoded_acs30[2]['action1'], 'Block')
        self.assertEqual(self.decoded_acs30[2]['comment'], 'Just Another Indicator')
        self.assertEqual(self.decoded_acs30[2]['dataItemID'],
                         'isa:guide.999191.Indicator-f2911c1d-a14d-50de-a211-33a8beb7c7e6')
        self.assertEqual(self.decoded_acs30[2]['duration1'], '86400')
        self.assertEqual(self.decoded_acs30[2]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs30[2]['fileID'],
                         'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs30[2]['indicator'], 'goo.gl/peter')
        self.assertEqual(self.decoded_acs30[2]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs30[2]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs30[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")


class TestKeyValueToLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_keyvalue = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/keyvalue.cfg'), 'r') as input_file:
            transform.add_parser('keyvalue', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(KEYVALUE), 'keyvalue', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_keyvalue = json.loads(cls.json_file)

    def test_keyvalue_entry0(self):
        utc_now = int(self.decoded_keyvalue[0]['processedTime'])
        self.assertEqual(self.decoded_keyvalue[0]['action1'], 'Block')
        self.assertEqual(self.decoded_keyvalue[0]['comment'],
                         'Attacker scanning for RDP, direction:ingress, confidence:0, severity:high')
        self.assertEqual(self.decoded_keyvalue[0]['detectedTime'], '1325401200')
        self.assertEqual(self.decoded_keyvalue[0]['duration1'], '86400')
        self.assertEqual(self.decoded_keyvalue[0]['fileHasMore'], '0')
        self.assertEqual(self.decoded_keyvalue[0]['majorTags'], 'Scanning')
        self.assertEqual(self.decoded_keyvalue[0]['reason1'], 'Scanning')
        self.assertEqual(self.decoded_keyvalue[0]['indicator'], '10.11.12.13')
        self.assertEqual(self.decoded_keyvalue[0]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_keyvalue[0]['reconAllowed'], '1')
        self.assertEqual(self.decoded_keyvalue[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    def test_keyvalue_entry1(self):
        utc_now = int(self.decoded_keyvalue[1]['processedTime'])
        self.assertEqual(self.decoded_keyvalue[1]['action1'], 'Block')
        self.assertEqual(self.decoded_keyvalue[1]['comment'],
                         'Attacker scanning for SSH, direction:ingress, confidence:0, severity:high')
        self.assertEqual(self.decoded_keyvalue[1]['detectedTime'], '1325401200')
        self.assertEqual(self.decoded_keyvalue[1]['duration1'], '86400')
        self.assertEqual(self.decoded_keyvalue[1]['fileHasMore'], '0')
        self.assertEqual(self.decoded_keyvalue[1]['majorTags'], 'Scanning')
        self.assertEqual(self.decoded_keyvalue[1]['reason1'], 'Scanning')
        self.assertEqual(self.decoded_keyvalue[1]['indicator'], '10.11.12.14')
        self.assertEqual(self.decoded_keyvalue[1]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_keyvalue[1]['reconAllowed'], '1')
        self.assertEqual(self.decoded_keyvalue[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    def test_keyvalue_entry2(self):
        utc_now = int(self.decoded_keyvalue[2]['processedTime'])
        self.assertEqual(self.decoded_keyvalue[2]['action1'], 'Block')
        self.assertEqual(self.decoded_keyvalue[2]['comment'],
                         'HTTP Response code 4xx, suspicious, direction:ingress, confidence:0, severity:low')
        self.assertEqual(self.decoded_keyvalue[2]['detectedTime'], '1325401200')
        self.assertEqual(self.decoded_keyvalue[2]['duration1'], '86400')
        self.assertEqual(self.decoded_keyvalue[2]['fileHasMore'], '0')
        self.assertEqual(self.decoded_keyvalue[2]['majorTags'], 'Reconnaissance')
        self.assertEqual(self.decoded_keyvalue[2]['reason1'], 'Reconnaissance')
        self.assertEqual(self.decoded_keyvalue[2]['indicator'], '2001:db8:16::1')
        self.assertEqual(self.decoded_keyvalue[2]['indicatorType'], 'IPv6Address')
        self.assertEqual(self.decoded_keyvalue[2]['reconAllowed'], '1')
        self.assertEqual(self.decoded_keyvalue[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")

    def test_keyvalue_entry3(self):
        utc_now = int(self.decoded_keyvalue[3]['processedTime'])
        self.assertEqual(self.decoded_keyvalue[3]['action1'], 'Block')
        self.assertEqual(self.decoded_keyvalue[3]['comment'],
                         'Malicious domain, direction:egress, confidence:0, severity:high')
        self.assertEqual(self.decoded_keyvalue[3]['detectedTime'], '1325401200')
        self.assertEqual(self.decoded_keyvalue[3]['duration1'], '86400')
        self.assertEqual(self.decoded_keyvalue[3]['fileHasMore'], '0')
        self.assertEqual(self.decoded_keyvalue[3]['majorTags'], 'Malware Traffic')
        self.assertEqual(self.decoded_keyvalue[3]['reason1'], 'Malware Traffic')
        self.assertEqual(self.decoded_keyvalue[3]['indicator'], 'bad.domain')
        self.assertEqual(self.decoded_keyvalue[3]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_keyvalue[3]['reconAllowed'], '1')
        self.assertEqual(self.decoded_keyvalue[3]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 3.")

class TestIIDCombinedRecentToLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_combinedRecent = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_combined_recent.cfg'), 'r') as input_file:
            transform.add_parser('iid_combined_recent', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(IIDCOMBINEDRECENT), 'iid_combined_recent', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_combinedRecent = json.loads(cls.json_file)

    def test_iidcombinedrecent_entry0(self):
        utc_now = int(self.decoded_combinedRecent[0]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[0]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[0]['comment'], 'Phishing, ABSA BANK')
        self.assertEqual(self.decoded_combinedRecent[0]['indicator'], 'http://79.96.154.154/Porigin/imgs/c/absaa/index.htm')
        self.assertEqual(self.decoded_combinedRecent[0]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[0]['detectedTime'], '1494532839')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    def test_iidcombinedrecent_entry1(self):
        utc_now = int(self.decoded_combinedRecent[1]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[1]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[1]['comment'], 'Phishing, CENTURYLINK')
        self.assertEqual(self.decoded_combinedRecent[1]['indicator'], 'http://distri7.com/libraries/mill/centurylink/index.php')
        self.assertEqual(self.decoded_combinedRecent[1]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[1]['detectedTime'], '1494532839')
        #These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        #self.assertEqual(self.decoded_combinedRecent[1]['secondaryIndicator'], 'distri7.com')
        #self.assertEqual(self.decoded_combinedRecent[1]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    def test_iidcombinedrecent_entry2(self):
        utc_now = int(self.decoded_combinedRecent[2]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[2]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[2]['comment'], 'Phishing, CENTURYLINK')
        self.assertEqual(self.decoded_combinedRecent[2]['indicator'], 'http://distri7.com/libraries/mill/centurylink/login.html')
        self.assertEqual(self.decoded_combinedRecent[2]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[2]['detectedTime'], '1494532839')
        #These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        #self.assertEqual(self.decoded_combinedRecent[2]['secondaryIndicator'], 'distri7.com')
        #self.assertEqual(self.decoded_combinedRecent[2]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")

    def test_iidcombinedrecent_entry3(self):
        utc_now = int(self.decoded_combinedRecent[3]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[3]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[3]['comment'], 'Phishing, YAHOO.COM')
        self.assertEqual(self.decoded_combinedRecent[3]['indicator'], 'http://ihtjo.ga/3a///yh/en/index.php')
        self.assertEqual(self.decoded_combinedRecent[3]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[3]['detectedTime'], '1494532839')
        #These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        #self.assertEqual(self.decoded_combinedRecent[3]['secondaryIndicator'], 'ihtjo.ga')
        #self.assertEqual(self.decoded_combinedRecent[3]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                         "Processed Time does not fall within time range of Entry 3.")


    def test_iidcombinedrecent_entry4(self):
        utc_now = int(self.decoded_combinedRecent[4]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[4]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[4]['comment'], 'Phishing, YAHOO.COM')
        self.assertEqual(self.decoded_combinedRecent[4]['indicator'], 'http://indonesianwonderagate.com/zee/validate.htm?utm_campaign=tr.im/1e0rQ&utm_content=direct_input&utm_medium=no_referer&utm_source=tr.im')
        self.assertEqual(self.decoded_combinedRecent[4]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[4]['detectedTime'], '1494532839')
        #These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        #self.assertEqual(self.decoded_combinedRecent[4]['secondaryIndicator'], 'indonesianwonderagate.com')
        #self.assertEqual(self.decoded_combinedRecent[4]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 4.")

    def test_iidcombinedrecent_entry5(self):
        utc_now = int(self.decoded_combinedRecent[5]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[5]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[5]['comment'], 'Phishing, YAHOO.COM')
        self.assertEqual(self.decoded_combinedRecent[5]['indicator'], 'http://indonesianwonderagate.com/zee/validate.htm?utm_source=tr.im&utm_medium=www.tr.im&utm_campaign=tr.im%252F1e0rQ&utm_content=link_click')
        self.assertEqual(self.decoded_combinedRecent[5]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[5]['detectedTime'], '1494533139')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[5]['secondaryIndicator'], 'indonesianwonderagate.com')
        # self.assertEqual(self.decoded_combinedRecent[5]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 5.")

    def test_iidcombinedrecent_entry6(self):
        utc_now = int(self.decoded_combinedRecent[6]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[6]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[6]['comment'], 'Phishing, SUNTRUST')
        self.assertEqual(self.decoded_combinedRecent[6]['indicator'], 'http://ivanasr.com/wp-admin/91042/28fde9335169c98810ca8dcfaaaf840b/')
        self.assertEqual(self.decoded_combinedRecent[6]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[6]['detectedTime'], '1494533739')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[6]['secondaryIndicator'], 'ivanasr.com')
        # self.assertEqual(self.decoded_combinedRecent[6]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 6.")

    def test_iidcombinedrecent_entry7(self):
        utc_now = int(self.decoded_combinedRecent[7]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[7]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[7]['comment'], 'Phishing, APPLE ID')
        self.assertEqual(self.decoded_combinedRecent[7]['indicator'], 'http://mail.applesupport.2fh.me/?ID=login&Key=1f104cbd258114b9790b1618d88560b2&login&path=/signin/?referrer')
        self.assertEqual(self.decoded_combinedRecent[7]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[7]['detectedTime'], '1494534039')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[7]['secondaryIndicator'], '2fh.me')
        # self.assertEqual(self.decoded_combinedRecent[7]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 7.")


    def test_iidcombinedrecent_entry8(self):
        utc_now = int(self.decoded_combinedRecent[8]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[8]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[8]['comment'], 'Phishing, YAHOO.COM')
        self.assertEqual(self.decoded_combinedRecent[8]['indicator'], 'http://omstraders.com/system/storage/logs/wp/')
        self.assertEqual(self.decoded_combinedRecent[8]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[8]['detectedTime'], '1494533739')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[8]['secondaryIndicator'], 'omstraders.com')
        # self.assertEqual(self.decoded_combinedRecent[8]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 8.")

    def test_iidcombinedrecent_entry9(self):
        utc_now = int(self.decoded_combinedRecent[9]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[9]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[9]['comment'], 'Phishing, AMAZON')
        self.assertEqual(self.decoded_combinedRecent[9]['indicator'], 'http://primavista-solusi.com/css/.https-www3/sellercentral.amazon.com/ap/signin/cafb30ac87e9c152b70349406227a9bc/auth.php?l=InboxLightaspxn._10&ProductID=DD9E53-&fid=KIBBLDI591KIBBLDI725&fav=1BF807E6036718-UserID&userid=&InboxLight.aspx?n=KIBBLDI591KIBBLDI725&Key=31c5c3553bd4565deab9f760f283b3d6')
        self.assertEqual(self.decoded_combinedRecent[9]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[9]['detectedTime'], '1494534039')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[9]['secondaryIndicator'], 'primavista-solusi.com')
        # self.assertEqual(self.decoded_combinedRecent[9]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 9.")

    def test_iidcombinedrecent_entry10(self):
        utc_now = int(self.decoded_combinedRecent[10]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[10]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[10]['comment'], 'Phishing, YAHOO.COM')
        self.assertEqual(self.decoded_combinedRecent[10]['indicator'], 'http://td6hb.net/gdocs/box/box/GoogleDrive-verfications/yahoo.html')
        self.assertEqual(self.decoded_combinedRecent[10]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[10]['detectedTime'], '1494532539')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[10]['secondaryIndicator'], 'td6hb.net')
        # self.assertEqual(self.decoded_combinedRecent[10]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 10.")

    def test_iidcombinedrecent_entry11(self):
        utc_now = int(self.decoded_combinedRecent[11]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[11]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[11]['comment'], 'Phishing, APPLE ID')
        self.assertEqual(self.decoded_combinedRecent[11]['indicator'], 'http://www.applesupport.2fh.me/?ID=login&Key=920134ac4988da998ba1a66123463b58&login&path=/signin/?referrer')
        self.assertEqual(self.decoded_combinedRecent[11]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_combinedRecent[11]['detectedTime'], '1494534039')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[11]['secondaryIndicator'], '2fh.me')
        # self.assertEqual(self.decoded_combinedRecent[11]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 11.")


#This test has the 'detectedTime test commented out because the field has been left blank in the
#input entry which causes the field to not be made in the output file.
    def test_iidcombinedrecent_entry12(self):
        utc_now = int(self.decoded_combinedRecent[12]['processedTime'])
        self.assertEqual(self.decoded_combinedRecent[12]['action1'], 'Block')
        self.assertEqual(self.decoded_combinedRecent[12]['comment'], 'Phishing, YAHOO.COM')
        self.assertEqual(self.decoded_combinedRecent[12]['indicator'], 'http://www.indonesianwonderagate.com/zee/validate.htm')
        self.assertEqual(self.decoded_combinedRecent[12]['indicatorType'], 'URL')
        #self.assertEqual(self.decoded_combinedRecent[12]['detectedTime'], '')
        # These two test to be uncommented if domain being mapped to secondaryIndicator becomes implemented
        # self.assertEqual(self.decoded_combinedRecent[12]['secondaryIndicator'], 'indonesianwonderagate.com')
        # self.assertEqual(self.decoded_combinedRecent[12]['secondaryIndicatorType'], 'DNSDomainName')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 12.")


class TestIIDActiveBadHostnamestoLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_activeBadHost = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_host_active.cfg'), 'r') as input_file:
            transform.add_parser('iid_host_active', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(IIDACTIVEBADHOST), 'iid_host_active', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_activeBadHost = json.loads(cls.json_file)

    def test_iidactivebadhost_entry0(self):
        utc_now = int(self.decoded_activeBadHost[0]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[0]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[0]['comment'], 'Malware_C2, Backdoor_RAT')
        self.assertEqual(self.decoded_activeBadHost[0]['indicator'], '007panel.no-ip.biz')
        self.assertEqual(self.decoded_activeBadHost[0]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[0]['detectedTime'], '1400533932')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    def test_iidactivebadhost_entry1(self):
        utc_now = int(self.decoded_activeBadHost[1]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[1]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[1]['comment'], 'Exploit_Kit, Exploit_Kit')
        self.assertEqual(self.decoded_activeBadHost[1]['indicator'], '00aa8i2wmwym.upaskitv1.org')
        self.assertEqual(self.decoded_activeBadHost[1]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[1]['detectedTime'], '1399653826')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    def test_iidactivebadhost_entry2(self):
        utc_now = int(self.decoded_activeBadHost[2]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[2]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[2]['comment'], 'Malware_C2, Backdoor_RAT')
        self.assertEqual(self.decoded_activeBadHost[2]['indicator'], '00black00.is-with-theband.com')
        self.assertEqual(self.decoded_activeBadHost[2]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[2]['detectedTime'], '1400533932')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")

    def test_iidactivebadhost_entry3(self):
        utc_now = int(self.decoded_activeBadHost[3]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[3]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[3]['comment'], 'Exploit_Kit, Exploit_Kit')
        self.assertEqual(self.decoded_activeBadHost[3]['indicator'], '00c731dah9of.sentencemc.uni.me')
        self.assertEqual(self.decoded_activeBadHost[3]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[3]['detectedTime'], '1402484639')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 3.")

    def test_iidactivebadhost_entry4(self):
        utc_now = int(self.decoded_activeBadHost[4]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[4]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[4]['comment'], 'Exploit_Kit, Exploit_Kit')
        self.assertEqual(self.decoded_activeBadHost[4]['indicator'], '00dcc4f3azhuei.judiciaryfair.uni.me')
        self.assertEqual(self.decoded_activeBadHost[4]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[4]['detectedTime'], '1402484639')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 4.")

    def test_iidactivebadhost_entry5(self):
        utc_now = int(self.decoded_activeBadHost[5]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[5]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[5]['comment'], 'Exploit_Kit, Magnitude')
        self.assertEqual(self.decoded_activeBadHost[5]['indicator'], '00.e04.d502008.aeaf6fb.f7b.f8.34c48.b90.xwnfgthbe.onesplacing.pw')
        self.assertEqual(self.decoded_activeBadHost[5]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[5]['detectedTime'], '1390402180')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 5.")

    def test_iidactivebadhost_entry6(self):
        utc_now = int(self.decoded_activeBadHost[6]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[6]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[6]['comment'], 'Exploit_Kit, Exploit_Kit')
        self.assertEqual(self.decoded_activeBadHost[6]['indicator'], '00hnumc.wsysinfonet.su')
        self.assertEqual(self.decoded_activeBadHost[6]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[6]['detectedTime'], '1399653826')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 6.")

    def test_iidactivebadhost_entry7(self):
        utc_now = int(self.decoded_activeBadHost[7]['processedTime'])
        self.assertEqual(self.decoded_activeBadHost[7]['action1'], 'Block')
        self.assertEqual(self.decoded_activeBadHost[7]['comment'], 'Malware_C2, Backdoor_RAT')
        self.assertEqual(self.decoded_activeBadHost[7]['indicator'], '00j.no-ip.info')
        self.assertEqual(self.decoded_activeBadHost[7]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_activeBadHost[7]['detectedTime'], '1400533932')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 7.")

class TestIIDDynamicBadHostnamestoLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_dynamicBadHost = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_host_dynamic.cfg'), 'r') as input_file:
            transform.add_parser('iid_host_dynamic', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        new_IIDDYNAMICBADHOST = dynamic_time_change(IIDDYNAMICBADHOST)

        transform.transform(io.StringIO(new_IIDDYNAMICBADHOST), 'iid_host_dynamic', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_dynamicBadHost = json.loads(cls.json_file)

    #Past block date
    def test_iiddynamicbadhost_entry0(self):
        utc_now = int(self.decoded_dynamicBadHost[0]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[0]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[0]['comment'], 'MalwareC2DGA, MalwareC2DGA_GameoverZeus')
        self.assertEqual(self.decoded_dynamicBadHost[0]['indicator'], '1001k04xl19cylqw6nr194ei4b.net')
        self.assertEqual(self.decoded_dynamicBadHost[0]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[0]['duration1'], '0')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    #Past block date
    def test_iiddynamicbadhost_entry1(self):
        utc_now = int(self.decoded_dynamicBadHost[1]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[1]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[1]['comment'], 'MalwareC2DGA, MalwareC2DGA_GameoverZeus')
        self.assertEqual(self.decoded_dynamicBadHost[1]['indicator'], '1001nsa1dxw3sxwrfqee1t7xddm.biz')
        self.assertEqual(self.decoded_dynamicBadHost[1]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[1]['duration1'], '0')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    #Past block date
    def test_iiddynamicbadhost_entry2(self):
        utc_now = int(self.decoded_dynamicBadHost[2]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[2]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[2]['comment'], 'MalwareC2DGA, MalwareC2DGA_GameoverZeus')
        self.assertEqual(self.decoded_dynamicBadHost[2]['indicator'], '10024iajyfsh65e6axy12bsh7l.org')
        self.assertEqual(self.decoded_dynamicBadHost[2]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[2]['duration1'], '0')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")

    #Past block date
    def test_iiddynamicbadhost_entry3(self):
        utc_now = int(self.decoded_dynamicBadHost[3]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[3]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[3]['comment'], 'MalwareC2DGA, MalwareC2DGA_GameoverZeus')
        self.assertEqual(self.decoded_dynamicBadHost[3]['indicator'], '1002cxm19ukeqp1l29lxosdfsig.net')
        self.assertEqual(self.decoded_dynamicBadHost[3]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[3]['duration1'], '0')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 3.")

    #On block date
    def test_iiddynamicbadhost_entry4(self):
        utc_now = int(self.decoded_dynamicBadHost[4]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[4]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[4]['comment'], 'MalwareC2DGA, MalwareC2DGA_GameoverZeus')
        self.assertEqual(self.decoded_dynamicBadHost[4]['indicator'], '1003xa01nbjxku1tilmja1lob2ee.net')
        self.assertEqual(self.decoded_dynamicBadHost[4]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[4]['duration1'], '0')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 4.")

    #On block date
    def test_iiddynamicbadhost_entry5(self):
        utc_now = int(self.decoded_dynamicBadHost[5]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[5]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[5]['comment'], 'MalwareC2DGA, MalwareC2DGA_GameoverZeus')
        self.assertEqual(self.decoded_dynamicBadHost[5]['indicator'], '1004b2a155bhg3lieod8ea14rm.com')
        self.assertEqual(self.decoded_dynamicBadHost[5]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[5]['duration1'], '0')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 5.")

    #On block date
    def test_iiddynamicbadhost_entry6(self):
        utc_now = int(self.decoded_dynamicBadHost[6]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[6]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[6]['comment'], 'MalwareC2DGA, ConfickerC')
        self.assertEqual(self.decoded_dynamicBadHost[6]['indicator'], 'clsg.mu')
        self.assertEqual(self.decoded_dynamicBadHost[6]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[6]['duration1'], '0')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 6.")

    #On block date
    def test_iiddynamicbadhost_entry7(self):
        utc_now = int(self.decoded_dynamicBadHost[7]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[7]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[7]['comment'], 'MalwareC2DGA, ConfickerA')
        self.assertEqual(self.decoded_dynamicBadHost[7]['indicator'], 'clshftfs.org')
        self.assertEqual(self.decoded_dynamicBadHost[7]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[7]['duration1'], '3600')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 7.")

    #Future block date
    def test_iiddynamicbadhost_entry8(self):
        utc_now = int(self.decoded_dynamicBadHost[8]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[8]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[8]['comment'], 'MalwareC2DGA, ConfickerC')
        self.assertEqual(self.decoded_dynamicBadHost[8]['indicator'], 'clshoc.mn')
        self.assertEqual(self.decoded_dynamicBadHost[8]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[8]['duration1'], '345600')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 8.")

    #Future block date
    def test_iiddynamicbadhost_entry9(self):
        utc_now = int(self.decoded_dynamicBadHost[9]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[9]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[9]['comment'], 'MalwareC2DGA, MalwareC2DGA_CryptoLocker')
        self.assertEqual(self.decoded_dynamicBadHost[9]['indicator'], 'clshpwgywbimuok.ru')
        self.assertEqual(self.decoded_dynamicBadHost[9]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[9]['duration1'], '345600')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 9.")

    #Future block date
    def test_iiddynamicbadhost_entry10(self):
        utc_now = int(self.decoded_dynamicBadHost[10]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[10]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[10]['comment'], 'MalwareC2DGA, MalwareC2DGA_Ranbyus')
        self.assertEqual(self.decoded_dynamicBadHost[10]['indicator'], 'clsisxplrhiqycklx.su')
        self.assertEqual(self.decoded_dynamicBadHost[10]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[10]['duration1'], '345600')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                       "Processed Time does not fall within time range of Entry 10.")

    #Future block date
    def test_iiddynamicbadhost_entry11(self):
        utc_now = int(self.decoded_dynamicBadHost[11]['processedTime'])
        self.assertEqual(self.decoded_dynamicBadHost[11]['action1'], 'Block')
        self.assertEqual(self.decoded_dynamicBadHost[11]['comment'], 'MalwareC2DGA, MalwareC2DGA_Qakbot')
        self.assertEqual(self.decoded_dynamicBadHost[11]['indicator'], 'clsitmhauaqfwmvk.org')
        self.assertEqual(self.decoded_dynamicBadHost[11]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_dynamicBadHost[11]['duration1'], '345600')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 11.")

class TestIIDBadIPV4toLQMT(unittest.TestCase):
    output1 = None
    json_file = None
    utc_before = None
    utc_after = None
    decoded_badIPV4 = None

    @classmethod
    def setUpClass(cls):
        current_dir = os.path.dirname(__file__)
        transform = FlexTransform.FlexTransform()

        with open(os.path.join(current_dir, '../resources/sampleConfigurations/iid_ipv4_recent.cfg'), 'r') as input_file:
            transform.add_parser('iid_ipv4_recent', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            transform.add_parser('lqmtools', input_file)
        output1_object = io.StringIO()

        cls.utc_before = arrow.utcnow().to('US/Pacific')

        transform.transform(io.StringIO(IIDBADIPV4), 'iid_ipv4_recent', 'lqmtools', target_file=output1_object)

        cls.utc_after = arrow.utcnow().to('US/Pacific')

        output1_object.seek(0)
        output1_object.readline()
        cls.json_file = output1_object.getvalue()
        cls.decoded_badIPV4 = json.loads(cls.json_file)

    def test_iidbadipv4_entry0(self):
        utc_now = int(self.decoded_badIPV4[0]['processedTime'])
        self.assertEqual(self.decoded_badIPV4[0]['action1'], 'Block')
        self.assertEqual(self.decoded_badIPV4[0]['comment'], 'Spam_Bot, Bot Cutwail')
        self.assertEqual(self.decoded_badIPV4[0]['indicator'], '101.203.174.209')
        self.assertEqual(self.decoded_badIPV4[0]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_badIPV4[0]['detectedTime'], '1494532802')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 0.")

    def test_iidbadipv4_entry1(self):
        utc_now = int(self.decoded_badIPV4[1]['processedTime'])
        self.assertEqual(self.decoded_badIPV4[1]['action1'], 'Block')
        self.assertEqual(self.decoded_badIPV4[1]['comment'], 'Spam_Bot, Bot Cutwail')
        self.assertEqual(self.decoded_badIPV4[1]['indicator'], '103.11.103.105')
        self.assertEqual(self.decoded_badIPV4[1]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_badIPV4[1]['detectedTime'], '1494532844')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 1.")

    def test_iidbadipv4_entry2(self):
        utc_now = int(self.decoded_badIPV4[2]['processedTime'])
        self.assertEqual(self.decoded_badIPV4[2]['action1'], 'Block')
        self.assertEqual(self.decoded_badIPV4[2]['comment'], 'Spam_Bot, Bot Kelihos')
        self.assertEqual(self.decoded_badIPV4[2]['indicator'], '103.12.196.177')
        self.assertEqual(self.decoded_badIPV4[2]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_badIPV4[2]['detectedTime'], '1494532893')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 2.")

    def test_iidbadipv4_entry3(self):
        utc_now = int(self.decoded_badIPV4[3]['processedTime'])
        self.assertEqual(self.decoded_badIPV4[3]['action1'], 'Block')
        self.assertEqual(self.decoded_badIPV4[3]['comment'], 'Spam_Bot, Bot Cutwail')
        self.assertEqual(self.decoded_badIPV4[3]['indicator'], '103.13.28.73')
        self.assertEqual(self.decoded_badIPV4[3]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_badIPV4[3]['detectedTime'], '1494533129')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 3.")

    def test_iidbadipv4_entry4(self):
        utc_now = int(self.decoded_badIPV4[4]['processedTime'])
        self.assertEqual(self.decoded_badIPV4[4]['action1'], 'Block')
        self.assertEqual(self.decoded_badIPV4[4]['comment'], 'Spam_Bot, Bot Cutwail')
        self.assertEqual(self.decoded_badIPV4[4]['indicator'], '103.16.115.18')
        self.assertEqual(self.decoded_badIPV4[4]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_badIPV4[4]['detectedTime'], '1494532800')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 4.")

    def test_iidbadipv4_entry5(self):
        utc_now = int(self.decoded_badIPV4[5]['processedTime'])
        self.assertEqual(self.decoded_badIPV4[5]['action1'], 'Block')
        self.assertEqual(self.decoded_badIPV4[5]['comment'], 'Spam_Bot, Bot Cutwail')
        self.assertEqual(self.decoded_badIPV4[5]['indicator'], '103.17.131.150')
        self.assertEqual(self.decoded_badIPV4[5]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_badIPV4[5]['detectedTime'], '1494532870')
        self.assertTrue(self.utc_before.timestamp <= utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 5.")
if __name__ == '__main__':
    unittest.main()
