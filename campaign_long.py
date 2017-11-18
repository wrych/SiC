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
    print('Time since start: {0}'.format(now_time - start_time))
    if (last_time is not None):
        print ('Time sinc last Test {0}'.format(now_time - last_time))
    return(now_time)

if __name__ == '__main__':
    device = get_serial()
    while(input('Is the device serial "{0}"?\nEnter "yes" to confirm.\n>'.format(device)) != 'yes'):
        device = get_serial()
    date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    max_bias = 20.0
    start_time = datetime.datetime.now()
    # Forward Bias Scan    
    scans.ForwardBiasScan(device=device, path_identifier=date_str)
    last_time = get_time_diff(start_time, start_time)
    # Reverse Bias Scan 
    scans.ReverseBiasScan(device=device, path_identifier=date_str, current_range=2)
    last_time = get_time_diff(start_time, last_time)
    #max_bias = scans[-1].get_result()
    # XY Coarse Scan for finding center
    xy_scan_inst = scans.XYScan(device=device, bias=max_bias, path_identifier=date_str)
    center_h, center_v = xy_scan_inst.get_result()
    last_time = get_time_diff(start_time, last_time)
    # CCE per pad
    for pad_index in range(4):
        x_offsets = [-0.5,0.5,-0.5,0.5]
        y_offsets = [-0.5,-0.5,0.5,0.5]
        scans.ReverseBiasScanBeam(device=device, 
                                     path_identifier=date_str,
                                     shutter_open=1,
                                     scan_name='cce_{0}'.format(pad_index+1),
                                     x_offset=x_offsets[pad_index],
                                     y_offset=y_offsets[pad_index])
    last_time = get_time_diff(start_time, last_time)
    for bias in [-2.5,-2.25,-2.0,0.0,20.0,90.0]:
        # High Resolution 1D Y Scan
        scans.YScan(device=device, 
                                x_offset=0.5, 
                                scan_name='y_scan_fine_bias_{0}V'.format(bias),
                                scan_kw_args={'y_center':center_v}, 
                                bias=bias, 
                                path_identifier=date_str)
        last_time = get_time_diff(start_time, last_time)
        # High Resolution 1D X Scan
        scans.XScan(device=device, 
                                y_offset=0.5, 
                                scan_name='x_scan_fine_bias_{0}V'.format(bias),
                                scan_kw_args={'x_center':center_h}, 
                                bias=bias, 
                                path_identifier=date_str)
        last_time = get_time_diff(start_time, last_time)
        # XY Fine Scan
        scans.XYScan(device=device, 
                            bias=bias, 
                            path_identifier=date_str,
                            scan_name='xy_scan_fine_bias_{0}V'.format(bias),
                            scan_kw_args={'x_center':center_v, 
                                          'y_center': center_h, 
                                          'x_range': numpy.arange(0.20,-0.201,-0.01), 
                                          'y_range': numpy.arange(0.20,-0.201,-0.01)})
        last_time = get_time_diff(start_time, last_time)
    # XY Very Coarse Scan
    scans.XYScan(device=device,
                        beam_size=0.2,
                        bias=max_bias, 
                        path_identifier=date_str,
                        scan_name='xy_scan_very_coarse',
                        scan_kw_args={'x_center':center_v, 
                                      'y_center': center_h, 
                                      'x_range': numpy.arange(2.5,-2.51,-0.20), 
                                      'y_range': numpy.arange(1.5,-1.51,-0.20)})
    last_time = get_time_diff(start_time, last_time)
    # Transparancy Scan
    for photon_energy in [5600.0, 8000.0, 12400.0, 17500.0]:
        scans.YScan(device=device, 
                           beam_size=0.2,
                           photon_energy=photon_energy, 
                           bias=max_bias, 
                           path_identifier=date_str)
    last_time = get_time_diff(start_time, last_time)
    

