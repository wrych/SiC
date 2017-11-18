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

import scanner

class TransparancyScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'transparancy_scan'})
        kw_args = self.set_kw_args(kw_args, 'photon_energy', default=0.0)
        super(ForwardBiasScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('photon_energy').set_value(self._kw_photon_energy)
        sys.exit()

    def post_scan(self):
        pass #self._analysis.plot(x_key='photon_energy', y_key='currents')

    def tear_down(self):
        pass

class ForwardBiasScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'forward_bias'})
        super(ForwardBiasScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').set_current_range(0)
        self._obj.get_child('Epics').compute_offset()

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_bias_voltage', y_key='currents')

    def tear_down(self):
        self._obj.get_child('Epics').compute_offset()


class ReverseBiasScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'reverse_bias'})
        kw_args = self.set_kw_args(kw_args, 'current_range', default=2)
        super(ReverseBiasScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').set_current_range(self._kw_current_range)
        self._obj.get_child('Epics').compute_offset()

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_bias_voltage', y_key='currents')

    def tear_down(self):
        self._obj.get_child('Epics').compute_offset()

    def get_result(self):
        result = self._analysis.get_max_param_value()
        self.save_result(result)
        return(result)


class ReverseBiasScanBeam(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'reverse_bias_beam'})
        kw_args = self.set_kw_args(kw_args, 'x_offset', default=0.0)
        kw_args = self.set_kw_args(kw_args, 'y_offset', default=0.0)
        kw_args = self.set_kw_args(kw_args, 'shutter_open', default=0)
        super(ReverseBiasScanBeam, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').compute_offset()
        self._obj.get_child('Epics').get_child('shutter_open').set_value(self._kw_shutter_open)
        time.sleep(15)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(self._kw_x_offset)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(self._kw_y_offset)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_bias_voltage', y_key='currents')

    def tear_down(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(0)
        time.sleep(15)
        self._obj.get_child('Epics').compute_offset()

    def get_result(self):
        result = self._analysis.get_max_param_value()
        self.save_result(result)
        return(result)


class YScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'y_scan'})
        kw_args = self.set_kw_args(kw_args, 'bias', default=0.0)
        kw_args = self.set_kw_args(kw_args, 'x_offset', default=0.0)
        super(CoarseYScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        time.sleep(15)
        self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(self._kw_x_offset)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_y_translation', y_key='currents')

    def get_result(self, *args, **kw_args):
        result = self._analysis.get_center(*args, **kw_args)
        self.save_result(result)
        return(result)


class XScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'x_scan'})
        kw_args = self.set_kw_args(kw_args, 'bias', default=0.0)
        kw_args = self.set_kw_args(kw_args, 'y_offset', default=0.0)
        super(CoarseXScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        time.sleep(15)
        self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(self._kw_y_offset)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_x_translation', y_key='currents')

    def get_result(self, *args, **kw_args):
        result = self._analysis.get_center(*args, **kw_args)
        self.save_result(result)
        return(result)


class XYScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'xy_scan'})
        kw_args = self.set_kw_args(kw_args, 'bias', default=0.0)
        kw_args = self.set_kw_args(kw_args, 'beam_size', default=0.0)
        super(XYScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('jj_slits_v_size').set_value(self._kw_beam_size)
        self._obj.get_child('Epics').get_child('jj_slits_h_size').set_value(self._kw_beam_size)
        time.sleep(15)
        self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_x_translation',
                            y_key='xbpm_y_translation',
                            z_key='currents')

    def get_result(self, *args, **kw_args):
        result = self._analysis.get_center_2d(*args, **kw_args)
        self.save_result(result)
        return(result)


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
    scans = []
    max_bias = 20.0
    start_time = datetime.datetime.now()
    # Forward Bias Scan    
    #scans.append(ForwardBiasScan(device=device, path_identifier=date_str))
    last_time = get_time_diff(start_time, start_time)
    # Reverse Bias Scan 
    #scans.append(ReverseBiasScan(device=device, path_identifier=date_str))
    last_time = get_time_diff(start_time, last_time)
    #max_bias = scans[-1].get_result()
    # XY Coarse Scan for finding center
    scans.append(XYScan(device=device, bias=max_bias, path_identifier=date_str))
    center_h, center_v = scans[-1].get_result()
    last_time = get_time_diff(start_time, last_time)
    # CCE per pad
    for pad_index in range(4):
        x_offsets = [-0.5,0.5,-0.5,0.5]
        y_offsets = [-0.5,-0.5,0.5,0.5]
        scans.append(ReverseBiasScanBeam(device=device, 
                                     path_identifier=date_str,
                                     shutter_open=1,
                                     scan_name='cce_{0}'.format(pad_index+1),
                                     x_offset=x_offsets[pad_index],
                                     y_offset=y_offsets[pad_index]))
    last_time = get_time_diff(start_time, last_time)
    # High Resolution 1D Y Scan
    scans.append(YScan(device=device, 
                            x_offset=0.5, 
                            scan_kw_args={'x_center':center_v}, 
                            bias=max_bias, 
                            path_identifier=date_str))
    last_time = get_time_diff(start_time, last_time)
    # High Resolution 1D X Scan
    scans.append(XScan(device=device, 
                            y_offset=0.5, 
                            scan_kw_args={'y_center':center_h}, 
                            bias=max_bias, 
                            path_identifier=date_str))
    last_time = get_time_diff(start_time, last_time)
    # XY Fine Scan
    scans.append(XYScan(device=device, 
                        bias=max_bias, 
                        path_identifier=date_str,
                        scan_name='xy_scan_fine',
                        scan_kw_args={'x_center':center_v, 
                                      'y_center': center_h, 
                                      'x_range': numpy.arange(0.125,-0.1251,-0.01), 
                                      'y_range': numpy.arange(0.125,-0.1251,-0.01)}))
    last_time = get_time_diff(start_time, last_time)
    # XY Very Coarse Scan
    scans.append(XYScan(device=device,
                        beam_size=0.2,
                        bias=max_bias, 
                        path_identifier=date_str,
                        scan_name='xy_scan_very_coarsee',
                        scan_kw_args={'x_center':center_v, 
                                      'y_center': center_h, 
                                      'x_range': numpy.arange(2.5,-2.51,-0.20), 
                                      'y_range': numpy.arange(1.5,-1.51,-0.20)}))
    last_time = get_time_diff(start_time, last_time)
    # Transparancy Scan
    for photon_energy in [5600.0, 8000.0, 12400.0, 17500.0]:
        scans.append(YScan(device=device, 
                           beam_size=0.2,
                           photon_energy=photon_energy, 
                           bias=max_bias, 
                           path_identifier=date_str))
    last_time = get_time_diff(start_time, last_time)
    

