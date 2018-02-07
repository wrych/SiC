'''
Created on Nov 15, 2017

@author: det
'''
import json
import datetime
import sys
import os
import time

import collectorobject
import scans

def calculate_current(epics, index):
    value = getattr(epics, 'get_mean_value_{0}'.format(index))()
    current_range = [2.5e-3, 2.5e-6, 2.5e-9][epics.get_current_range()]
    resolution = [16, 24][epics.get_resolution()]
    current = float(2*current_range)/(2**resolution-1)*value
    return(current)


if __name__ == '__main__':
    with open('standard_config.json') as f:
        cfg = json.load(f)
    with open('safe_config.json') as f:
        safe_cfg = json.load(f)
    obj = collectorobject.Resource()
    obj.initialize(cfg)
    
    device = sys.argv[1]

    date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')

    folder = '/import/exchange/mx/blcntl/6S/X06SA-IDL/devl/xbpm/180206_SiCXBPM/data/{0}'.format(device)

    try:
        os.mkdir(folder)
    except:
        pass

    file_path = os.path.join(folder,'{0}.log'.format(date_str))

    while True:
        date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S.%f')
        #currents = obj.get_child('Epics').get_currents()
        currents = [calculate_current(obj.get_child('Epics'),ch) for ch in range(4)]
        current_str = ' '.join([str(curr) for curr in currents])
        print(date_str)        
        print(current_str)
        with open(file_path, 'a') as f:
            f.write('{0} {1}\n'.format(date_str, current_str))
        time.sleep(.1)
        
 
    
