'''
Created on Nov 15, 2017

@author: det
'''
import json

import collectorobject
import scans

Y_ZERO_OFFSET = -6.0

if __name__ == '__main__':
    with open('standard_config.json') as f:
        cfg = json.load(f)
    with open('safe_config.json') as f:
        safe_cfg = json.load(f)
    try:
        obj = collectorobject.Resource()
        obj.initialize(cfg)
        scan = collectorobject.Scan(obj, scans.y_scan(Y_ZERO_OFFSET), './scans')
        scan.scan()
    finally:
        obj.initialize(safe_cfg)
 
    
