import numpy

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

def xy_scan(x_center=0.0, y_center=0.0, x_range=numpy.arange(0.25, -0.25, -0.025), y_range=numpy.arange(0.25, -0.25, -0.025)):
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
