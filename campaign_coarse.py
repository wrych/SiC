'''
Created on Nov 15, 2017

@author: det
'''
import json
import logging
import datetime
import sys
import time
import numpy

import scans
import scanner

def get_serial():
    return(input('Please enter device Serial:\n>'))

def get_time_diff(start_time, last_time=None):
    now_time = datetime.datetime.now()
    print('####################################')
    print('####################################')
    print('Time since start: {0}'.format(now_time - start_time))
    if (last_time is not None):
        print ('Time sinc last Test {0}'.format(now_time - last_time))
    print('####################################')
    print('####################################')
    return(now_time)

if __name__ == '__main__':
    device = sys.argv[1]
    date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    center_v, center_h = [0.0, 0.0]
    start_time = datetime.datetime.now()
    last_time = get_time_diff(start_time, start_time)

    #--------
    #max_bias = 30.0     #This for Diamond
    max_bias = 0.0     #This for SiC
    #-------    
    ## Forward Bias Scan  
    '''  
    scans.ForwardBiasScan(device=device, path_identifier=date_str)
    last_time = get_time_diff(start_time, last_time)
    '''

    ## Reverse Bias Scan 
    '''
    reverse_bias = scans.ReverseBiasScan(device=device, path_identifier=date_str, current_range=2)
    last_time = get_time_diff(start_time, last_time)

    scan_bias = reverse_bias.get_result()    
    if (scan_bias < max_bias):
        max_bias = scan_bias
    '''

    print('###############################')
    print('Determined Bias Setting:{0} V'.format(max_bias))
    print('###############################')
    
    for bias_voltage in numpy.arange(0,10.1,1):
        ## High Resolution 1D Y Scan
        scans.YScan(device=device, 
                                x_offset=center_h+0.25,
                                scan_name='Yscan_13_{0}V'.format(bias_voltage), 
                                scan_kw_args={'y_center':center_v, 'y_range':numpy.arange(.25,-.2501,-0.025)}, 
                                bias=bias_voltage, 
                                path_identifier=date_str)
        last_time = get_time_diff(start_time, last_time)


