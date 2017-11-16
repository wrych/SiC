import numpy

def bias():
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_bias_voltage': {
					    'type': 'value',
					    'values': numpy.arange(-4.0, 10.0, 0.1)
				    }
			    }
		    }
	    },
	    'meas':{
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'currents':{
                        'allowed_range': [[None]*4, [-10e-9]*4],
					    'type': 'value'
				    }
			    }
		    }
	    }
    })

def y_scan(y_center):
    return({
	    'scan': {
		    'Epics': {
			    'type': 'resource',
			    'config': {
				    'xbpm_y_translation': {
					    'type': 'value',
					    'values': numpy.arange(-0.5, 0.5, 0.01)+y_center
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
				    }
			    }
		    }
	    }
    })
