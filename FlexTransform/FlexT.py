'''
Created on Jun 17, 2015

@author: ahoying
'''

def main():
    from FlexTransform import FlexTransform
    from FlexTransform.OntologyOracle import OntologyOracle
    import logging
    
    import argparse
    import os
    import json
    
    logging.basicConfig(format='%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s', level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description="Transform a source file's syntax and schema to the target file document type")
    parser.add_argument('--src-config',
                        type=argparse.FileType('r'),
                        help='Source file parser configuration',
                        metavar='CONFIG',
                        required=True)
    parser.add_argument('--src',
                        type=argparse.FileType('r'),
                        help='Source file',
                        required=True)
    parser.add_argument('--src-metadata',
                        type=argparse.FileType('r'),
                        help='Source Metadata file',
                        required=False)
    parser.add_argument('--dst-config',
                        type=argparse.FileType('r'),
                        help='Destination file parser configuration',
                        metavar='CONFIG',
                        required=True)
    parser.add_argument('--dst',
                        type=argparse.FileType('w'),
                        help='Destination file',
                        required=True)
    
    parser.add_argument('--tbox-uri',
                        type=argparse.FileType('r'),
                        help='The uri location of the tbox file to load',
                        required=False)
    
    
    args = parser.parse_args()
    
    try:       
        Transform = FlexTransform.FlexTransform()
        Transform.AddParser('src', args.src_config)
        Transform.AddParser('dst', args.dst_config)
    
        metadata = None
                
        if (args.src_metadata) :
            metadata = json.load(args.src_metadata)
        
        kb = None
    
        if (args.tbox_uri) :
            kb = OntologyOracle.Oracle(args.tbox_uri)
    
        FinalizedData = Transform.TransformFile(sourceFileName=args.src, targetFileName=args.dst, sourceParserName='src', targetParserName='dst', sourceMetaData=metadata, oracle=kb)
        args.dst.close()
        
    except Exception as inst :
        logging.exception(inst)
        args.dst.close()
        os.remove(args.dst.name)
    
    else :
        logging.info("Success")
    
