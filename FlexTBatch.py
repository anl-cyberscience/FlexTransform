'''
Created on Apr 12, 2017

@author: taxon
'''
#
# FlexTBatch is a simple wrapper script to FlexT that allows the user to start
# FLexT and send it commands via stdin for processing.  If there are many files to convert,
# the config files only need to be specified once and will also only be loaded once, saving
# a significant amount of time in processing subsequent transforms
#
# This class is here for running FlexTBatch within the Eclipse environment as FlexTransform.FlextBatch.py
# is not able to be run within Eclipse.
from FlexTransform import FlexTBatch

def main():
    FlexTBatch.main()

if __name__ == '__main__':
   FlexTBatch.main()
