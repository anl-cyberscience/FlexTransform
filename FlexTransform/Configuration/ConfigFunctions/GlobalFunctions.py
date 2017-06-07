"""
@author: cstrasburg
"""

import logging
import os.path
import re

import arrow

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
    def register_functions(cls):
        for FunctionName, RequiredArgs in cls.__FunctionNames.items():
            ConfigFunctionManager.register_function(FunctionName, RequiredArgs, 'GlobalFunctions')

    def Execute(self, function_name, args):
        value = None

        if function_name not in self.__FunctionNames:
            raise Exception('FunctionNotDefined',
                            'Function %s is not defined in GlobalFunctions' % (function_name))

        elif function_name == 'getFileCreationDate':
            if 'fileName' in args:
                try:
                    rawctime = os.path.getctime(args['fileName'])
                    ''' Convert to given time format '''
                    if 'fieldDict' in args and 'dateTimeFormat' in args['fieldDict'] and \
                            args['fieldDict']['dateTimeFormat'] == 'unixtime':
                        value = str(arrow.get(rawctime).timestamp)
                    else:
                        value = arrow.get(rawctime).format(args['fieldDict']['dateTimeFormat'])
                except OSError as e:
                    self.logging.warning("Could not get file ctime for {}: {}".format(args['fileName'], e))

        elif function_name == 'getFileUUID':
            if 'fileName' in args and args['fileName']:
                fileName = args['fileName']
                baseName = os.path.basename(fileName)
                p = re.compile(args['functionArg'])
                result = p.match(baseName)
                if result is not None:
                    value = result.group(1)
                else:
                    value = None
                    self.logging.warning("getFileUUID: could not extract UUID from filename {} using regex {}".format(baseName,args['functionArg']))
            if value is None:
                self.logging.warning("getFileUUID: no fileName provided in args(); could not extract UUID.")

        return value
