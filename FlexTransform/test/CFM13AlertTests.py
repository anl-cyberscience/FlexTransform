import io
import os
import unittest
from lxml import etree

from FlexTransform import FlexTransform

CFM13ALERT1 = """
    <!DOCTYPE IDMEF-Message PUBLIC "-//IETF//DTD RFC XXXX IDMEF v1.0//EN" "idmef-message.dtd">
    <IDMEF-Message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.anl.gov/cfm/1.3/IDMEF-Message" xsi:schemaLocation="http://www.anl.gov/cfm/1.3/IDMEF-Message/../../../resources/schemas/CFMMessage13.xsd">
      <Alert>
        <Analyzer analyzerid="Fake">
          <Node>
            <location>Fake National Lab</location>
            <name>Fake Name</name>
          </Node>
        </Analyzer>
        <AnalyzerTime>2016-02-21T22:50:02+0000</AnalyzerTime>
        <AdditionalData meaning="report schedule" type="string">5 minutes</AdditionalData>
        <AdditionalData meaning="number of alerts in this report" type="integer">2</AdditionalData>
        <AdditionalData meaning="report type" type="string">alerts</AdditionalData>
        <AdditionalData meaning="report start time" type="date-time">2016-02-21T22:45:53+0000</AdditionalData>
      </Alert>
      <Alert>
        <CreateTime>2016-02-21T22:45:53+0000</CreateTime>
        <Source>
          <Node>
            <Address category="ipv4-addr">
              <address>10.10.10.10</address>
            </Address>
          </Node>
        </Source>
        <Target>
          <Service>
            <port>22</port>
            <protocol>TCP</protocol>
          </Service>
        </Target>
        <Classification text="SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high">
          <Reference meaning="Scanning" origin="user-specific">
            <name>SSH Attack</name>
            <url> </url>
          </Reference>
        </Classification>
        <Assessment>
          <Action category="block-installed"/>
        </Assessment>
        <AdditionalData meaning="restriction" type="string">private</AdditionalData>
        <AdditionalData meaning="recon" type="integer">0</AdditionalData>
        <AdditionalData meaning="prior offenses" type="integer">11</AdditionalData>
        <AdditionalData meaning="duration" type="integer">86400</AdditionalData>
        <AdditionalData meaning="alert threshold" type="integer">0</AdditionalData>
        <AdditionalData meaning="OUO" type="integer">0</AdditionalData>
        <AdditionalData meaning="top level domain owner" type="string">The Republic of Fake</AdditionalData>
      </Alert>
    </IDMEF-Message>
    """


class TestCFM13Alert1ToSTIXTLP(unittest.TestCase):
    output1 = None
    namespace = {
        'cybox': "http://cybox.mitre.org/cybox-2",
        'indicator': "http://stix.mitre.org/Indicator-2",
        'marking': "http://data-marking.mitre.org/Marking-1",
        'stix': "http://stix.mitre.org/stix-1",
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

        transform.TransformFile(io.StringIO(CFM13ALERT1), 'cfm13alert', 'stix', targetFileName=output1_object)
        cls.output1 = etree.XML(output1_object.getvalue())

    def test_tlp_type(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/marking:Marking_Structure/@xsi:type", namespaces=self.namespace)[0], "tlpMarking:TLPMarkingStructureType")

    def test_tlp_color(self):
        self.assertEqual(self.output1.xpath("/stix:STIX_Package/stix:STIX_Header/stix:Handling/marking:Marking/marking:Marking_Structure/@color", namespaces=self.namespace)[0], "AMBER")


if __name__ == '__main__':
    unittest.main()