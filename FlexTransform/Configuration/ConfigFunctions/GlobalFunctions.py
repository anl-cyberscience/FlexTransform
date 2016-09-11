'''
Created on Mar 13, 2015

@author: ahoying
'''

import pytz
import time
import datetime
import logging
import uuid
import os.path
import re

from FlexTransform.Configuration.ConfigFunctions import ConfigFunctionManager


class GlobalFunctions(object):
    """
    Contains Configuration functions that multiple configuration files can use:
    """

    '''
    The _FunctionNames dictionary should contain each function name understood by this class. Each is 
    mapped to a list with required fields to be passed in the args dictionary, or None if no args are required.
    
    Allowed fields for the Args dictionary:
    
    fieldName       - Optional - The name of the field being processed

    fileName        - Optional - The name of the loaded file (full path)
    
    functionArg     - Optional - The string between the '(' and ')' in the function definition

    fieldDict       - Optional - The dictionary of the field where this method is defined

    '''
    
    __FunctionNames = {
                          'getFileCreationDate': ['fileName'],
                          'getFileUUID': ['fileName', 'functionArg'],
                      }

    def __init__(self):
        """
        Constructor
        """
        self.logging = logging.getLogger('FlexTransform.Configuration.ConfigFunctions.GlobalFunctions')
        
    @classmethod
    def RegisterFunctions(cls):
        for FunctionName, RequiredArgs in cls.__FunctionNames.items():
            ConfigFunctionManager.RegisterFunction(FunctionName, RequiredArgs, 'GlobalFunctions')
        
    def Execute(self, function_name, args):
        """
        Execute the specific called function with the supplied args
        """
        
        value = None
         
        if function_name not in self.__FunctionNames:
            raise Exception('FunctionNotDefined',
                            'Function %s is not defined in GlobalFunctions' % (function_name))
        
        elif function_name == 'getFileCreationDate':
            if 'fileName' in args:
                try: 
                    rawctime = os.path.getctime(args['fileName'])
                    ''' Convert to given time format '''
                    if 'fieldDict' in args and \
                        'dateTimeFormat' in args['fieldDict'] and \
                        args['fieldDict']['dateTimeFormat'] == 'unixtime':
                        value = '%i' % time.mktime(datetime.datetime.utcfromtimestamp(rawctime).timetuple())
                    else:
                        value = datetime.datetime.fromtimestamp(rawctime, tz=pytz.utc).strftime(args['fieldDict']['dateTimeFormat'])
                except OSError as e:
                    self.logging.warn("Could not get file ctime for {}: {}".format(fileName, e))

        elif function_name == 'getFileUUID':
            if 'fileName' in args:
                fileName = args['fileName']
                baseName = os.path.basename(fileName)
                p = re.compile(args['functionArg'])
                result = p.match(baseName)
                if result is not None:
                    value = result.group(1)
                else:
                    value = None
                    self.logging.warn("getFileUUID: could not extract UUID from filename {} using regex {}".format(baseName,args['functionArg']))
            if value is None:
                self.logging.warn("getFileUUID: no fileName provided in args(); could not extract UUID.")

        return value