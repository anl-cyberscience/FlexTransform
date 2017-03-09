'''
Created on Jun 17, 2015

@author: ahoying
'''

from FlexTransform import FlexTransform
from FlexTransform.OntologyOracle import Oracle
import logging
import rdflib

import argparse
import os
import sys
import json


# Configure logging to send INFO, DEGUB and TRACE messages to stdout and all other logs to stderr
# Based on code from http://stackoverflow.com/questions/2302315/how-can-info-and-debug-logging-message-be-sent-to-stdout-and-higher-level-messag
class LessThenFilter(logging.Filter):
    def __init__(self, level):
        self._level = level
        logging.Filter.__init__(self)

    def filter(self, rec):
        return rec.levelno < self._level


def main():
    log = logging.getLogger()
    log.setLevel(logging.NOTSET)

    sh_out = logging.StreamHandler(stream=sys.stdout)
    sh_out.setLevel(logging.DEBUG)
    sh_out.setFormatter(logging.Formatter('%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s'))
    sh_out.addFilter(LessThenFilter(logging.WARNING))
    log.addHandler(sh_out)

    sh_err = logging.StreamHandler(stream=sys.stderr)
    sh_err.setLevel(logging.WARNING)
    sh_err.setFormatter(logging.Formatter('%(name)s (%(pathname)s:%(lineno)d) %(levelname)s:%(message)s'))
    log.addHandler(sh_err)

    parser = argparse.ArgumentParser(
        description="Transform a source file's syntax and schema to the target file document type")
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
    parser.add_argument('--source-schema-IRI',
                        help='The ontology IRI for the destination',
                        required=False)
    parser.add_argument('--destination-schema-IRI',
                        help='The ontology IRI for the destination',
                        required=False)

    args = parser.parse_args()

    try:
        Transform = FlexTransform.FlexTransform()
        Transform.AddParser('src', args.src_config)
        Transform.AddParser('dst', args.dst_config)

        metadata = None

        if args.src_metadata:
            metadata = json.load(args.src_metadata)

        kb = None

        if args.tbox_uri:
            if args.destination_schema_IRI:
                kb = Oracle(args.tbox_uri, rdflib.URIRef(args.destination_schema_IRI))
            else:
                logging.warning(
                    "Ontology file specified, but no destination schema IRI is given.  Ontology will not be used.")

        FinalizedData = Transform.TransformFile(
            sourceFileName=args.src,
            targetFileName=args.dst,
            sourceParserName='src',
            targetParserName='dst',
            sourceMetaData=metadata,
            oracle=kb)
        args.dst.close()

    except Exception as inst:
        log.error(inst)
        args.dst.close()
        os.remove(args.dst.name)
        exit(1)

    else:
        log.info("Success")
        exit(0)

if __name__ == '__main__':
    main()
