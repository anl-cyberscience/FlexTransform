'''
Created on Dec 5, 2014

@author: ahoying
'''

from lxml import etree
import SyntaxParser
# import sys
import copy

# from pprint import pprint
# from uuid import uuid4

class CFM20Alert(object):
    '''
    Parser for CFM version 2.0 Alert XML documents
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    def Read(self, cfm20file, xmlparser = None):
        '''
        Parse CFM20Alert XML document. Return a dictionary object with the data from the document.
        '''
        
        root = None
        if (xmlparser is not None) :
            # Validate file against the schema when it is loaded
            tree = etree.parse(cfm20file, xmlparser)
            root = tree.getroot()
        else :
            tree = etree.parse(cfm20file)
            root = tree.getroot()
        
        ParsedData = {};
        ParsedData['DocumentHeaderData'] = {}
        ParsedData['IndicatorData'] = [];
               
        cfm20dict = SyntaxParser.XMLParser.etree_to_dict(root)
        
        # Extract CFM 2.0 version information
        if ('Version' in cfm20dict['CFMAlert']) :
            ParsedData['DocumentHeaderData']['Version'] = cfm20dict['CFMAlert']['Version']
            
        if (isinstance(cfm20dict['CFMAlert']['Alert'],list)) :
            for alert in cfm20dict['CFMAlert']['Alert'] :
                indicators = self._ProcessCFM20Alert(alert)
                if (indicators.__len__() > 0) :
                    ParsedData['IndicatorData'].extend(indicators)
        else :
            indicators = self._ProcessCFM20Alert(cfm20dict['CFMAlert']['Alert'])
            if (indicators.__len__() > 0) :
                ParsedData['IndicatorData'].extend(indicators)
                
        self._NormalizeCFM20AlertData(ParsedData)
                
        return ParsedData
                

    def _ProcessCFM20Alert(self, alert):
        '''
        Process the alert, return one alert object for each combination of complex indicators
        '''
        
        indicators = []
        
        if ('IndicatorSet' in alert) :
            indicatorList = self._BuildIndicatorList(alert['IndicatorSet'])
            if (indicatorList.__len__() == 1) :
                alert['IndicatorSet'] = indicatorList[0]
                indicators.append(alert)
            else :
                for indicator in indicatorList :
                    newAlert = copy.deepcopy(alert);
                    newAlert['IndicatorSet'] = indicator
                    indicators.append(newAlert)
        
        return indicators
    
    def _BuildIndicatorList(self, indicatorset, operation=None):
        '''
        Process out the indicator set data, return one indicator for each combination of complex indicators
        '''
        
        indicatorList = []
        newIndicators = []
        
        for k,v in indicatorset.items() :
            if (k == 'Indicator') :
                if (isinstance(v,list)) :
                    indicatorList.extend(v)
                else :
                    indicatorList.append(v)
            elif (k == 'CompositeIndicator') :
                if ('Or' in v) :
                    newIndicators = self._BuildIndicatorList(v['Or'], operation='Or')
                    if (operation != 'And') :
                        indicatorList.extend(newIndicators)
                    
                elif ('And' in v) :
                    newIndicators = self._BuildIndicatorList(v['And'], operation='And')
                    indicatorList.append(newIndicators)
                    
                else :
                    raise Exception('InvalidOperation', 'Invalid composite indicator operation: %s' % v.items())
                
        if (operation == 'And') :
            for i in newIndicators :
                for x in indicatorList :
                    if (isinstance(x,list)) :
                        x.extend(i)
                    else :
                        x = [x,i]
                        
        return indicatorList
    
    def _NormalizeCFM20AlertData(self, ParsedData):
        '''
        Normalize the data in the indicators, convert dictionaries to arrays for elements that may have multiple values, add namespaces to values if they are missing
        '''
                
        NormalizeElementLists = {
                                'ActionList': {'Action': 'list'},
                                'ReasonList': {'Reason': 'list'},
                                'IndicatorSet': 'list',
                                'AlertExtendedAttribute': 'list'
                                }
        
        NormalizeElementValueNamespaces =   {
                                            'ActionList': {'Action': { 'ActionCategory': 'http://www.anl.gov/cfm/2.0/current/#'}},
                                            'ReasonList': {'Reason': { 'ReasonCategory': 'http://www.anl.gov/cfm/2.0/current/#'}},
                                            'IndicatorSet': {'Type': 'http://www.anl.gov/cfm/2.0/current/#', 'Constraint': 'http://www.anl.gov/cfm/2.0/current/#'},
                                            'AlertExtendedAttribute': {'Field': 'http://www.anl.gov/cfm/2.0/current/#'},
                                            }
        
        for indicator in ParsedData['IndicatorData'] :
            self._NormalizeIndicatorElements(indicator, NormalizeElementLists)
            self._NormalizeIndicatorNamespaces(indicator, NormalizeElementValueNamespaces)
            
            
    def _NormalizeIndicatorElements(self, indicator, element):
        '''
        Normalize a single indicator, use the element dictionary for processing rules on which elements should always be represented as a list
        '''
        
        if (isinstance(element,dict)) :
            for (e,v) in element.items() :
                if (e in indicator) :
                    if (isinstance(v,dict)) :
                        self._NormalizeIndicatorElements(indicator[e], element[e])
                    elif (isinstance(v,str)) :
                        if (v == 'list' and not isinstance(indicator[e], list)) :
                            newValue = indicator.pop(e)
                            indicator[e] = [newValue]

    def _NormalizeIndicatorNamespaces(self, indicator, element):
        '''
        Normalize a single indicator, use the element dictionary for processing rules on which elements should have the namespace prepended to the value
        '''
        
        if (isinstance(element,dict)) :
            for (e,v) in element.items() :
                if (isinstance(indicator,dict) and e in indicator) :
                    if (isinstance(v,dict)) :
                        self._NormalizeIndicatorNamespaces(indicator[e], element[e])
                    elif (isinstance(v,str) and v not in indicator[e]) :
                        indicator[e] = "%s%s" % (v,indicator[e])
                elif (isinstance(indicator,list)) :
                    for i in indicator :
                        self._NormalizeIndicatorNamespaces(i, element)
            