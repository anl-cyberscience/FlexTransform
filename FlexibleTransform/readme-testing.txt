To test, I set the following arguments in eclipse:

--src-config resources/sampleConfigurations/cfm13.cfg --src resources/sampleMessages/cfm13Uploads/cfm13-B1.xml --dst-config resources/sampleConfigurations/cfm13_nrel.cfg --dst resources/testing/dst.xml

--src-config resources/sampleConfigurations/cfm13.cfg --src resources/sampleMessages/cfm13Uploads/WithMetadata/1433D342-EC43-4E81-B596-843A03C6B21A_20141118151046_ANL.Alert.Cfm13Alert --src-metadata resources/sampleMessages/cfm13Uploads/WithMetadata/.1433D342-EC43-4E81-B596-843A03C6B21A_20141118151046_ANL.Alert.Cfm13Alert --dst-config resources/sampleConfigurations/cfm13_nrel.cfg --dst resources/testing/dst.xml

--src-config resources/sampleConfigurations/cfm13.cfg --src resources/sampleMessages/cfm13Uploads/WithMetadata/1433D342-EC43-4E81-B596-843A03C6B21A_20141118151046_ANL.Alert.Cfm13Alert --src-metadata resources/sampleMessages/cfm13Uploads/WithMetadata/.1433D342-EC43-4E81-B596-843A03C6B21A_20141118151046_ANL.Alert.Cfm13Alert --dst-config resources/sampleConfigurations/lqmtools.cfg --dst resources/testing/lqmtools-test.json

Test KeyValue:

--src-config resources/sampleConfigurations/keyvalue_nrel.cfg --src resources/sampleMessages/keyvalue/nsnare.log --dst-config resources/sampleConfigurations/cfm13_nrel.cfg --dst resources/testing/cfm13-nsnare-transform.xml

Test STIX:

--src-config resources/sampleConfigurations/stix_ciscp.cfg --src resources/sampleMessages/stix/CISCP_INDICATOR.1682097386.1.xml --dst-config resources/sampleConfigurations/cfm13_nrel.cfg --dst resources/testing/cfm13-ciscp_stix-transform.xml

--src-config resources/sampleConfigurations/stix_ciscp.cfg --src resources/sampleMessages/stix/CISCP_INDICATOR.1682097386.1.xml --dst-config resources/sampleConfigurations/lqmtools.cfg --dst resources/testing/lqmtools-stix-test.json

--src-config resources/sampleConfigurations/stix_ciscp.cfg --src resources/sampleMessages/stix/CISCP_INDICATOR.1682097386.1.xml --dst-config resources/sampleConfigurations/cfm20alert.cfg --dst resources/testing/cfm20-ciscp_stix-transform.xml

Test CFM 2.0 Alert

--src-config resources/sampleConfigurations/cfm20alert.cfg --src resources/sampleMessages/cfm20Alerts/1DC002C2-98F9-498F-A8DA-6820DC7D1F52_20141125193003_FedP.Alert.Cfm20Alert --dst-config resources/sampleConfigurations/cfm13_nrel.cfg --dst resources/testing/dst.xml

--src-config resources/sampleConfigurations/cfm13.cfg --src resources/sampleMessages/cfm13Uploads/WithMetadata/1433D342-EC43-4E81-B596-843A03C6B21A_20141118151046_ANL.Alert.Cfm13Alert --src-metadata resources/sampleMessages/cfm13Uploads/WithMetadata/.1433D342-EC43-4E81-B596-843A03C6B21A_20141118151046_ANL.Alert.Cfm13Alert --dst-config resources/sampleConfigurations/cfm20alert.cfg --dst resources/testing/dst.xml

--src-config resources/sampleConfigurations/cfm20alert.cfg --src resources/sampleMessages/cfm20Alerts/1DC002C2-98F9-498F-A8DA-6820DC7D1F52_20141125193003_FedP.Alert.Cfm20Alert --dst-config resources/sampleConfigurations/cfm20alert.cfg --dst resources/testing/dst.xml