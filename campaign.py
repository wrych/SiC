'''
Created on Nov 15, 2017

@author: det
'''
import numpy
import datetime
import sys
import scans


def get_serial():
    return (input('Please enter device Serial:\n>'))


def get_time_diff(start_time, last_time=None):
    now_time = datetime.datetime.now()
    print('####################################')
    print('####################################')
    print('Time since start: {0}'.format(now_time - start_time))
    if (last_time is not None):
        print('Time sinc last Test {0}'.format(now_time - last_time))
    print('####################################')
    print('####################################')
    return (now_time)


if __name__ == '__main__':
    device = sys.argv[1]
    data_path = '/sls/X05DA/data/e16578/Data1/sicrigi/20180216'
    date_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    center_v, center_h = [0.0, 0.0]
    start_time = datetime.datetime.now()
    last_time = get_time_diff(start_time, start_time)

    max_bias = 2.0
    ## Reverse Bias Scan
    reverse_bias = scans.BiasScan(device=device,
                                  data_path=data_path,
                                  path_identifier=date_str,
                                  name='reverse_bias',
                                  scan_kw_args={
                                    'bias_range' : numpy.arange(0.0, 1.01, 0.1),
                                    'current_range': 2})
    last_time = get_time_diff(start_time, last_time)

    scan_bias = reverse_bias.get_result()
    if (scan_bias < max_bias):
        max_bias = scan_bias


