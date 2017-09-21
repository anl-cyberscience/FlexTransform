## Examples
- Input Files (present in the repo, not the package, download to known location if needed)
  - [CFM13 File](./Example Files/SampleInput-CFM13.xml)
  - [STIX-TLP File](./Example Files/SampleInput-STIX-TLP.xml)
- Command
  - CFM13 to STIX-TLP


    flext --src FlexTransform/ExampleFiles/SampleInput-CFM13.xml --src-config FlexTransform/FlexTransform/resources/sampleConfigurations/cfm13.cfg --dst Output-STIX-TLP.xml --dst-config FlexTransform/FlexTransform/resources/sampleConfigurations/stix_tlp.cfg
  - STIX-TLP to CFM13

   
    flext --src FlexTransform/ExampleFiles/SampleInput-STIX-TLP.xml --src-config FlexTransform/FlexTransform/resources/sampleConfigurations/stix_tlp.cfg --dst Output-CFM13.xml --dst-config FlexTransform/FlexTransform/resources/sampleConfigurations/cfm13.cfg
- Output
  - CFM13 to STIX-TLP

      
      <stix:STIX_Package 
      	xmlns:cyboxCommon="http://cybox.mitre.org/common-2"
      	xmlns:cybox="http://cybox.mitre.org/cybox-2"
      	xmlns:cyboxVocabs="http://cybox.mitre.org/default_vocabularies-2"
      	xmlns:AddressObj="http://cybox.mitre.org/objects#AddressObject-2"
      	xmlns:PortObj="http://cybox.mitre.org/objects#PortObject-2"
      	xmlns:marking="http://data-marking.mitre.org/Marking-1"
      	xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
      	xmlns:coa="http://stix.mitre.org/CourseOfAction-1"
      	xmlns:indicator="http://stix.mitre.org/Indicator-2"
      	xmlns:stixCommon="http://stix.mitre.org/common-1"
      	xmlns:stixVocabs="http://stix.mitre.org/default_vocabularies-1"
      	xmlns:stix="http://stix.mitre.org/stix-1"
      	xmlns:CFM="http://www.anl.gov/cfm/stix"
      	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      	xsi:schemaLocation="
      	http://cybox.mitre.org/common-2 http://cybox.mitre.org/XMLSchema/common/2.1/cybox_common.xsd
      	http://cybox.mitre.org/cybox-2 http://cybox.mitre.org/XMLSchema/core/2.1/cybox_core.xsd
      	http://cybox.mitre.org/default_vocabularies-2 http://cybox.mitre.org/XMLSchema/default_vocabularies/2.1/cybox_default_vocabularies.xsd
      	http://cybox.mitre.org/objects#AddressObject-2 http://cybox.mitre.org/XMLSchema/objects/Address/2.1/Address_Object.xsd
      	http://cybox.mitre.org/objects#PortObject-2 http://cybox.mitre.org/XMLSchema/objects/Port/2.1/Port_Object.xsd
      	http://data-marking.mitre.org/Marking-1 http://stix.mitre.org/XMLSchema/data_marking/1.1.1/data_marking.xsd
      	http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1 http://stix.mitre.org/XMLSchema/extensions/marking/tlp/1.1.1/tlp_marking.xsd
      	http://stix.mitre.org/CourseOfAction-1 http://stix.mitre.org/XMLSchema/course_of_action/1.1.1/course_of_action.xsd
      	http://stix.mitre.org/Indicator-2 http://stix.mitre.org/XMLSchema/indicator/2.1.1/indicator.xsd
      	http://stix.mitre.org/common-1 http://stix.mitre.org/XMLSchema/common/1.1.1/stix_common.xsd
      	http://stix.mitre.org/default_vocabularies-1 http://stix.mitre.org/XMLSchema/default_vocabularies/1.1.1/stix_default_vocabularies.xsd
      	http://stix.mitre.org/stix-1 http://stix.mitre.org/XMLSchema/core/1.1.1/stix_core.xsd" id="CFM:STIXPackage-722cede7-e98e-53db-b3a9-192a0c6166cb" version="1.1.1" timestamp="2016-05-20T20:43:24+00:00">
        <stix:STIX_Header>
            <stix:Package_Intent xsi:type="stixVocabs:PackageIntentVocab-1.0">Indicators</stix:Package_Intent>
            <stix:Handling>
                <marking:Marking>
                    <marking:Controlled_Structure>//node() | //@*</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color="AMBER"/>
                </marking:Marking>
            </stix:Handling>
            <stix:Information_Source>
                <stixCommon:Description>Fake National Lab</stixCommon:Description>
                <stixCommon:Identity>
                    <stixCommon:Name>Fake</stixCommon:Name>
                </stixCommon:Identity>
                <stixCommon:Time>
                    <cyboxCommon:Produced_Time>2016-02-21T22:50:02+06:00</cyboxCommon:Produced_Time>
                </stixCommon:Time>
            </stix:Information_Source>
        </stix:STIX_Header>
        <stix:Indicators>
            <stix:Indicator id="CFM:Indicator-2b2d04ff-b597-5f30-bd6e-e7741e91d1ed" timestamp="2016-05-20T20:43:24+00:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">IP Watchlist</indicator:Type>
                <indicator:Description>SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high</indicator:Description>
                <indicator:Observable id="CFM:Observable-44b81e1b-f77b-5903-b4a7-5c56c9c5748b" sighting_count="1">
                    <cybox:Keywords>
                        <cybox:Keyword>Scanning</cybox:Keyword>
                    </cybox:Keywords>
                    <cybox:Object id="CFM:Object-da05a4ba-1626-57c8-9a7b-bcaf514c43e7">
                        <cybox:Properties xsi:type="AddressObj:AddressObjectType" category="ipv4-addr">
                            <AddressObj:Address_Value condition="Equals">10.10.10.10</AddressObj:Address_Value>
                        </cybox:Properties>
                        <cybox:Related_Objects>
                            <cybox:Related_Object id="CFM:Object-7ca69e67-d908-55da-8a42-2e0d4cf8fbaf">
                                <cybox:Properties xsi:type="PortObj:PortObjectType">
                                    <PortObj:Port_Value>22</PortObj:Port_Value>
                                    <PortObj:Layer4_Protocol>TCP</PortObj:Layer4_Protocol>
                                </cybox:Properties>
                                <cybox:Relationship xsi:type="cyboxVocabs:ObjectRelationshipVocab-1.1">Connected_To</cybox:Relationship>
                            </cybox:Related_Object>
                        </cybox:Related_Objects>
                    </cybox:Object>
                </indicator:Observable>
                <indicator:Suggested_COAs>
                    <indicator:Suggested_COA>
                        <stixCommon:Course_Of_Action id="CFM:COA-7a9ed7c3-4872-51cc-83e4-3f0600cc400d" xsi:type='coa:CourseOfActionType'>
                            <coa:Stage>Remedy</coa:Stage>
                            <coa:Type>Perimeter Blocking</coa:Type>
                        </stixCommon:Course_Of_Action>
                    </indicator:Suggested_COA>
                </indicator:Suggested_COAs>
                <indicator:Sightings sightings_count="12">
                    <indicator:Sighting timestamp="2016-02-21T22:45:53-04:00" timestamp_precision="second"/>
                </indicator:Sightings>
            </stix:Indicator>
        </stix:Indicators>
      </stix:STIX_Package>
      
   - STIX-TLP to CFM13

    
    <?xml version='1.0' encoding='UTF-8'?>
    <!DOCTYPE IDMEF-Message PUBLIC "-//IETF//DTD RFC XXXX IDMEF v1.0//EN" "idmef-message.dtd">
    <IDMEF-Message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.anl.gov/cfm/1.3/IDMEF-Message" xsi:schemaLocation="http://www.anl.gov/cfm/1.3/IDMEF-Message/../../../resources/schemas/CFMMessage13.xsd">
      <Alert>
        <Analyzer analyzerid="Fake">
          <Node>
            <location>1325 G St, NW, Suite 600, Washington DC 20005</location>
            <name>Operations Desk, 404-446-9780, operations@esisac.com</name>
          </Node>
        </Analyzer>
        <AnalyzerTime>2016-03-23T16:45:05+0400</AnalyzerTime>
        <AdditionalData type="string" meaning="report schedule">NoValue</AdditionalData>
        <AdditionalData type="integer" meaning="number of alerts in this report">2</AdditionalData>
        <AdditionalData type="string" meaning="report type">alerts</AdditionalData>
        <AdditionalData type="date-time" meaning="report start time">2016-03-23T16:45:05+0400</AdditionalData>
      </Alert>
      <Alert>
        <CreateTime>2016-03-23T16:45:05+0400</CreateTime>
        <Source>
          <Node>
            <Address category="ipv4-addr">
              <address>10.10.10.10</address>
            </Address>
          </Node>
        </Source>
        <Classification text="CRISP Report Indicator">
          <Reference meaning="Unspecified" origin="user-specific">
            <name>unknown</name>
            <url> </url>
          </Reference>
        </Classification>
        <Assessment>
          <Action category="block-installed"/>
        </Assessment>
        <AdditionalData type="integer" meaning="recon">0</AdditionalData>
        <AdditionalData type="integer" meaning="OUO">0</AdditionalData>
        <AdditionalData type="integer" meaning="duration">86400</AdditionalData>
        <AdditionalData type="string" meaning="restriction">public</AdditionalData>
      </Alert>
      <Alert>
        <CreateTime>2016-03-23T16:45:05+0400</CreateTime>
        <Source>
          <Node>
            <Address>
              <address>bad.domain.be/poor/path</address>
            </Address>
          </Node>
        </Source>
        <Classification text="URL Block: CRISP Report Indicator">
          <Reference meaning="Unspecified" origin="user-specific">
            <name>unknown</name>
            <url> </url>
          </Reference>
        </Classification>
        <Assessment>
          <Action category="block-installed"/>
        </Assessment>
        <AdditionalData type="integer" meaning="recon">0</AdditionalData>
        <AdditionalData type="integer" meaning="OUO">0</AdditionalData>
        <AdditionalData type="integer" meaning="duration">86400</AdditionalData>
        <AdditionalData type="string" meaning="restriction">public</AdditionalData>
      </Alert>
    </IDMEF-Message>
    
    
   -STIX-TLP to LQMT
    
    {
    "indicators" : {
        "DataSensitivity": "noSensitivity",
        "DownloadElementExtendedAttribute": {
            "Field": "orig1.3Filename",
            "Value": "asderts.201409140500.xml.gpg"
        },
        "FileName": "LQMT_Test_Alert.Alert.Cfm13Alert",
        "PayloadFormat": "Cfm13Alert",
        "PayloadType": "Alert",
        "ReconPolicy": "Touch",
        "SendingSite": "ANL",
        "SentTimestamp": "1410685202",
        "UploadID": "0387f9cc-a903-4822-8976-27e1ff47ca71"
    }
}
