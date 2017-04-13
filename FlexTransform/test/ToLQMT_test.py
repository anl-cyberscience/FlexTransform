import io
import os
import unittest
import json
import arrow

from FlexTransform.test.SampleInputs import CFM20ALERT, CFM13ALERT, STIXTLP, STIXACS, KEYVALUE
from FlexTransform import FlexTransform


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
        self.assertEqual(self.decoded_cfm13_1[0]['detectedTime'], 1456109153) #14561163.0

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

    #Added from Sean's Test

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
        self.assertEqual(self.decoded_cfm13_1[0]['comment'], 'SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high')

    def test_cfm13_fileHasMore(self):
        self.assertEqual(self.decoded_cfm13_1[0]['fileHasMore'], '0')

    def test_cfm13_reference(self):
        self.assertEqual(self.decoded_cfm13_1[0]['reference1'], 'user-specific')





    # # CFM20 format tests

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
        self.assertEqual(self.decoded_cfm13_2[0]['detectedTime'], 1468350602)

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
            # transform.AddParser('cfm13alert', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('stix_tlp', input_file)
        with open(os.path.join(current_dir, '../resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            # transform.AddParser('lqmtools', input_file) Used for master branch since it still uses AddParser (3/22/2017)
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
        self.assertEqual(self.decoded_tlp[0]['detectedTime'], 1458737105)
        self.assertEqual(self.decoded_tlp[0]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[0]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[0]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[0]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[0]['indicator'], '10.10.10.10')
        self.assertEqual(self.decoded_tlp[0]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[0]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")


    def test_stixtlp_entry1(self):
        utc_now = int(self.decoded_tlp[1]['processedTime'])
        self.assertEqual(self.decoded_tlp[1]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[1]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[1]['dataItemID'], 'CFM:Indicator-82b0c3f9-95d4-5ec7-9e09-30b0bf87cfcd')
        self.assertEqual(self.decoded_tlp[1]['detectedTime'], 1458737105)
        self.assertEqual(self.decoded_tlp[1]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[1]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[1]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[1]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[1]['indicator'], '13.13.13.13')
        self.assertEqual(self.decoded_tlp[1]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[1]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")


    def test_stixtlp_entry2(self):
        utc_now = int(self.decoded_tlp[2]['processedTime'])
        self.assertEqual(self.decoded_tlp[2]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[2]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[2]['dataItemID'], 'CFM:Indicator-52c46f7c-cca9-5d2e-9d3b-a3b1744dcf52')
        self.assertEqual(self.decoded_tlp[2]['detectedTime'], 1458737105)
        self.assertEqual(self.decoded_tlp[2]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[2]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[2]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[2]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[2]['indicator'], '12.12.12.12')
        self.assertEqual(self.decoded_tlp[2]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[2]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 2.")


    def test_stixtlp_entry3(self):
        utc_now = int(self.decoded_tlp[3]['processedTime'])
        self.assertEqual(self.decoded_tlp[3]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[3]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[3]['dataItemID'], 'CFM:Indicator-052c65e0-c667-5e4c-9970-ac9ddd3511b3')
        self.assertEqual(self.decoded_tlp[3]['detectedTime'], 1458737105)
        self.assertEqual(self.decoded_tlp[3]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[3]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[3]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[3]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[3]['indicator'], '11.11.11.11')
        self.assertEqual(self.decoded_tlp[3]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[3]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[3]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 3.")


    def test_stixtlp_entry4(self):
        utc_now = int(self.decoded_tlp[4]['processedTime'])
        self.assertEqual(self.decoded_tlp[4]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[4]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[4]['dataItemID'], 'CFM:Indicator-1cf2d34d-007a-5a50-b7c1-cce9faf6f968')
        self.assertEqual(self.decoded_tlp[4]['detectedTime'], 1458737105)
        self.assertEqual(self.decoded_tlp[4]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[4]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[4]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[4]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[4]['indicator'], '14.14.14.14')
        self.assertEqual(self.decoded_tlp[4]['indicatorType'], 'IPv4Address')
        self.assertEqual(self.decoded_tlp[4]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[4]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 4.")


    def test_stixtlp_entry5(self):
        utc_now = int(self.decoded_tlp[5]['processedTime'])
        self.assertEqual(self.decoded_tlp[5]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[5]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[5]['dataItemID'], 'CFM:Indicator-2e95d2ac-1b08-5f38-8522-2f4b2ef3686c')
        self.assertEqual(self.decoded_tlp[5]['detectedTime'], 1458737105)
        self.assertEqual(self.decoded_tlp[5]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[5]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[5]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[5]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[5]['indicator'], 'bad.domain.be/poor/path')
        self.assertEqual(self.decoded_tlp[5]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[5]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[5]['secondaryIndicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[5]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 5.")


    def test_stixtlp_entry6(self):
        utc_now = int(self.decoded_tlp[6]['processedTime'])
        self.assertEqual(self.decoded_tlp[6]['action1'], 'Block')
        self.assertEqual(self.decoded_tlp[6]['comment'], 'CRISP Report Indicator')
        self.assertEqual(self.decoded_tlp[6]['dataItemID'], 'CFM:Indicator-5fd6c616-d923-5e70-916d-dca3a2d1ee02')
        self.assertEqual(self.decoded_tlp[6]['detectedTime'], 1458737105)
        self.assertEqual(self.decoded_tlp[6]['directSource'], 'Fake')
        self.assertEqual(self.decoded_tlp[6]['duration1'], '86400')
        self.assertEqual(self.decoded_tlp[6]['fileHasMore'], '0')
        self.assertEqual(self.decoded_tlp[6]['fileID'], 'CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0')
        self.assertEqual(self.decoded_tlp[6]['indicator'], 'fake.site.com/malicious.js')
        self.assertEqual(self.decoded_tlp[6]['indicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[6]['reconAllowed'], '1')
        self.assertEqual(self.decoded_tlp[6]['secondaryIndicatorType'], 'URL')
        self.assertEqual(self.decoded_tlp[6]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 6.")

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
        self.assertEqual(self.decoded_acs[0]['dataItemID'], 'isa:guide.999191.Indicator-3312fec8-9504-51ad-bd9f-e43017af4a10')
        self.assertEqual(self.decoded_acs[0]['duration1'], '86400')
        self.assertEqual(self.decoded_acs[0]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs[0]['fileID'], 'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs[0]['indicator'], 'blog.website.net')
        self.assertEqual(self.decoded_acs[0]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs[0]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")

    def test_stixacs_entry1(self):
        utc_now = int(self.decoded_acs[1]['processedTime'])
        self.assertEqual(self.decoded_acs[1]['action1'], 'Block')
        self.assertEqual(self.decoded_acs[1]['comment'], 'Domain Indicator')
        self.assertEqual(self.decoded_acs[1]['dataItemID'], 'isa:guide.999191.Indicator-60742920-231d-508d-8f75-d361f24a5fb0')
        self.assertEqual(self.decoded_acs[1]['duration1'], '86400')
        self.assertEqual(self.decoded_acs[1]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs[1]['fileID'], 'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs[1]['indicator'], 'fake.com')
        self.assertEqual(self.decoded_acs[1]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs[1]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")

    def test_stixacs_entry2(self):
        utc_now = int(self.decoded_acs[2]['processedTime'])
        self.assertEqual(self.decoded_acs[2]['action1'], 'Block')
        self.assertEqual(self.decoded_acs[2]['comment'], 'Just Another Indicator')
        self.assertEqual(self.decoded_acs[2]['dataItemID'], 'isa:guide.999191.Indicator-f2911c1d-a14d-50de-a211-33a8beb7c7e6')
        self.assertEqual(self.decoded_acs[2]['duration1'], '86400')
        self.assertEqual(self.decoded_acs[2]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs[2]['fileID'], 'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs[2]['indicator'], 'goo.gl/peter')
        self.assertEqual(self.decoded_acs[2]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs[2]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
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
        self.assertEqual(self.decoded_acs30[0]['dataItemID'], 'isa:guide.999191.Indicator-3312fec8-9504-51ad-bd9f-e43017af4a10')
        self.assertEqual(self.decoded_acs30[0]['duration1'], '86400')
        self.assertEqual(self.decoded_acs30[0]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs30[0]['fileID'], 'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs30[0]['indicator'], 'blog.website.net')
        self.assertEqual(self.decoded_acs30[0]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs30[0]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs30[0]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 0.")


    def test_stixacs30_entry1(self):
        utc_now = int(self.decoded_acs30[1]['processedTime'])
        self.assertEqual(self.decoded_acs30[1]['action1'], 'Block')
        self.assertEqual(self.decoded_acs30[1]['comment'], 'Domain Indicator')
        self.assertEqual(self.decoded_acs30[1]['dataItemID'], 'isa:guide.999191.Indicator-60742920-231d-508d-8f75-d361f24a5fb0')
        self.assertEqual(self.decoded_acs30[1]['duration1'], '86400')
        self.assertEqual(self.decoded_acs30[1]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs30[1]['fileID'], 'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs30[1]['indicator'], 'fake.com')
        self.assertEqual(self.decoded_acs30[1]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs30[1]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs30[1]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                        "Processed Time does not fall within time range of Entry 1.")


    def test_stixacs30_entry2(self):
        utc_now = int(self.decoded_acs30[2]['processedTime'])
        self.assertEqual(self.decoded_acs30[2]['action1'], 'Block')
        self.assertEqual(self.decoded_acs30[2]['comment'], 'Just Another Indicator')
        self.assertEqual(self.decoded_acs30[2]['dataItemID'], 'isa:guide.999191.Indicator-f2911c1d-a14d-50de-a211-33a8beb7c7e6')
        self.assertEqual(self.decoded_acs30[2]['duration1'], '86400')
        self.assertEqual(self.decoded_acs30[2]['fileHasMore'], '0')
        self.assertEqual(self.decoded_acs30[2]['fileID'], 'isa:guide.999191.STIXPackage-96f564e1-e1b1-5625-b41c-506e231fbd53')
        self.assertEqual(self.decoded_acs30[2]['indicator'], 'goo.gl/peter')
        self.assertEqual(self.decoded_acs30[2]['indicatorType'], 'DNSDomainName')
        self.assertEqual(self.decoded_acs30[2]['reconAllowed'], '1')
        self.assertEqual(self.decoded_acs30[2]['sensitivity'], 'noSensitivity')
        self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
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
        try:
            utc_now = int(self.decoded_keyvalue[0]['processedTime'])
            self.assertEqual(self.decoded_keyvalue[0]['action1'], 'Block')
            self.assertEqual(self.decoded_keyvalue[0]['comment'], 'Attacker scanning for RDP, direction:ingress, confidence:0, severity:high')
            self.assertEqual(self.decoded_keyvalue[0]['detectedTime'], 1325401200)
            self.assertEqual(self.decoded_keyvalue[0]['duration1'], '86400')
            self.assertEqual(self.decoded_keyvalue[0]['fileHasMore'], '0')
            self.assertEqual(self.decoded_keyvalue[0]['majorTags'], 'Scanning')
            self.assertEqual(self.decoded_keyvalue[0]['reason1'], 'Scanning')
            self.assertEqual(self.decoded_keyvalue[0]['indicator'], '10.11.12.13')
            self.assertEqual(self.decoded_keyvalue[0]['indicatorType'], 'IPv4Address')
            self.assertEqual(self.decoded_keyvalue[0]['reconAllowed'], '1')
            self.assertEqual(self.decoded_keyvalue[0]['sensitivity'], 'noSensitivity')
            self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 0.")

        except:
            print(json.dumps(self.decoded_keyvalue[0], indent=4, sort_keys=True))
            self.assertEqual(0, 1)

    def test_keyvalue_entry1(self):
        try:
            utc_now = int(self.decoded_keyvalue[1]['processedTime'])
            self.assertEqual(self.decoded_keyvalue[1]['action1'], 'Block')
            self.assertEqual(self.decoded_keyvalue[1]['comment'], 'Attacker scanning for SSH, direction:ingress, confidence:0, severity:high')
            self.assertEqual(self.decoded_keyvalue[1]['detectedTime'], 1325401200)
            self.assertEqual(self.decoded_keyvalue[1]['duration1'], '86400')
            self.assertEqual(self.decoded_keyvalue[1]['fileHasMore'], '0')
            self.assertEqual(self.decoded_keyvalue[1]['majorTags'], 'Scanning')
            self.assertEqual(self.decoded_keyvalue[1]['reason1'], 'Scanning')
            self.assertEqual(self.decoded_keyvalue[1]['indicator'], '10.11.12.14')
            self.assertEqual(self.decoded_keyvalue[1]['indicatorType'], 'IPv4Address')
            self.assertEqual(self.decoded_keyvalue[1]['reconAllowed'], '1')
            self.assertEqual(self.decoded_keyvalue[1]['sensitivity'], 'noSensitivity')
            self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 1.")
        except:
            print(json.dumps(self.decoded_keyvalue[0], indent=4, sort_keys=True))
            print(json.dumps(self.decoded_keyvalue[1], indent=4, sort_keys=True))
            print(json.dumps(self.decoded_keyvalue[2], indent=4, sort_keys=True))
            print(json.dumps(self.decoded_keyvalue[3], indent=4, sort_keys=True))
            self.assertEqual(0,1)

    def test_keyvalue_entry2(self):
        try:
            utc_now = int(self.decoded_keyvalue[2]['processedTime'])
            self.assertEqual(self.decoded_keyvalue[2]['action1'], 'Block')
            self.assertEqual(self.decoded_keyvalue[2]['comment'], 'HTTP Response code 4xx, suspicious, direction:ingress, confidence:0, severity:low')
            self.assertEqual(self.decoded_keyvalue[2]['detectedTime'], 1325401200)
            self.assertEqual(self.decoded_keyvalue[2]['duration1'], '86400')
            self.assertEqual(self.decoded_keyvalue[2]['fileHasMore'], '0')
            self.assertEqual(self.decoded_keyvalue[2]['majorTags'], 'Reconnaissance')
            self.assertEqual(self.decoded_keyvalue[2]['reason1'], 'Reconnaissance')
            self.assertEqual(self.decoded_keyvalue[2]['indicator'], '2001:db8:16::1')
            self.assertEqual(self.decoded_keyvalue[2]['indicatorType'], 'IPv6Address')
            self.assertEqual(self.decoded_keyvalue[2]['reconAllowed'], '1')
            self.assertEqual(self.decoded_keyvalue[2]['sensitivity'], 'noSensitivity')
            self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 2.")

        except:
            print(json.dumps(self.decoded_keyvalue[2], indent=4, sort_keys=True))
            self.assertEqual(0, 1)

    def test_keyvalue_entry3(self):
        try:
            utc_now = int(self.decoded_keyvalue[3]['processedTime'])
            self.assertEqual(self.decoded_keyvalue[3]['action1'], 'Block')
            self.assertEqual(self.decoded_keyvalue[3]['comment'], 'Malicious domain, direction:egress, confidence:0, severity:high')
            self.assertEqual(self.decoded_keyvalue[3]['detectedTime'], 1325401200)
            self.assertEqual(self.decoded_keyvalue[3]['duration1'], '86400')
            self.assertEqual(self.decoded_keyvalue[3]['fileHasMore'], '0')
            self.assertEqual(self.decoded_keyvalue[3]['majorTags'], 'Malware Traffic')
            self.assertEqual(self.decoded_keyvalue[3]['reason1'], 'Malware Traffic')
            self.assertEqual(self.decoded_keyvalue[3]['indicator'], 'bad.domain')
            self.assertEqual(self.decoded_keyvalue[3]['indicatorType'], 'DNSDomainName')
            self.assertEqual(self.decoded_keyvalue[3]['reconAllowed'], '1')
            self.assertEqual(self.decoded_keyvalue[3]['sensitivity'], 'noSensitivity')
            self.assertTrue(self.utc_before.timestamp <= utc_now and utc_now <= self.utc_after.timestamp,
                            "Processed Time does not fall within time range of Entry 3.")

        except:
            print(json.dumps(self.decoded_keyvalue[3], indent=4, sort_keys=True))
            self.assertEqual(0, 1)

if __name__ == '__main__':
    unittest.main()
