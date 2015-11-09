'''
Created on Nov 9, 2015

@author: ahoying
'''

'''
Test module utilities
'''

import json

def deep_sort(obj):
    """
    Recursively sort list or dict nested lists
    Based on code from http://stackoverflow.com/questions/18464095/how-to-achieve-assertdictequal-with-assertsequenceequal-applied-to-values
    """

    if isinstance(obj, dict):
        _sorted = {}
        for key in sorted(obj):
            _sorted[key] = deep_sort(obj[key])

    elif isinstance(obj, list):
        new_list = []
        isdict = False
        for val in obj:
            if (not isdict and isinstance(val, dict)) :
                isdict = True
                
            new_list.append(deep_sort(val))
            
        if (isdict) :
            # Sort lists of dictionaries by the hash value of the data in the dictionary
            _sorted = sorted(new_list, key=lambda d: hash(json.dumps(d, ensure_ascii = True, sort_keys = True)))                
        else :
            _sorted = sorted(new_list)

    else:
        _sorted = obj

    return _sorted
        