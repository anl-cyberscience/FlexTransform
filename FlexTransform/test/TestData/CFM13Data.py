'''
Created on Aug 25, 2015

@author: ahoying
'''

import textwrap
import io

class CFM13Data(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.sample_cfm13_string_head = """<?xml version="1.0" encoding="UTF-8"?>
                                <!DOCTYPE IDMEF-Message PUBLIC "-//IETF//DTD RFC XXXX IDMEF v1.0//EN" "idmef-message.dtd">
                                <IDMEF-Message>
                                <Alert>
                                <Analyzer analyzerid="TEST">
                                <Node>
                                <location>TEST</location>
                                <name>Test User, 555-555-1212, test@test.int</name>
                                </Node>
                                </Analyzer>
                                <AnalyzerTime>2015-05-30T09:10:45-0000</AnalyzerTime>
                                <AdditionalData meaning="report start time" type="date-time">2015-05-30T09:10:45-0000</AdditionalData>
                                <AdditionalData meaning="report type" type="string">alerts</AdditionalData>
                                <AdditionalData meaning="report schedule" type="string">5 minutes</AdditionalData>
                                <AdditionalData meaning="number of alerts in this report" type="integer">2</AdditionalData>
                                </Alert>
                                """
                                
        self.sample_cfm13_string_alert1 = """                        
                                <Alert>
                                <CreateTime>2015-05-30T09:08:00-0000</CreateTime>
                                <Source>
                                <Node category="dns">
                                <name>badsite.example.int</name>
                                <Address category="ipv4-addr">
                                <address>192.168.123.231</address>
                                </Address>
                                </Node>
                                </Source>
                                <Classification text="WEBattack"/>
                                <Assessment>
                                <Action category="block-installed">Blocked for 2592000 seconds</Action>
                                </Assessment>
                                <AdditionalData meaning="restriction" type="string">private</AdditionalData>
                                <AdditionalData meaning="recon" type="integer">0</AdditionalData>
                                <AdditionalData meaning="prior offenses" type="integer">1</AdditionalData>
                                <AdditionalData meaning="OUO" type="integer">0</AdditionalData>
                                <AdditionalData meaning="top level domain owner" type="string">US, United States</AdditionalData>
                                <AdditionalData meaning="duration" type="integer">2592000</AdditionalData>
                                <AdditionalData meaning="alert threshold" type="integer">1</AdditionalData>
                                </Alert>
                                """
                                
        self.sample_cfm13_string_alert2 = """ 
                                <Alert>
                                <CreateTime>2015-05-30T09:09:00-0000</CreateTime>
                                <Source>
                                <Node category="dns">
                                <name>another.evil.site</name>
                                <Address category="ipv4-addr">
                                <address>172.20.40.120</address>
                                </Address>
                                </Node>
                                </Source>
                                <Target>
                                <Service>
                                <port>22</port>
                                </Service>
                                </Target>
                                <Classification text="Netflow port or host scan">
                                <Reference origin="user-specific" meaning="Scanning">
                                <name>Netflow port or host scan</name>
                                </Reference>
                                </Classification>
                                <Assessment>
                                <Action category="block-installed">Host scan</Action>
                                </Assessment>
                                <AdditionalData meaning="restriction" type="string">private</AdditionalData>
                                <AdditionalData meaning="recon" type="integer">0</AdditionalData>
                                <AdditionalData meaning="prior offenses" type="integer">2</AdditionalData>
                                <AdditionalData meaning="OUO" type="integer">0</AdditionalData>
                                <AdditionalData meaning="duration" type="integer">36000</AdditionalData>
                                </Alert>
                                """
                                
        self.sample_cfm13_string_alert_portlist = """
                                <Alert>
                                <CreateTime>2015-05-30T09:09:20-0000</CreateTime>
                                <Source>
                                <Node>
                                <Address category="ipv4-addr">
                                <address>172.17.17.172</address>
                                </Address>
                                </Node>
                                </Source>
                                <Target>
                                <Service>
                                <portlist>1433,3306</portlist>
                                <protocol>TCP</protocol>
                                </Service>
                                </Target>
                                <Classification text="MSSQL scans against multiple hosts, direction:ingress, confidence:77, severity:medium">
                                <Reference meaning="Scanning" origin="user-specific">
                                <name>Scanning</name>
                                <url> </url>
                                </Reference>
                                </Classification>
                                <Assessment>
                                <Action category="block-installed"/>
                                </Assessment>
                                <AdditionalData meaning="alert threshold" type="integer">0</AdditionalData>
                                <AdditionalData meaning="recon" type="integer">0</AdditionalData>
                                <AdditionalData meaning="duration" type="integer">86400</AdditionalData>
                                <AdditionalData meaning="OUO" type="integer">0</AdditionalData>
                                <AdditionalData meaning="prior offenses" type="integer">5</AdditionalData>
                                </Alert>
                                """
                                
        self.sample_cfm13_string_alert_urlblock = """
                                <Alert>
                                <CreateTime>2015-05-30T09:09:00+00:00</CreateTime>
                                <Source>
                                <Node>
                                <Address>
                                <address>http://bad.domain.url/?ref=RANDOM_STRING</address>
                                </Address>
                                </Node>
                                </Source>
                                <Classification text="URL Block: Random String">
                                <Reference origin="user-specific" meaning="Phishing">
                                <name>target: bad.domain.url</name>
                                </Reference>
                                </Classification>
                                <Assessment>
                                <Action category="notification-sent" />
                                </Assessment>
                                <AdditionalData type="integer" meaning="prior offenses">0</AdditionalData>
                                <AdditionalData type="integer" meaning="alert threshold">1</AdditionalData>
                                <AdditionalData type="integer" meaning="duration">0</AdditionalData>
                                <AdditionalData type="integer" meaning="recon">1</AdditionalData>
                                <AdditionalData type="integer" meaning="OUO">1</AdditionalData>
                                <AdditionalData type="string" meaning="restriction">private</AdditionalData>
                                <AdditionalData type="string" meaning="alert provenance">badurl 12345</AdditionalData>
                                </Alert>
                                """
                                
        self.sample_cfm13_string_alert_domainblock = """
                                <Alert>
                                <CreateTime>2015-05-30T09:06:00+00:00</CreateTime>
                                <Source>
                                <Node category="dns">
                                <name>malicious.domain</name>
                                </Node>
                                </Source>
                                <Classification text="Domain Block: malicious"/>
                                <Assessment>
                                <Action category="notification-sent">observe_and_report</Action>
                                </Assessment>
                                <AdditionalData type="integer" meaning="prior offenses">0</AdditionalData>
                                <AdditionalData type="integer" meaning="alert threshold">255</AdditionalData>
                                <AdditionalData type="integer" meaning="duration">0</AdditionalData>
                                <AdditionalData type="integer" meaning="recon">1</AdditionalData>
                                <AdditionalData type="string" meaning="restriction">private</AdditionalData>
                                <AdditionalData type="integer" meaning="OUO">1</AdditionalData>
                                </Alert>
                                """
                                
        self.sample_cfm13_string_tail = "</IDMEF-Message>"
        
    def getFile(self):
        
        sample_cfm13_file = io.BytesIO(textwrap.dedent(self.sample_cfm13_string_head + 
                                                        self.sample_cfm13_string_alert1 + 
                                                        self.sample_cfm13_string_alert2 + 
                                                        self.sample_cfm13_string_alert_portlist +
                                                        self.sample_cfm13_string_alert_urlblock +
                                                        self.sample_cfm13_string_alert_domainblock +
                                                        self.sample_cfm13_string_tail).encode("UTF-8"))
        
        return sample_cfm13_file