'''
Created on Mar 13, 2015

@author: ahoying
'''

import FlexTransform.SchemaParser

from .TransformFunctionManager import TransformFunctionManager
from .GlobalFunctions import GlobalFunctions
from .CFM13Functions import CFM13Functions
from .CFM20Functions import CFM20Functions
from .STIXFunctions import STIXFunctions

GlobalFunctions.RegisterFunctions()