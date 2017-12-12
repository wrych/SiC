import json
import logging
import datetime
import sys
import time
import numpy

import scanner

#def reverse_bias(vmax=60.0, vdelta=0.5):  #for Diamond and 10um SiC
def reverse_bias(vmax=10.0, vdelta=0.25):  #for <2um SiC
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_bias_voltage': {
					    'type': 'value',
					    'values': list(numpy.arange(0.0, vmax+0.1, vdelta))
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
                        'allowed_range': [[-2e-9]*4, [2e-9]*4],
					    'type': 'value'
				    },
				    'diode_current':{
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

#def reverse_bias_beam(vmax=60.0, vdelta=1):  #THIS FOR DIAMOND
def reverse_bias_beam(vmax=0.0, vdelta=0.025):  #THIS FOR SiC PiN
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_bias_voltage': {
					    'type': 'value',
					    'values': list(numpy.arange(-3.0, vmax+0.01, vdelta))
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
					    'type': 'value'
				    },
				    'diode_current':{
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

def forward_bias():
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_bias_voltage': {
					    'type': 'value',
					    'values': list(numpy.arange(0.0, -4.1, -0.2))
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
                        'allowed_range': [[-2.5e-3]*4, [2.5e-3]*4],
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

def y_scan(y_center=0.0, y_range=numpy.arange(0.6, -0.601, -0.005)):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_y_translation': {
					    'type': 'value',
					    'values': list(y_range+y_center)
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
					    'type': 'value'
				    },
				    'diode_current':{
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

def x_scan(x_center=0.0, x_range=numpy.arange(0.6, -0.601, -0.005)):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_x_translation': {
					    'type': 'value',
					    'values': list(x_range+x_center)
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
					    'type': 'value'
				    },
				    'diode_current':{
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

def xy_scan(x_center=0.0, y_center=0.0, x_range=numpy.arange(0.70, -0.701, -0.05), y_range=numpy.arange(0.7, -0.701, -0.05)):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_x_translation': {
					    'type': 'value',
					    'values': list(x_range+x_center)
				    },
				    'xbpm_y_translation': {
					    'type': 'value',
					    'values': list(y_range+y_center)
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
					    'type': 'value'
				    },
				    'diode_current':{
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

def transparancy_scan():
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_y_translation': {
					    'type': 'value',
					    'values': [0.0,-37.0]
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
					    'type': 'value'
				    },
				'diode_current':{
					    'type': 'value'
				    },
				'storage_ring_current':{
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

class TransparancyScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'transparancy_scan'})
        kw_args = self.set_kw_args(kw_args, 'beam_size')
        kw_args = self.set_kw_args(kw_args, 'bias')
        kw_args = self.set_kw_args(kw_args, 'photon_energy')
        super(TransparancyScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('aperature').set_value(self._kw_beam_size)
        time.sleep(20)
        self._obj.get_child('Epics').get_child('photon_energy').set_value(self._kw_photon_energy)
        self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)

    def post_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(0)

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
        kw_args = self.set_kw_args(kw_args, 'current_range')
        super(ReverseBiasScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        if (self._kw_current_range is not None):
            self._obj.get_child('Epics').get_child('current_range').set_value(self._kw_current_range)
        self._obj.get_child('Epics').compute_offset()

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_bias_voltage', y_key='currents')

    def tear_down(self):
        self._obj.get_child('Epics').compute_offset()

    def get_result(self):
        result = self._analysis.get_max_param_value()
        return(result)


class ReverseBiasScanBeam(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'reverse_bias_beam'})
        kw_args = self.set_kw_args(kw_args, 'x_offset')
        kw_args = self.set_kw_args(kw_args, 'y_offset')
        kw_args = self.set_kw_args(kw_args, 'shutter_open')
        super(ReverseBiasScanBeam, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').compute_offset()
        if (self._kw_shutter_open is not None):
            self._obj.get_child('Epics').get_child('shutter_open').set_value(self._kw_shutter_open)
            time.sleep(15)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        if (self._kw_x_offset is not None):
            self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(self._kw_x_offset)
        if (self._kw_y_offset is not None):
            self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(self._kw_y_offset)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_bias_voltage', y_key='currents')

    def tear_down(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(0)
        time.sleep(15)
        self._obj.get_child('Epics').compute_offset()

    def get_result(self):
        result = self._analysis.get_max_param_value()
        return(result)


class YScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'y_scan'})
        kw_args = self.set_kw_args(kw_args, 'bias')
        kw_args = self.set_kw_args(kw_args, 'x_offset')
        super(YScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        time.sleep(15)
        self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(self._kw_x_offset)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_y_translation', y_key='currents')

    def get_result(self, pads):
        result = self._analysis.get_center(pads=pads,
                                           x_key='xbpm_y_translation', 
                                           y_key='currents')
        return(result)


class XScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'x_scan'})
        kw_args = self.set_kw_args(kw_args, 'bias')
        kw_args = self.set_kw_args(kw_args, 'y_offset')
        super(XScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        time.sleep(15)
        self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(self._kw_y_offset)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_x_translation', y_key='currents')

    def get_result(self, pads):
        result = self._analysis.get_center(pads=pads,
                                           x_key='xbpm_x_translation', 
                                           y_key='currents')
        return(result)


class XYScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'xy_scan'})
        kw_args = self.set_kw_args(kw_args, 'bias')
        kw_args = self.set_kw_args(kw_args, 'beam_size')
        kw_args = self.set_kw_args(kw_args, 'photon_energy')
        kw_args = self.set_kw_args(kw_args, 'filter_wheel')
        super(XYScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        if (self._kw_filter_wheel is not None):
            self._obj.get_child('Epics').get_child('filter_wheel').set_value(self._kw_filter_wheel)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        if (self._kw_photon_energy is not None):
            self._obj.get_child('Epics').get_child('photon_energy').set_value(self._kw_photon_energy)
        if (self._kw_beam_size is not None):
            self._obj.get_child('Epics').get_child('aperature').set_value(self._kw_beam_size)
        time.sleep(15)
        if (self._kw_bias is not None):
            self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_x_translation',
                            y_key='xbpm_y_translation',
                            z_key='currents')

    def tear_down(self):
        if (self._kw_filter_wheel is not None):
            self._obj.get_child('Epics').get_child('filter_wheel').set_value(self._kw_filter_wheel)
            time.sleep(15)

    def get_result(self, *args, **kw_args):
        result = self._analysis.get_center_2d(x_key='xbpm_x_translation',
                                              y_key='xbpm_y_translation',
                                              z_key='currents')
        return(result)
