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
    
    TestDir = os.path.join(currentdir, 'resources/sampleMessages/cfm13Uploads/WithMetadata')
    
    Transform = FlexTransform()
    Cfm13AlertConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/cfm13.cfg'), 'r')
    Transform.AddParser('Cfm13Alert', Cfm13AlertConfig)
    
    LQMToolsConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/lqmtools.cfg'), 'r')
    Transform.AddParser('LQMTools', LQMToolsConfig)
    
    TransformedData = []
    
    for file in os.listdir(TestDir) :
        if (file.startswith('.')) :
            f = open(os.path.join(TestDir, file), 'r')
            metadata = json.load(f)
            f.close()
            
            sourceFile = os.path.join(TestDir, metadata['FileName'])
            
            try :
                Data = Transform.TransformFile(sourceFileName=sourceFile, sourceParserName=metadata['PayloadFormat'], targetParserName='LQMTools', sourceMetaData=metadata)
            except Exception as inst :
                print(sourceFile + ': ' + str(inst), file=sys.stderr)
            else :
                if (Data) :
                    TransformedData.extend(Data)
                  
    out = open(os.path.join(currentdir,'resources/testing/lqmtools-test.json'), 'w')  
    json.dump(TransformedData, out, sort_keys=True, indent=4)