'''
Created on Nov 18, 2014

@author: ahoying
'''

from FlexTransform import FlexTransform
import os
import sys
import json

if __name__ == '__main__':
    
    currentdir = os.path.dirname(__file__)
    
    TestDir = os.path.join(currentdir, 'resources/sampleMessages/stix')
    
    Transform = FlexTransform()
    StixConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/stix_ciscp.cfg'), 'r')
    Transform.AddParser('STIX', StixConfig)
    
    LQMToolsConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/lqmtools.cfg'), 'r')
    Transform.AddParser('LQMTools', LQMToolsConfig)
    
    TransformedData = []
    
    for file in os.listdir(TestDir) :
        if (file.startswith('CISCP')) :        
            sourceFile = os.path.join(TestDir, file)
            
            print(sourceFile, file=sys.stderr)
            
            try :
                Data = Transform.TransformFile(sourceFileName=sourceFile, sourceParserName='STIX', targetParserName='LQMTools')
            except Exception as inst :
                print(sourceFile + ': ' + str(inst), file=sys.stderr)
            else :
                if (Data) :
                    TransformedData.extend(Data)
                  
    out = open(os.path.join(currentdir,'resources/testing/lqmtools-stix-test.json'), 'w')  
    json.dump(TransformedData, out, sort_keys=True, indent=4)