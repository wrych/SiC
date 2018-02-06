'''
Created on Nov 15, 2017

@author: det
'''
import json

import collectorobject
import scans
import logging
import scananalyser
import numpy
import sys
import os

DEVICE = 'pin12'
SCAN = 'forward_bias'

class UserScan(collectorobject.CollectorObject):
    def __init__(self, device, name, path_identifier, scan_name=None, scan_kw_args={}, logger=sys.stdout):
        super(UserScan, self).__init__(logger)
        self._device = device
        self._name = name
        if (scan_name is not None):
            self._scan_name = scan_name
        else:
            self._scan_name = self._name
        self._path_identifier = path_identifier
        self._cfg = self.get_standard_config()
        self._safe_cfg = self.get_standard_config()
        self._scan_kw_args = scan_kw_args
        self.log(logging.INFO, 'Scan "{0}" with config "{1}"...'.format(self._scan_name, self._name))
        try:
            self.initialise()
            self._pre_scan()
            self.setup_scan()
            self.scan()
            self._post_scan()
        finally:
            self._tear_down()

    def set_kw_args(self, kw_args, key):
        try:
            setattr(self, '_kw_{0}'.format(key), kw_args[key])
            del(kw_args[key])
        except:
            setattr(self, '_kw_{0}'.format(key), None)
        return(kw_args)

    def get_standard_config(self):
        with open('standard_config.json') as f:
            return(json.load(f))

    def get_safe_config(self):
        with open('safe_config.json') as f:
            return(json.load(f))

    def initialise(self):
        self.log(logging.INFO, 'Initialising objects...')
        self._obj = collectorobject.Resource()
        self._obj.initialize(self._cfg)

    def _pre_scan(self):
        self.log(logging.INFO, 'Executing Pre Scan Operations...')
        self.pre_scan()

    def pre_scan(self):
        pass

    def setup_scan(self):
        self._scan_config = getattr(scans,self._name)(**self._scan_kw_args)
        self.setup_folders()
        self._scan = collectorobject.Scan(self._obj, self._scan_config, self._scan_root_path)

    def setup_folders(self):
        self._scan_root_path = os.path.join('/import/exchange/mx/blcntl/6S/X06SA-IDL/devl/xbpm/180206_SiCXBPM/data', self._device, self._path_identifier, self._scan_name)
        os.makedirs(self._scan_root_path)
        return(self._scan_root_path)

    def scan(self):
        self.log(logging.INFO, 'Starting Scan')
        try:
            self._scan.scan()       
        except collectorobject.CollectorException as e:
            self.log(logging.WARN, e)
        self.log(logging.INFO, 'Scan Finished')

    def _post_scan(self):
        self.log(logging.INFO, 'Executing Post Scan Operations...')
        self. _analysis = scananalyser.ScanAnalyser(self._scan.get_scan_path(), self._scan_config, scan_data=self._scan.get_data_points())
        self.post_scan()

    def post_scan(self):
        pass

    def _tear_down(self):
        self.log(logging.INFO, 'Executing Tear Down Operations...')
        self._obj.initialize(self._safe_cfg)
        self.log(logging.INFO, 'Executing Manual Tear Down Operations...')
        self.tear_down()
        self.log(logging.INFO, 'Finished Tearing Down')
    
    def tear_down(self):
        pass

    def save_result(self, result):
        with open(os.path.join(self._scan.get_scan_path(), 'result.txt'), 'w') as f:
            f.write(str(result))
 
    
