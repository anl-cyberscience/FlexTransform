#!/home/sys-kenobi/.virtualenvs/isight/bin/python
'''
Created on Oct 10, 2014

@author: Matt Henderson
'''

from os import environ
import datetime
import hashlib
import hmac
import httplib
import subprocess
import time
import urllib
import uuid

from lxml import etree


class isight(object):
    '''
    Downloads indicators from iSIGHT
    
    Queries iSIGHTS RESTful api with various configurations. Currently only using
    indicator query.
    '''
    _query = {
        'domain': 'gicp.net',
        'format': 'xml'}

    _pubKey = "bb5695d39d48aa400f67ca36f943e61cc4ee30b30d0a0437ea870f195af64013"
    _privKey = "fab04a886c245cd5e16a9d9ab179f04e9ec995d15a433c0e4ee38c26f6bc7245"
    _uriBasic = "/search/basic"
    _uriAdvanced = "/search/advanced"
    _uriIndicator = "/view/indicators"
    _uriReportIndex = "/report/index"
    _uriReportDownload = "/report/"
    
#     def __init__(self):
#         """
#         Constructor
#         """
#         pass
    
    def _get_time_from(self, offset):
        '''
        Returns epoch time of now-offset.  Offset is in minutes.
        '''
        
        return int(time.time() - offset * 60)

    def get_data(self, url, path, query, pub, prv):
        try:
            from urlparse import urlparse
        except ImportError:
            from urllib.parse import urlparse
        hashed = hmac.new(prv, '', hashlib.sha256)
        
        headers = {
            'X-Auth': pub,
            'X-Auth-Hash': hashed.hexdigest()
        }
        
        conn = httplib.HTTPSConnection(url)
        conn.request('GET', path + '?' + query, '', headers)
#         conn.request('GET', "/view/indicators?startDate=1415635200&endDate=1415723057&format=xml", '', headers)
    
        resp = conn.getresponse()
        return resp.read()

    def get_indicators(self, minBefore):
        '''
        Return all reports published in last N minutes
        
        minBefore = how far back should reports be pulled
        Polls iSIGHT's servers for all reports released in the last "minBefore" mintues,
        returns xml formatted list with metadata from Reports
        '''
        return self.get_data("api.isightpartners.com", self._uriIndicator, urllib.urlencode({'since': self._get_time_from(minBefore), 'format': 'xml'}), self._pubKey, self._privKey)
    
    def get_report_index(self, minBefore):
        '''
        Return all reports published in last N minutes
        
        minBefore = how far back should reports be pulled
        Polls iSIGHT's servers for all reports released in the last "minBefore" mintues,
        returns xml formatted list with metadata from Reports
        '''
        return self.get_data("api.isightpartners.com", self._uriReportIndex, urllib.urlencode({'since': self._get_time_from(minBefore), 'format': 'xml'}), self._pubKey, self._privKey)
    
    def get_report(self, reportId, reportFormat):
        '''
        Returns specified report in given format
        
        reportId = iSIGHT report id for requested report
        reportFormat = format for downloaded report: json, xml, STIX, pdf
        '''
        return self.get_data("api.isightpartners.com", self._uriReportDownload + reportId, urllib.urlencode({'format': reportFormat, 'detail': 'full'}), self.pubKey, self.privKey)
            
    
class IndicatorStore(object):
    '''
    Sort input into reports, store data, output CFM alerts
    '''
    
    _nsm = {"tns": "http://www.anl.gov/cfm/2.0/current/CFMAlert",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    _cfm_prefix = "{http://www.anl.gov/cfm/2.0/current/CFMAlert}"
    
    def __init__(self, xml_input):
        '''
        Initialize instance variables, parse xml input.
        
        _report_dict = dictionary w/ key=reportId, value = a set containing indicator groups
        
        raises IOError if the xmlinput contains no indicators
        '''
        
        self._report_dict = {}
        input_local = etree.XML(xml_input)
        if "false" in input_local.find("success").text:
            raise IOError("No indicators from iSIGHT")
        self._build_report_index(input_local)
        
    def _build_report_index(self, xml_input):
        '''
        Sorts indicators into Reports.
        
        Checks whether the indicator's report has already been initialized, if not
        do so, if so then add the indicator to the apporpriate report set.
        '''
        
        for element in xml_input.iter("indicatorsAndWarning"):
            reportID = element.find("reportId").text
            if reportID in self._report_dict:
                self._report_dict[reportID].add_indicator(element)
            else:
                self._report_dict[reportID] = ReportIndicators(element)
                
    def gen_cfm_20_alerts(self):
        '''
        Public method to create CFMAlert structure
        
        Creates root w/ namespace & schema information, version, then iterates through
        reports to create alerts.  Returns xml structure
        '''
        
        output = etree.Element(self._cfm_prefix + "CFMAlert", nsmap=self._nsm, attrib={"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://www.anl.gov/cfm/2.0/current/CFMAlert CFMAlert.xsd "})
        etree.SubElement(output, self._cfm_prefix + "Version").text = "2.0"
        
        for report in self._report_dict.values():
            output.append(report.gen_cfm_20_alert())
        return output

    def indicator_count(self):
        '''
        Aggregates & returns total number of iSIGHT indicators in output 
        '''
        
        count = 0
        for report in self._report_dict.itervalues():
            count += report.indicator_count()
        return count

    def report_count(self):
        '''
        Returns number of reports contained in output
        '''
        return len(self._report_dict)


class ReportIndicators(object):
    """
    Holds indicators associated with a report.
    
    Class Variables:
        _key_value_20_map = dictionary mapping of iSIGHT fields to CFM 2.0
            Alert fields, not all fields directly mapped.
    Instance Variables:
        report_id = iSIGHT report ID for quick reference
        indicator_value_dict = dict with key = iSIGHT field names, value =
            set of iSIGHT values.
    """
    
    _key_value_20_map = {
        'emailName': ('EmailAddress', 'EmailAddressMatch'),
        'attachmentName': ('FileName', 'SringValueMatch'),
        'attachmentMD5': ('FileMD5Hash', 'MD5Equality'),
        'attachmentSHA1': ('FileSHA1Hash', 'SHA1Equality'),
        'malicious_url': ('URL', 'URLMatch'),
        'senderAddress': ('EmailAddress', 'EmailAddressMatch'),
        'sourceDomain': ('DNSDomainName', 'DNSSubDomainNameMatch'),
        'sourceIP': ('IPv4SourceAddress', 'IPv4DottedDecimalEquality'),
        'subject': ('EmailSubject', 'StringValueMatch'),
        'recipient': ('EmailAddress', 'EmailAddressMatch'),
        'ccrecipient': ('EmailAddress', 'EmailAddressMatch'),
        'content': ('EmailBody', 'StringValueMatch'),
        'fileName': ('FileName', 'StringValueMatch'),
        'fileSize': ('FileSize', 'IntegerEquality'),
        'md5': ('FileMD5Hash', 'MD5Equality'),
        'sha1': ('FileSHA1Hash', 'SHA1Equality'),
        'cidr': ('IPv4Address', 'IPv4CIDRMembership'),
        'domain': ('DNSDomainName', 'DNSDomainNameMatch'),
        'ips': ('IPv4Address', 'IPv4DottedDecimalEquality')
    }
    _cfm_prefix = "{http://www.anl.gov/cfm/2.0/current/CFMAlert}"
    _cfm_text_value_prefix = "&cfm;"
    _cfm_text_value_isight_prefix = "iSIGHT-"
    _nsm = {"tns": "http://www.anl.gov/cfm/2.0/current/CFMAlert",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    def __init__(self, xml_indicator):
        # Public Instance Variables
        self.indicator_value_dict = {}
        self.report_id = xml_indicator.find("reportId").text
        self.report_output = ""

        # Private Instance Variables
        self._report_timestamp = xml_indicator.find("publishDate").text
        self._alert_indicator_location = ""
        self._alert_extended_indicator_location = ""
        self._key_ignore_set = set(["emailTagId", "filetagid", "networktagid"])
        self._indicator_count = 0

        self.add_indicator(xml_indicator)

    def add_indicator(self, xml_indicator):
        for value in xml_indicator.getchildren():
            if value.text and value.tag not in self._key_ignore_set:
                if value.tag in self.indicator_value_dict:
                    self.indicator_value_dict[value.tag].update([value.text])
                else:
                    self.indicator_value_dict[value.tag] = set([value.text])
                    if value.tag == "domainTimeOfLookup":
                        self._key_ignore_set.update([value.tag])

    def gen_cfm_20_alert(self):
        '''
        Public method to generate & return CFM 2.0 Alert
        '''
        
        self._gen_cfm_20_alert_skeleton()
        [[self._gen_cfm_20_indicator(p[0], v) for v in p[1]] for p in self.indicator_value_dict.items()]
        
        return self.report_output

    def _gen_cfm_20_alert_skeleton(self):
        """
        Create empty CFM 2.0 alert

        Clear previous data, create the empty alert, & store it along with
        sub-element references (increase speed by reducing repeated structure
        traversal)
        """

        # xml root = CFMAlert
#         self.report_output = etree.Element(self._cfm_prefix + "CFMAlert", nsmap=self._nsm, attrib={"{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": "http://www.anl.gov/cfm/2.0/current/CFMAlert CFMAlert.xsd "})

        # Children of CFMAlert
#         etree.SubElement(self.report_output, self._cfm_prefix + "Version").text = "2.0"
#         elementAlert = etree.SubElement(self.report_output, self._cfm_prefix + "Alert")
        self.report_output = etree.Element(self._cfm_prefix + "Alert")

        # Children of Alert
        etree.SubElement(self.report_output, self._cfm_prefix + "AlertID").text = str(uuid.uuid4())
        etree.SubElement(self.report_output, self._cfm_prefix + "AlertTimestamp").text = self._report_timestamp
        elementIndicatorSet = etree.SubElement(self.report_output, self._cfm_prefix + "IndicatorSet")
        elementReasonList = etree.SubElement(self.report_output, self._cfm_prefix + "ReasonList")
        elementActionList = etree.SubElement(self.report_output, self._cfm_prefix + "ActionList")
        
        # Child of IndicatorSet
        elementCompositeIndicator = etree.SubElement(elementIndicatorSet, self._cfm_prefix + "CompositeIndicator")
        
        # Child of CompositeIndicator
        self._alert_indicator_location = etree.SubElement(elementCompositeIndicator, self._cfm_prefix + "Or")
        
        # Child of ReasonList
        elementReason = etree.SubElement(elementReasonList, self._cfm_prefix + "Reason")
        etree.SubElement(elementReason, self._cfm_prefix + "ReasonCategory").text = "Unspecified"
        etree.SubElement(elementReason, self._cfm_prefix + "ReasonDescription").text = "iSIGHT"
        
        # Child of ActionList
        elementAction = etree.SubElement(elementActionList, self._cfm_prefix + "Action")
        etree.SubElement(elementAction, self._cfm_prefix + "ActionCategory").text = "Block"
        etree.SubElement(elementAction, self._cfm_prefix + "ActionTimestamp").text = self._report_timestamp
        
        # Set pointer to Alert element, for appending extended alert attributes
#         self._alert_extended_indicator_location = elementAlert
        self._alert_extended_indicator_location = self.report_output

    def _gen_cfm_20_indicator(self, key, value):
        """
        Create and add CFM 2.0 indicator to alert structure
    
        Arguments:
        key = iSIGHT field name
        value = iSIGHT field value
        """
        if key in self._key_value_20_map:
            if key == "fileSize" and int(value) <= 0:
                return
            new_indicator = etree.SubElement(self._alert_indicator_location, self._cfm_prefix + "Indicator")
            new_type = etree.SubElement(new_indicator, self._cfm_prefix + "Type")
            new_constraint = etree.SubElement(new_indicator, self._cfm_prefix + "Constraint")
            new_value = etree.SubElement(new_indicator, self._cfm_prefix + "Value")

            type_, constraint = self._key_value_20_map[key]
            new_type.text = self._cfm_text_value_prefix + type_
            new_constraint.text = self._cfm_text_value_prefix + constraint
            new_value.text = value
        else:
            if key == "registrantEmail":
                key = "DomainRegistrantEmail"
            extended_attribute = etree.SubElement(self._alert_extended_indicator_location, self._cfm_prefix + "AlertExtendedAttribute")
            etree.SubElement(extended_attribute, self._cfm_prefix + "Field").text = self._cfm_text_value_prefix + self._cfm_text_value_isight_prefix + key
            etree.SubElement(extended_attribute, self._cfm_prefix + "Value").text = value
        self._indicator_count += 1

    def indicator_count(self):
        return self._indicator_count


if __name__ == '__main__':
    # How far back do we look every time
    time_interval = 6000
    
    # Paths specific to ht-sink.it.anl.gov
    sys_path = "/var/opt/crons/"
    cfm_path = "cfm3/bin/cfm3"
    cfm_config_path = "cfm3/etc/cfm-isight.conf"
    
    try:
        print "[{0}] Success Start".format(datetime.datetime.utcnow())
        
        # Download & process iSIGHT data into an indicator store object
        indicator_store = IndicatorStore(isight().get_indicators(time_interval))
        
        # Format & store alerts from indicator_store
        with open("output.xml", "w") as output_file:
            output_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE CFMEnvelope [\n\t<!ENTITY cfm \'http://www.anl.gov/cfm/2.0/current/#\'>\n\t<!ENTITY tlp \'http://www.us-cert.gov/tlp/#\'>\n]>\n")
            output_file.write(etree.tostring(indicator_store.gen_cfm_20_alerts(), pretty_print=True).replace("&amp;cfm;", "&cfm;"))
            
        # CFM client call with modified environment
        my_env = environ.copy()
        my_env["PROXY_ALERT"] = "0"
        subprocess.Popen(sys_path + cfm_path + " -f " + sys_path + cfm_config_path + " upload", shell=True, env=my_env)
        
        print "[{0}] Success Finish {1} Alerts {2} Indicators".format(datetime.datetime.utcnow(), indicator_store.report_count(), indicator_store.indicator_count())
    except IOError as e:
        print "[{0}] Success Finish 0 Alerts 0 Indicators".format(datetime.datetime.utcnow())
    except Exception as e:
        print "[{0}] Error {1}".format(datetime.datetime.utcnow(), e)
