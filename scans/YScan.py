import logging

import scans.globals
import scanner


class BiasScan(scanner.UserScan):
    def __init__(self, *args, **kw_args):
        super(BiasScan, self).__init__(*args, **kw_args)

    def pre_scan(self):
        self._obj.get_child('Epics').compute_offset()

    def tear_down(self):
        self._obj.get_child('Epics').compute_offset()

    def get_result(self):
        try:
            result = self._analysis.get_max_param_value()
        except Exception as e:
            print(e)
            print('Failed')
        self.log(logging.INFO, 'Result of {0}: {1}'.format(self._name, result))
        return(result)

    def get_scan_config(self,
                        y_range,
                        current_range=None,
                        shutter_open=1):
        scan_config = {
            'prescan': {
                'Epics': {
                    'type': 'resource',
                    'config': {
                        'current_range': {
                            'type': 'value',
                            'value': current_range
                        },
                        'shutter_open': {
                            'type': 'value',
                            'value': shutter_open
                        }
                    }
                }
            },
            'scan': {
                'Epics': {
                    'type': 'resource',
                    'config': {
                        'xbpm_y_translation': {
                            'type': 'value',
                            'values': list(y_range)
                        }
                    }
                }
            },
            'plot': {
                'x_key': 'xbpm_y_translation',
                'y_key': 'currents'
            }
        }
        scan_config.update(scans.globals.get_beam_meas_keys())
        return(scan_config)
