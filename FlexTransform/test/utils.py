'''
Created on Nov 9, 2015

@author: ahoying
'''

'''
Test module utilities
'''

import json
import arrow
import csv

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

#Used for test cases where the time is based on the current time
#so that test cases dont fail everytime due to there being a constant change
#in the value between the current time and the values stored in the data.
def dynamic_time_change(data):
    index = 0
    newData = """"""
    reader = csv.reader(data.split(), delimiter=',', quotechar='"')
    for row in reader:
        for x in range(len(row)):
            row[x] = '\"' + row[x] + '\"'
        if (index < 7):
            newData += ','.join(row) + '\n'
        elif (index == 7):
            row[1] = arrow.utcnow().replace(hours=1).format('YYYYMMDDTHHmmss') + 'Z'
            newData += ','.join(row) + '\n'
        else:
            row[1] = arrow.utcnow().replace(days=4).format('YYYYMMDDTHHmmss') + 'Z'
            newData += ','.join(row) + '\n'
        index += 1

    return newData
        