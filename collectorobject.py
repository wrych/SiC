#! /usr/bin/env python2.7

import copy
import sys
import logging
import os
import datetime
import json
import time


def get_preconfigured_logger():
    logging.basicConfig(level=logging.INFO)
    return(logging.getLogger('collector'))

class CollectorException(Exception):
    pass

class CollectorObject(object):

    def __init__(self, logger):
        self.set_logger(logger)

    def set_logger(self, logger):
        if (logger == sys.stdout):
            self._logger = get_preconfigured_logger()
        else:
            self._logger = logger

    def get_logger(self):
        return(self._logger)

    def log(self, *args, **kw_args):
        if (self.get_logger() is not None):
            self._logger.log(*args, **kw_args)
        else:
            pass


class Resource(CollectorObject):

    def __init__(self, logger=sys.stdout):
        super(Resource, self).__init__(logger)
        self._is_initialized = False
        self._children = {}

    def initialize(self, config):
        self.set_config(config)
        self._is_initialized = True
        return(True)

    def get_kw_args(self, key, params):
        kw_args = {pkey: params[pkey] for pkey in params if not pkey in ['type', 'value']}
        return(kw_args)

    def add_interactors(self, child, key):
        if ('w' in child.get_access_mode()):
            child.set_setter(getattr(self, 'set_{0}'.format(key)))
        if ('r' in child.get_access_mode()):
            child.set_getter(getattr(self, 'get_{0}'.format(key)))

    def update_value_child(self, key, params):
        try:
            value = params['value']
            if ('w' in self._children[key].get_access_mode()):
                self._children[key].set_value(value)
        except:
            pass

    def initialize_value_child(self, key, params):
        kw_args = self.get_kw_args(key, params)
        self._children[key] = Value(**kw_args)
        self.add_interactors(self._children[key], key)
        self.update_value_child(key, params)

    def set_config(self, config):
        for (key, params) in config.items():
            obj_type = params['type']
            if (obj_type == 'value'):
                self.initialize_value_child(key, params)
            elif (obj_type == 'resource'):
                import resources
                self._children[key] = getattr(resources, key)()
                self._children[key].initialize(params['config'])

    def update_config(self, config):
        for (key, params) in config.items():
            obj_type = params['type']
            if (obj_type == 'value'):
                self.update_value_child(key, params)
            elif (obj_type == 'resource'):
                self._children[key].update_config(params['config'])

    def get_is_initialized(self):
        return(self._is_initialized)

    def get_child(self, key):
        return(self._children[key])

    def scan(self, scan, config, done_keys=[]):
        done_keys = copy.copy(done_keys)
        self.log(logging.INFO, '****{0}'.format(config.keys()))
        remaining_keys = [key for key in config if (key not in done_keys)]
        if (len(remaining_keys) > 0):
            key = remaining_keys[0]
            params = config[key]
            done_keys.append(key)
            obj_type = params['type']
            if (obj_type == 'value'):
                for value in params['values']:
                    self.log(logging.INFO, 'Setting {0} to {1}'.format(key, value))
                    self.update_value_child(key, {'value': value})
                    self.scan(scan, config, done_keys)
            elif (obj_type == 'resource'):
                self._children[key].scan(scan, params['config'], done_keys)
        else:
            scan.take_data_point()
            self.log(logging.INFO, 'Scan Step completed')

    def get_value_dict(self):
        data_dict = {}
        for key in self._children:
            obj = self.get_child(key)
            data_dict[key] = obj.get_value_dict()
        return(data_dict)

    def update_data_dict(self, config, data_dict):
        for (key, params) in config.items():
            data_dict = self.append_data_dict(data_dict, key, params)
        return(data_dict)

    def append_data_dict(self, data_dict, key, params):
        if not(key in data_dict):
            data_dict[key] = {}
        obj_type = params['type']
        data_dict[key]['type'] = obj_type
        if (obj_type == 'value'):
            value = self.get_child(key).get_value_dict()
            data_dict[key]['value'] = value
        elif (obj_type == 'resource'):
            if ('config' not in data_dict[key]):
                data_dict[key]['config'] = {}
            data_dict[key]['config'] = self.get_child(key).update_data_dict(params['config'],data_dict[key]['config'])
        return(data_dict)

    def tear_down(self):
        self._is_initialized = False
        return(True)


class Scan(CollectorObject):

    def __init__(self, resource, config, path, name_pattern='scan_{0}', logger=sys.stdout):
        super(Scan, self).__init__(logger)
        self._resource = resource
        self._config = config
        self._data_points = []
        self._name_pattern = name_pattern
        self._root_path = path

    def get_scan_path(self):
        return(self._scan_path)

    def scan(self):
        self._data_point_nr = 0
        self._scan_path = self._root_path
        self.write_initial_state()
        self.write_scan_config()
        self.log(logging.INFO, 'Running Scan')
        self._resource.scan(self, self._config['scan'])
        self.log(logging.INFO, 'Scan Finished')
        return(self.get_data_points())

    def get_data_points(self):
        return(self._data_points)

    def take_data_point(self):
        self.log(logging.DEBUG, 'Getting all data for scan point.')
        data_dict = self.build_data_dict()
        self._data_points.append(data_dict)
        self.write_data_file(data_dict)
        self._data_point_nr += 1
        self.check_values(data_dict, self._config['meas'])

    def check_values(self, values, config):
        for key in config:
            if(config[key]['type'] == 'value'):
                try:
                    self.check_value_exceeds_limits(values[key]['value']['value'], config[key]['allowed_range'])
                except KeyError as e:
                    self.log(logging.DEBUG, 'No limit for value: {0}'.format(key))
            else:
                self.check_values(values[key]['config'], config[key]['config'])

    def check_value_exceeds_limits(self, value, allowed_range, max_values_out_of_range=1):
        self.log(logging.DEBUG, 'Checking values {0} against range {1}'.format(value, allowed_range))
        if (type(value) == list):
            fails = 0
            for i, v in enumerate(value):
                try:
                    self.check_value_exceeds_limits(v, [allowed_range[0][i], allowed_range[1][i]])
                except CollectorException as e:
                    self.log(logging.WARN, e)
                    fails += 1
            if (fails > max_values_out_of_range):
                raise(CollectorException('More values out of range than defined'))
        else:
            self.log(logging.DEBUG, 'Value: {0} Limits: {1}'.format(value, allowed_range))
            if (allowed_range[0] is not None):
                if (value < allowed_range[0]):
                    raise(CollectorException('Value lower than definded minmum'))
            if (allowed_range[1] is not None):
                if (value > allowed_range[1]):
                    raise(CollectorException('Value higher than definded maximum'))

    def write_initial_state(self):   
        file_name = '{0}.json'.format(self._name_pattern.format('init_state'))
        config_dict = self._resource.get_value_dict()
        self.write_file(config_dict, file_name)

    def write_scan_config(self):   
        file_name = '{0}.json'.format(self._name_pattern.format('params'))     
        config_dict = self._config
        self.write_file(config_dict, file_name)

    def write_file(self, data_dict, file_name):
        with open(os.path.join(self._scan_path, file_name), 'w') as f:
            json.dump(data_dict, f)

    def write_data_file(self, data_dict):
        data_file_name = '{0}.json'.format(self._name_pattern.format('{0:0>6}'.format(self._data_point_nr)))
        self.write_file(data_dict, data_file_name)

    def build_data_dict(self):
        config_dict = {}
        config_dict = self._resource.update_data_dict(self._config['scan'], config_dict)
        config_dict = self._resource.update_data_dict(self._config['meas'], config_dict)
        return(config_dict)

    def get_data_points(self):
        return(self._data_points)


class Value(CollectorObject):
    _ALLOWED_ACCESS_MODES = ['r', 'w', 'rw']
    _KNOWN_DTYPES = {
        'int': int,
        'float': float,
        'str': str
        }
    _ALLOWED_RANGE_DTYPES = ['int', 'float']
    _ATTRIBUTES = [
        'dtype', 
        'access_mode',
        'unit',
        'allowed_range',
        'allowed_values'
        ]

    def __init__(self,
                 dtype=None,
                 access_mode='rw',
                 unit='',
                 allowed_range=None,
                 allowed_values=None,
                 setter=None,
                 getter=None,
                 synced=None,
                 logger=sys.stdout):
        super(self.__class__, self).__init__(logger)
        self.set_dtype(dtype)
        self.set_access_mode(access_mode)
        self.set_unit(unit)
        self.set_allowed_range(allowed_range)
        self.set_allowed_values(allowed_values)
        self.set_setter(setter)
        self.set_getter(getter)
        self.set_synced(synced)

    def set_synced(self, value):
        self._synced = value

    def get_synced(self):
        return(self._synced)

    def set_dtype(self, dtype):
        if (dtype not in self._KNOWN_DTYPES and dtype is not None):
            msg = ('Data Type {0} not in known data types ({1})'.format(dtype, self._KNOWN_DTYPES))
            self.log(logging.WARN, msg)
            raise(ValueError(msg))
        self.log(logging.DEBUG, 'Setting dtype to {0}'.format(dtype))
        self._dtype = dtype

    def get_dtype(self):
        return(self._dtype)

    def set_access_mode(self, access_mode):
        if(access_mode not in self._ALLOWED_ACCESS_MODES):
            msg = ('Access Mode {0} not in allowed_access_modes ({1})'.format(access_mode, self._ALLOWED_ACCESS_MODES))
            self.log(logging.WARN, msg)
            raise(ValueError, msg)
        self.log(logging.DEBUG, 'Setting access_mode to {0}'.format(access_mode))
        self._access_mode = access_mode

    def get_access_mode(self):
        return(self._access_mode)

    def get_dtype_from_str(self, dtype):
        return(self._KNOWN_DTYPES[dtype])

    def cast_dtype(self, value):
        dtype = self.get_dtype()
        if (dtype is not None):
            value = self.get_dtype_from_str(dtype)(value)
        return(value)

    def cast_array_dtype(self, array):
        if (array is not None):
            return([self.cast_dtype(el) for el in array])
        return(array)

    def check_in_allowed_range(self, value):
        allowed_range = self.get_allowed_range()
        if (allowed_range is not None):
            if (value < allowed_range[0] or value > allowed_range[1]):
                msg = ('Value {0} not in the allowed range ({1})'.format(value, allowed_range))
                self.log(logging.WARN, msg)
                raise(ValueError(msg))

    def check_in_allowed_values(self, value):
        allowed_values = self.get_allowed_values()
        if (allowed_values is not None):
            if (value not in allowed_values):
                msg = ('Value {0} not in the allowed values ({1})'.format(value, allowed_values))
                self.log(logging.WARN, msg)
                raise(ValueError(msg))

    def check_in_allowed_range_dtypes(self, allowed_range):
        if (allowed_range is not None):
            dtype = self.get_dtype()
            if (dtype not in self._ALLOWED_RANGE_DTYPES):
                msg = ('Data Type {0} not in the allowed range data types ({1})'.format(dtype, self._ALLOWED_RANGE_DTYPES))
                self.log(logging.WARN, msg)
                raise(TypeError(msg))

    def set_setter(self, setter):
        self._setter = setter

    def get_setter(self):
        return(self._setter)

    def set_getter(self, getter):
        self._getter = getter

    def get_getter(self):
        return(self._getter)

    def sync(self, setter, getter, value, acceptable_delta, retried=False):
        init_value = getter()
        setter(value)
        retries = 1
        while(abs(getter()-value)>acceptable_delta):
            time.sleep(.2)
            if ((retries%20) == 0 and getter() == init_value):
                self.log(logging.WARN, 'No difference in value detected, trying to re set value.')
                setter(value)
            if(retries > 200):
                self.log(logging.WARN, 'No difference in value detected, failed to re set value. Raising E...')
                raise(Exception('Could not set value'))
            retries += 1
        time.sleep(0.4)
        return(True)

    def set_value(self, value):
        value = self.cast_dtype(value)
        self.check_in_allowed_range(value)
        self.check_in_allowed_values(value)
        self.log(logging.DEBUG, 'Setting set_point to {0}'.format(value))
        self._set_point = value
        setter = self.get_setter()
        if (setter is not None):
            if(self._synced is not None):
                self.sync(setter, self.get_getter(), value, self._synced)
            else:
                setter(value)
                

    def get_set_point(self):
        try:
            return(self._set_point)
        except AttributeError as e:
            raise(RuntimeError('Accessing set_point before assignment'))

    def get_value(self):
        getter = self.get_getter()
        if (getter is not None):
            value = getter()
        else:
            value = self.get_set_point()
        return(value)

    def get_value_dict(self):
        attr_dict = {}
        for key in self._ATTRIBUTES:
            attr = getattr(self, 'get_{0}'.format(key))()
            if (attr is not None):
                attr_dict[key] = attr
        if ('r' in self.get_access_mode()):
            attr_dict['value'] = self.get_value()
        return(attr_dict)

    def set_unit(self, unit):
        self.log(logging.DEBUG, 'Setting unit to {0}'.format(unit))
        self._unit = unit

    def get_unit(self):
        return(self._unit)

    def set_allowed_range(self, allowed_range):
        self.check_in_allowed_range_dtypes(allowed_range)
        self.log(logging.DEBUG, 'Setting allowed_range to {0}'.format(allowed_range))
        self._allowed_range = self.cast_array_dtype(allowed_range)

    def get_allowed_range(self):
        return(self._allowed_range)

    def set_allowed_values(self, allowed_values):
        self.log(logging.DEBUG, 'Setting allowed_values to {0}'.format(allowed_values))
        self._allowed_values = self.cast_array_dtype(allowed_values)

    def get_allowed_values(self):
        return(self._allowed_values)
