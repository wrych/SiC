'''
Created on Nov 15, 2017

@author: det
'''
import json

import collectorobject
import scans

Y_ZERO_OFFSET = -1.5
BIAS_VOLTAGE = 10.0

if __name__ == '__main__':
    with open('standard_config.json') as f:
        cfg = json.load(f)
    with open('safe_config.json') as f:
        safe_cfg = json.load(f)
    obj = collectorobject.Resource()
    obj.initialize(cfg)
 
    
