import io
import os
import unittest
import json

from FlexTransform.test.SampleInputs import CFM20ALERT, CFM13ALERT
from FlexTransform import FlexTransform

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

        with open(os.path.join(current_dir, 'C:/Users/epdevine/Desktop/AL_FlexTransform/FlexTransform/FlexTransform/resources/sampleConfigurations/cfm13.cfg'), 'r') as input_file:
            #transform.AddParser('cfm13alert', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('cfm13alert', input_file)
        with open(os.path.join(current_dir, 'C:/Users/epdevine/Desktop/AL_FlexTransform/FlexTransform/FlexTransform/resources/sampleConfigurations/lqmtools.cfg'), 'r') as input_file:
            #transform.AddParser('lqmtools', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('lqmtools', input_file)
        with open(os.path.join(current_dir, 'C:/Users/epdevine/Desktop/AL_FlexTransform/FlexTransform/FlexTransform/resources/sampleConfigurations/cfm20alert.cfg'), 'r') as input_file:
            #transform.AddParser('cfm20alert', input_file) Used for master branch since it still uses AddParser (3/22/2017)
            transform.add_parser('cfm20alert', input_file)
        output1_object = io.StringIO()
        output2_object = io.StringIO()

        # with open("C:/Users/epdevine/Desktop/AL_FlexTransform/FlexTransform/ExampleFiles/SampleInput-CFM13.xml", "r") as in_file:
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

if __name__ == '__main__':
    unittest.main()