'''
Created on Aug 25, 2015

@author: ahoying
'''

import textwrap
import io

class KeyValueData(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        self.sample_kv_ipv4 = "timestamp=1325401200 ipv4=10.11.12.13 direction=ingress comment='Attacker scanning for RDP' service=3389/TCP category='Scanning' severity=high\r\n"
        
        self.sample_kv_ipv6 = "timestamp=1325401200 ipv6=2001:db8:16::1 direction=ingress comment='HTTP Response code 4xx, suspicious' category='Reconnaissance' severity=low\r\n"
        
        self.sample_kv_domain = "timestamp=1325401200 fqdn=bad.domain direction=egress comment='Malicious domain' category='Malware Traffic' severity=high\r\n"
    
    def getFile(self):
        
        sample_kv_file = io.BytesIO(textwrap.dedent(self.sample_kv_domain +
                                                        self.sample_kv_ipv4 +
                                                        self.sample_kv_ipv6).encode("UTF-8"))
        
        return sample_kv_file