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
    
    center_v, center_h = [0.0, 0.0]
    start_time = datetime.datetime.now()
    last_time = get_time_diff(start_time, start_time)

    #--------
    #max_bias = 30.0     #This for Diamond
    max_bias = 2.0     #This for SiC
    #-------    

    ## Start OF CENTERING
    date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    xy_scan_inst = scans.XYScan(device=device, 
                        bias=max_bias, 
                        path_identifier=date_str,
                        scan_name='xy_centering_1',
                        scan_kw_args={'x_center': center_h, 
                                      'y_center': center_v, 
                                      'x_range': numpy.arange(0.4,-0.41,-0.04), 
                                      'y_range': numpy.arange(0.4,-0.41,-0.04)})   
    last_time = get_time_diff(start_time, last_time)
    center_h, center_v = xy_scan_inst.get_result()

    ## Forward Bias Scan  
    for max_bias in numpy.arange(0,3.01,0.3):
        date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
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
        

        ## Transparancy Scan
        
        scans.TransparancyScan(device=device,
                           beam_size=0,#ignored
                           bias=max_bias, 
                           scan_name='trans_scan',
                           path_identifier=date_str,
                           scan_kw_args={'out_of_beam_value':-37.0})
        last_time = get_time_diff(start_time, last_time)
        

        ## Linearity Scan
        for xbpm_range in [2,1,0]:
            scans.LinearityScan(device=device,
                                scan_name='linearity_xbpmrange_{0}'.format(xbpm_range),
                                path_identifier=date_str,
                                x_offset = center_h+.25, 
                                y_offset = center_v+.25)
            last_time = get_time_diff(start_time, last_time)
        
        ## High Resolution 1D Y Scan
        scans.YScan(device=device, 
                                x_offset=center_h+0.25,
                                scan_name='Yscan_13', 
                                scan_kw_args={'y_center':center_v}, 
                                bias=max_bias, 
                                path_identifier=date_str)
        last_time = get_time_diff(start_time, last_time)
          
         
        scans.YScan(device=device, 
                                x_offset=center_h-0.25,
                                scan_name='Yscan_42', 
                                scan_kw_args={'y_center':center_v}, 
                                bias=max_bias, 
                                path_identifier=date_str)
        last_time = get_time_diff(start_time, last_time)

        ## High Resolution 1D X Scan
        scans.XScan(device=device, 
                                y_offset=center_v+0.25, 
                                scan_name='Xscan_12', 
                                scan_kw_args={'x_center':center_h}, 
                                bias=max_bias, 
                                path_identifier=date_str)
        last_time = get_time_diff(start_time, last_time)


        scans.XScan(device=device, 
                                y_offset=center_v-0.25, 
                                scan_name='Xscan_43', 
                                scan_kw_args={'x_center':center_h}, 
                                bias=max_bias, 
                                path_identifier=date_str)
        last_time = get_time_diff(start_time, last_time)
           

