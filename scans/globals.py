def get_non_beam_meas_keys(currents_limit=None):
    return({
        'meas':{
            'Epics': {
                'type': 'resource',
                'config': {
                    'currents':{
                        'allowed_range': currents_limit,
                        'type': 'value'
                    }
                }
            }
        }
    })


def get_beam_meas_keys(*args, **kw_args):
    meas = get_non_beam_meas_keys(*args,**kw_args)
    meas.update({
        'meas':{
            'Epics': {
                'type': 'resource',
                'config': {
                    'storage_ring_current':{
                        'type': 'value'
                    },
                    'diode_current':{
                        'type': 'value'
                    },
                }
            }
        }
    })
    return(meas)