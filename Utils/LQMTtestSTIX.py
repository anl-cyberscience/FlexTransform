'''
Created on Nov 18, 2014

@author: ahoying
'''

from FlexTransform import FlexTransform
import os
import json
import logging

if __name__ == '__main__':
    
    currentdir = os.path.dirname(__file__)
    logging.basicConfig(format='%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s', level=logging.DEBUG)
    
    TestDir = os.path.join(currentdir, 'resources/sampleMessages/stix')
    
    Transform = FlexTransform()
    StixConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/stix_ciscp.cfg'), 'r')
    Transform.add_parser('STIX', StixConfig)
    
    LQMToolsConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/lqmtools.cfg'), 'r')
    Transform.add_parser('LQMTools', LQMToolsConfig)
    
    TransformedData = []
    
    for file in os.listdir(TestDir) :
        if (file.startswith('CISCP_INDICATOR.')) :        
            sourceFile = os.path.join(TestDir, file)
            
            logging.info(sourceFile)
            
            try :
                Data = Transform.transform(source_file=sourceFile, source_parser_name='STIX', target_parser_name='LQMTools')
            except Exception as inst :
                logging.exception(inst)
            else :
                if (Data) :
                    TransformedData.extend(Data)
                  
    out = open(os.path.join(currentdir,'resources/testing/lqmtools-stix-test.json'), 'w')  
    json.dump(TransformedData, out, sort_keys=True, indent=4)