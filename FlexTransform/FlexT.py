"""
Created on Jun 17, 2015

@author: ahoying
"""

import argparse
import json
import logging
import os
import sys
import traceback

import rdflib

from FlexTransform import FlexTransform
from FlexTransform.OntologyOracle import Oracle


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
    parser.add_argument('--trace-src-field',
                        help='Given the name of a field from the source schema, will output trace messages to log.trace() as it is processed',
                        action='append',
                        default=[],
                        required=False)
    parser.add_argument('--trace-dst-field',
                        help='Given the name of a field from the dest schema, will output trace messages to log.trace() as it is processed',
                        action='append',
                        default=[],
                        required=False)
    parser.add_argument('--trace-src-IRI',
                        help='Given the name of an IRI from the source schema, will output trace messages to log.trace() as it is processed',
                        action='append',
                        default=[],
                        required=False)
    parser.add_argument('--trace-dst-IRI',
                        help='Given the name of an IRI from the dest schema, will output trace messages to log.trace() as it is processed',
                        action='append',
                        default=[],
                        required=False)
    parser.add_argument('--logging-level', '-l',
                        help="Set the output level for the logger.  Acceptable values: debug, info, warning, error, critical",
                        required=False)

    args = parser.parse_args()
    try:
        if args.logging_level:
            if args.logging_level.lower() == "debug":
                log.setLevel(logging.DEBUG)
            elif args.logging_level.lower() == "info":
                log.setLevel(logging.INFO)
            elif args.logging_level.lower() == "warning":
                log.setLevel(logging.WARNING)
            elif args.logging_level.lower() == "error":
                log.setLevel(logging.ERROR)
            elif args.logging_level.lower() == "critical":
                log.setLevel(logging.CRITICAL)
        transform = FlexTransform.FlexTransform(source_fields=args.trace_src_field,
                                                source_iri=args.trace_src_IRI,
                                                destination_fields=args.trace_dst_field,
                                                destination_iri=args.trace_dst_IRI,
                                                logging_level=logging.NOTSET)

        transform.add_parser('src', args.src_config)
        transform.add_parser('dst', args.dst_config)

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

        FinalizedData = transform.transform(
            source_file=args.src,
            target_file=args.dst,
            source_parser_name='src',
            target_parser_name='dst',
            source_meta_data=metadata,
            oracle=kb)
        args.dst.close()

    except Exception as inst:
        log.error(inst)
        ''' For debugging - capture to log.debug instead? '''
        traceback.print_exc()
        args.dst.close()
        os.remove(args.dst.name)
        exit(1)

    else:
        log.info("Success")
        exit(0)

if __name__ == '__main__':
    main()
