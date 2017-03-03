'''
Created on Nov 18, 2014

@author: ahoying
'''

from FlexTransform import FlexTransform
import os
import json
import logging
'''
# To enable profiling, remove comments below
import cProfile, pstats, io
'''

if __name__ == '__main__':
    
    '''
    # Profiling
    pr = cProfile.Profile()
    '''
    
    currentdir = os.path.dirname(__file__)
    logging.basicConfig(format='%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s', level=logging.DEBUG)
    
    TestDir = os.path.join(currentdir, 'resources/sampleMessages/cfm13Uploads/WithMetadata')
    
    Transform = FlexTransform.FlexTransform()
    Cfm13AlertConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/cfm13.cfg'), 'r')
    Transform.add_parser('Cfm13Alert', Cfm13AlertConfig)
    
    LQMToolsConfig = open(os.path.join(currentdir,'resources/sampleConfigurations/lqmtools.cfg'), 'r')
    Transform.add_parser('LQMTools', LQMToolsConfig)
    
    TransformedData = []
    
    for file in os.listdir(TestDir):
        if file.startswith('.'):
            f = open(os.path.join(TestDir, file), 'r')
            metadata = json.load(f)
            f.close()
            
            sourceFile = os.path.join(TestDir, metadata['FileName'])
            logging.info(sourceFile)
            
            '''
            # Profiling
            pr.enable()
            '''
            
            try:
                Data = Transform.transform(source_file=sourceFile, source_parser_name=metadata['PayloadFormat'], target_parser_name='LQMTools', source_meta_data=metadata)
            except Exception as inst :
                logging.exception(inst)
            else:
                if Data:
                    TransformedData.extend(Data)

            '''
            # Profiling
            pr.disable()
            '''

    '''
    # Profiling
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    '''
                       
    out = open(os.path.join(currentdir,'resources/testing/lqmtools-test.json'), 'w')
    json.dump(TransformedData, out, sort_keys=True, indent=4)
