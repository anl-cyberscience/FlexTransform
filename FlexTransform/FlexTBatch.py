'''
Created on Apr 12, 2017

@author: taxon
'''
#
# FlexTBatch is a simple wrapper script to FlexT that allows the user to start
# FlexT and send it commands via stdin for processing.  If there are many files to convert,
# the config files only need to be specified once and will also only be loaded once, saving
# a significant amount of time in processing subsequent transforms
#
import argparse
import sys
import logging
import json
from FlexTransform import FlexTransform
#
# process a single command
# valid commands are:
# config {config_name}={config_file}
#   loads a configuration file and stores it as config_name
# transform src_format={src_config_name} src_file={source_file} [src_metadata={metadata_file}] [dest_format={dest_confgi_name} dest_file={output_file}
#   Transforms the source_file from src_config_name into des_file using dest_config_name and optionally the src_metadata.
# quit
#   Terminates the program
# 
def processCommand(flexT,inputData):
    cmd=inputData[0]
    if(cmd=='config'):
        try:
            # config config_id={config_filename}
            if(len(inputData)>2):
                logging.error("Invalid config inputData: "+(" ".join(inputData))+"\n")
                return False
            cvtFormat,filename=inputData[1].split("=")
            if(format in flexT.Parsers):
                logging.error("Format already specified: "+format+"\n")
                return False
            with(open(filename,"r")) as cfg:
                flexT.add_parser(cvtFormat,cfg)
        except Exception as e:
            logging.error("An exception has occurred while adding configuration: "+str(e))

    elif(cmd=='list_configs'):
        print(json.JSONEncoder().encode({ 'configs': list(flexT.Parsers.keys()) }))
    elif(cmd=='transform'):
        # src_format={format} src_file={source_filename} src_metadata={source_metdata_filename} dest=format={dest_format} dest_file={dest_filename}
        try:
            data={}
            hasError=False
            for kv in inputData[1:]:
                key,value=kv.split("=")
                if(key in data):
                    logging.error("Invalid transform inputData - duplicate key: "+key+"\n")
                    hasError=True
                data[key]=value
            if(hasError):
                return False
            required={'src_format','src_file','dest_format','dest_file'}
            optional={'src_metadata'}
            hasAllRequired=data.keys() >= required
            extraKeys=data.keys() - required -optional
            if(len(extraKeys)>0):
                logging.error("Unsupported keys in transform: "+extraKeys+"\n")
                return False
            if(not hasAllRequired):
                logging.error("Missing required keys in transform: "+(required - data.keys())+"\n")
                return False
            with open(data['src_file'],"r") as input_file:
                with open(data['dest_file'],"w") as output_file:
                    try:
                        flexT.transform(source_file=input_file,
                                        source_parser_name=data['src_format'],
                                        target_parser_name=data['dest_format'],
                                        target_file=output_file,
                                        source_meta_data=data.get(data.get('src_metadata')))
                    except Exception as e:
                        logging.error("An exception has occurred while transforming file: "+str(e))
                    return False
        except Exception as e:
            logging.error("An exception has occurred while setting up for transform: "+str(e))
    elif(cmd=='quit'):
        return True
    else:
        logging.error("Unknown command: "+cmd)

class LessThanFilter(logging.Filter):
    def __init__(self, level):
        self._level = level
        logging.Filter.__init__(self)

    def filter(self, rec):
        return rec.levelno < self._level

def initializeLogging(stdout_level):
    log = logging.getLogger()
    log.setLevel(logging.NOTSET)

    sh_out = logging.StreamHandler(stream=sys.stdout)
    sh_out.setLevel(stdout_level)
    sh_out.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
    sh_out.addFilter(LessThanFilter(logging.WARNING))
    log.addHandler(sh_out)
    
    sh_err = logging.StreamHandler(stream=sys.stderr)
    sh_err.setLevel(logging.WARNING)
    sh_err.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
    log.addHandler(sh_err)

def main():
    parser = argparse.ArgumentParser(
    description="Transform a source file's syntax and schema to the target file document type")
    parser.add_argument('--delimiter',
                        help='Delimiter used for input lines (default \'\t\')',
                        metavar='DELIM_CHAR',
                        default='\t',
                        required=False)
    parser.add_argument('--output-done-markers',
                        dest='output_markers',
                        help='Output {err-done} and {out-done} when processing a command is complete.  Useful if a program is controlling batch execution.',
                        action='store_true',
                        default=False,
                        required=False)
    parser.add_argument('--stdout-log-level',
                        dest='stdout_level',
                        help='Log level to output to stdout.  (stderr will always be WARNING)',
                        choices=['NOTSET','DEBUG','INFO'],
                        default='NOTSET',
                        required=False)
    args = parser.parse_args()

    initializeLogging(args.stdout_level)
    flexT = FlexTransform.FlexTransform()
    done=False
    while(not done):
        try:
            inputData=sys.stdin.readline()
            cmd=inputData.strip().split(args.delimiter)
            done=processCommand(flexT,cmd)
        except Exception as e:
            logging.error("An exception has occurred while processing input: "+str(e))
        if(args.output_markers):
            sys.stderr.write('{err-done}\n')
            sys.stderr.flush()
            sys.stdout.write('{out-done}\n')
            sys.stdout.flush()

if __name__ == '__main__':
    main()
