'''
Created on Aug 26, 2015

@author: ahoying
'''

import json
import logging


class iSightReport(object):
    '''
    Parser for iSight JSON Reports
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.logging = logging.getLogger('FlexTransform.DICTParser.iSightReports')
    
    def Read(self, reportFile):
        '''
        Read in JSON report file and process into indicators and header data
        '''
        
        jsondoc = json.load(reportFile)
        
        if ("success" in jsondoc and jsondoc["success"] == True) :
        
            if ("message" in jsondoc and "report" in jsondoc["message"]) :
                Report = jsondoc["message"]["report"]
                
                indicators = []
                
                if ("tagSection" in Report) :
                    indicators = self._extractIndicators(Report.pop("tagSection"))
                
                if (len(indicators) == 0) :
                    raise Exception("NoData","iSight JSON document did not contain any indicators")
                
                ParsedData = {};
                ParsedData['IndicatorData'] = indicators;
                ParsedData['DocumentHeaderData'] = Report;
                
            else :
                raise Exception("NoData","iSight JSON document did not contain a report")
            
        else :
            raise Exception("Unparsable","iSight JSON document could not be parsed, success field not defined or not True")
        
        return ParsedData
    
    def Write(self, reportFile, FinalizedData):
        raise Exception("MethodNotDefined","Write")
    
    def _extractIndicators(self,tagSection):
        
        indicators = []
        
        for indicatorType in tagSection :
            if (indicatorType == "main") :
                # TODO, extract TTP and other targetting data from the main tag
                continue
            if (indicatorType == "networks") :
                networkList = tagSection["networks"].pop("network")
                
                if (isinstance(networkList,list)) :
                    for network in networkList :
                        # Fix for error in iSight JSON generation that appends a .0 to the end of the asn numbers
                        if ("asn" in network and network["asn"].endswith(".0")) :
                            network["asn"] = network["asn"].replace(".0","")
                        indicators.append(network)
                else :
                    indicators.append(networkList)
            if (indicatorType == "emails") :
                emailList = tagSection["emails"].pop("email")
                
                if (isinstance(emailList,list)) :
                    for email in emailList :
                        indicators.append(email)
                else :
                    indicators.append(emailList)
            if (indicatorType == "files") :
                fileList = tagSection["files"].pop("file")
                
                if (isinstance(fileList,list)) :
                    for file in fileList :
                        indicators.append(file)
                else :
                    indicators.append(fileList)
                    
        return indicators
                    
            
    
        