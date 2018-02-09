import logging
import numpy
import unittest

import collectorobject


class Test(unittest.TestCase):

    def get_default_test_configuration(self):
        return({
            'Template': {
                    'type': 'resource',
                    'config': {
                            'test_1': {
                                'type': 'value',
                                'value': 1.0,
                                'dtype': 'float',
                            },
                            'test_2': {
                                'type': 'value',
                                'value': 2.0,
                                'dtype': 'float'
                            }
                        }
                    }
                })

    def get_scan_configuration(self):
        return({
            'scan': {
                'Template': {
                        'type': 'resource',
                        'config': {
                                'test_1': {
                                    'type': 'value',
                                    'values': numpy.arange(1.0, 1.4, .1),
                                },
                                'test_2': {
                                    'type': 'value',
                                    'values': numpy.arange(3.0, 3.4, .1),
                                }
                            }
                        },
                    },
            'meas': {
                }
            })

    def get_instance(self):
        return(collectorobject.Resource())

    def initialize_object(self, obj, config=None):
        if (config is None):
            config = self.get_default_test_configuration()
        ret = obj.initialize(config)
        return(ret)

    def get_initialized_instance(self, config=None):
        obj = self.get_instance()
        self.initialize_object(obj, config)
        return(obj)

    def get_is_initialized(self, obj):
        return(obj.get_is_initialized())

    def test_class(self):
        obj = self.get_instance()
        self.assertIsInstance(obj, collectorobject.Resource)

    def test_is_not_initalized(self):
        obj = self.get_instance()
        ret = self.get_is_initialized(obj)
        self.assertFalse(ret)

    def test_initialize(self):
        obj = self.get_instance()
        ret = self.initialize_object(obj)
        self.assertTrue(ret)

    def test_is_initalized(self):
        obj = self.get_initialized_instance()
        ret = self.get_is_initialized(obj)
        self.assertTrue(ret)
        
    def test_set_config(self):
        config = self.get_default_test_configuration()
        obj = self.get_initialized_instance(config)
        values = [config[resource]['config'][key]['value'] for resource in config for key in config[resource]['config']]
        get_values = [obj.get_child(resource).get_child(key).get_value() for resource in config for key in config[resource]['config']]
        self.assertSequenceEqual(get_values, values)

    def test_update_config(self):
        obj = self.get_initialized_instance()
        value = 3.0
        update_config = {
                'Template': {
                    'type': 'resource',
                    'config': {
                        'test_1': {
                            'type': 'value',
                            'value': value
                            }
                        }
                    }
                }
        obj.update_config(update_config)
        get_value = obj.get_child('Template').get_child('test_1').get_value()
        self.assertAlmostEqual(get_value, value)

    def test_tear_down(self):
        obj = self.get_instance()
        ret = obj.tear_down()
        self.assertTrue(ret)

    def test_tear_down_not_initialized(self):
        obj = self.get_initialized_instance()
        obj.tear_down()
        ret = self.get_is_initialized(obj)
        self.assertFalse(ret)
        
    def test_scan(self):
        log = logging.getLogger('test.test_scan')
        log.warn('*******************')
        obj = self.get_initialized_instance()
        scan = collectorobject.Scan(obj, self.get_scan_configuration())
        log.warn(scan.get_data_points())
        log.warn('*******************')

if __name__ == "__main__":
    unittest.main()
