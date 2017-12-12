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
    device = sys.argv[1]#get_serial()
    #while(input('Is the device serial "{0}"?\nEnter "yes" to confirm.\n>'.format(device)) != 'yes'):
    #    device = get_serial()
    date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    center_v, center_h = [0.0, 0.0]
    start_time = datetime.datetime.now()
    last_time = get_time_diff(start_time, start_time)

#--------
    #max_bias = 30.0     #This for Diamond
    max_bias = 0.0     #This for SiC
#-------    

    ## Forward Bias Scan    
    scans.ForwardBiasScan(device=device, path_identifier=date_str)
    last_time = get_time_diff(start_time, last_time)
    ## Reverse Bias Scan 
    reverse_bias = scans.ReverseBiasScan(device=device, path_identifier=date_str, current_range=2)
    last_time = get_time_diff(start_time, last_time)
    scan_bias = reverse_bias.get_result()
    if (scan_bias < max_bias):
        max_bias = scan_bias
    print('###############################')
    print('Determined Bias Setting:{0} V'.format(max_bias))
    print('###############################')
    

    ## Transparancy Scan
    for index, beam_size in enumerate([0.010, 0.050, 0.200]):
        scans.TransparancyScan(device=device, 
                           diode_pool=5,
                           beam_size=beam_size,
                           bias=max_bias, 
                           scan_name='trans_scan_{0:0>5}eV'.format(photon_energy),
                           path_identifier=date_str)
    last_time = get_time_diff(start_time, last_time)
   
#---
    
    ## Start OF CENTERING
    xy_scan_inst = scans.XYScan(device=device, 
                        bias=max_bias, 
                        path_identifier=date_str,
                        scan_name='xy_centering_1',
                        scan_kw_args={'x_center': center_h, 
                                      'y_center': center_v, 
                                      'x_range': numpy.arange(0.4,-0.41,-0.04), 
                                      'y_range': numpy.arange(0.4,-0.41,-0.04)})   
    last_time = get_time_diff(start_time, last_time)

#---If broken, do not center!
    center_h, center_v = xy_scan_inst.get_result()

    ## 
    xy_scan_inst = scans.XYScan(device=device, 
                        bias=max_bias, 
                        path_identifier=date_str,
                        scan_name='xy_centering_2',
                        scan_kw_args={'x_center': center_h, 
                                      'y_center': center_v, 
                                      'x_range': numpy.arange(0.125,-0.1251,-0.01), 
                                      'y_range': numpy.arange(0.125,-0.1251,-0.01)}) 
    last_time = get_time_diff(start_time, last_time)

#---If broken, do not center!
    center_h, center_v = xy_scan_inst.get_result()

    ## END OF CENTERING, with 10um resolution!
    
    ## CCE per pad
    for pad_index in range(4):
        x_offsets = numpy.array([-0.5,0.5,-0.5,0.5])+center_h
        y_offsets = numpy.array([-0.5,-0.5,0.5,0.5])+center_v
        scans.ReverseBiasScanBeam(device=device, 
                                     path_identifier=date_str,
                                     shutter_open=1,
                                     scan_name='cce_{0}'.format(pad_index+1),
                                     x_offset=x_offsets[pad_index],
                                     y_offset=y_offsets[pad_index])
    
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
    ## XY Fine Scan
    
    ## XY Very Coarse Scan
    scans.XYScan(device=device,
                        beam_size=0.2,
                        bias=max_bias, 
                        path_identifier=date_str,
                        scan_name='xy_scan_very_coarse',
                        scan_kw_args={'x_center': center_h, 
                                      'y_center': center_v, 
                                      'x_range': numpy.arange(3.5,-3.51,-0.30), 
                                      'y_range': numpy.arange(2.5,-2.51,-0.30)})
    last_time = get_time_diff(start_time, last_time)

    '''
#---------------OVERNIGHT!!
    xy_scan_inst = scans.XYScan(device=device, 
                        bias=max_bias, 
                        beam_size=-0.130,
                        path_identifier=date_str,
                        scan_name='xy_centering_HR',
                        scan_kw_args={'x_center': center_h, 
                                      'y_center': center_v, 
                                      'x_range': numpy.arange(0.625,-0.6251,-0.01), 
                                      'y_range': numpy.arange(0.625,-0.6251,-0.01)}) 
    last_time = get_time_diff(start_time, last_time)
    
    ## FilterWheel per pad
    
    filters = {
                0:'Air',
                1:'Al_2e2_um',
                2:'Al_5e2_um',
                3:'Al_1e3_um',
                4:'Al_2e3_um',
                5:'Al_5e3_um',
                6:'Fe_25_um',
                7:'Cu_25_um',
                8:'Zn__um',
                9:'Mo_25_um',
                10:'Ag_25_um',
                11:'Au_25_um',
                }
    for filter_key in filters:
        scans.XYScan(device=device, 
                    filter_wheel=filter_key,
                    bias=max_bias, 
                    beam_size=0.5,
                    path_identifier=date_str,
                    scan_name='linearity_{0}'.format(filters[filter_key]),
                    scan_kw_args={'x_center': center_v, 
                                 'y_center': center_h, 
                                  'x_range': numpy.array([0.5, 0.0, -0.5, 60]), 
                                  'y_range': numpy.array([0.5, 0.0, -0.5])})
    last_time = get_time_diff(start_time, last_time)
    '''
    

