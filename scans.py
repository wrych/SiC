import json
import logging
import datetime
import sys
import time
import numpy

import scanner

def reverse_bias(vmax=95.0, vdelta=1.0):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_bias_voltage': {
					    'type': 'value',
					    'values': numpy.arange(0.0, vmax+0.1, vdelta)
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

def reverse_bias_beam(vmax=0.0, vdelta=0.05):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_bias_voltage': {
					    'type': 'value',
					    'values': numpy.arange(-3.0, vmax+0.01, vdelta)
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
					    'values': numpy.arange(0.0, -4.1, -0.2)
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

def y_scan(y_center=0.0):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_y_translation': {
					    'type': 'value',
					    'values': numpy.arange(0.05, -0.05, -0.0025)+y_center
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

def x_scan(x_center=0.0):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_x_translation': {
					    'type': 'value',
					    'values': numpy.arange(0.05, -0.05, -0.0025)+x_center
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

def xy_scan(x_center=0.0, y_center=0.0, x_range=numpy.arange(0.20, -0.201, -0.025), y_range=numpy.arange(0.20, -0.201, -0.025)):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_x_translation': {
					    'type': 'value',
					    'values': x_range+x_center
				    },
				    'xbpm_y_translation': {
					    'type': 'value',
					    'values': y_range+y_center
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
				    'xbpm_x_translation': {
					    'type': 'value',
					    'values': [0.0,60.0]
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
        kw_args = self.set_kw_args(kw_args, 'photon_energy')
        super(ForwardBiasScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('jj_slits_v_size').set_value(self._kw_beam_size)
        self._obj.get_child('Epics').get_child('jj_slits_h_size').set_value(self._kw_beam_size)
        time.sleep(15)
        self._obj.get_child('Epics').get_child('photon_energy').set_value(self._kw_photon_energy)

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
        self.save_result(result)
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
        self.save_result(result)
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

    def get_result(self, *args, **kw_args):
        result = self._analysis.get_center(*args, **kw_args)
        self.save_result(result)
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

    def get_result(self, *args, **kw_args):
        result = self._analysis.get_center(*args, **kw_args)
        self.save_result(result)
        return(result)


class XYScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        kw_args.update({'name': 'xy_scan'})
        kw_args = self.set_kw_args(kw_args, 'bias')
        kw_args = self.set_kw_args(kw_args, 'beam_size')
        super(XYScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').get_child('shutter_open').set_value(1)
        self._obj.get_child('Epics').get_child('xbpm_x_translation').set_value(-4)
        self._obj.get_child('Epics').get_child('xbpm_y_translation').set_value(-4)
        if (self._kw_beam_size is not None):
            self._obj.get_child('Epics').get_child('jj_slits_v_size').set_value(self._kw_beam_size)
            self._obj.get_child('Epics').get_child('jj_slits_h_size').set_value(self._kw_beam_size)
        time.sleep(15)
        if (self._kw_bias is not None):
            self._obj.get_child('Epics').get_child('xbpm_bias_voltage').set_value(self._kw_bias)

    def post_scan(self):
        self._analysis.plot(x_key='xbpm_x_translation',
                            y_key='xbpm_y_translation',
                            z_key='currents')

    def get_result(self, *args, **kw_args):
        result = self._analysis.get_center_2d(*args, **kw_args)
        self.save_result(result)
        return(result)
