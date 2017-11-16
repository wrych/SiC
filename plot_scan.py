import matplotlib.pyplot
import os
import json
import numpy
import copy
import sys
import logging

import scans

def get_preconfigured_logger():
    logging.basicConfig(level=logging.DEBUG)
    return(logging.getLogger('plot_scan'))

class ScanPlotter():

    def __init__(self, scan_parameter, scan_path, logger=sys.stdout):
        self.set_logger(logger)
        self._scan_parameter = getattr(scans, scan_parameter)()
        self.log(logging.INFO, 'Using scan {0}...'.format(scan_parameter))
        self._scan_path = scan_path  
        self.log(logging.INFO, 'Looking in folder {0}...'.format(scan_path))
        self._data = self.get_data(self._scan_path)
        self.plot()        

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

    def get_data(self, scan_path):
        data=[]
        n_point = 0
        while(True):
            file_name = 'scan_{0:0>6}.json'.format(n_point)
            try:
                with open(os.path.join(folder, file_name), 'r') as f:
                    data.append(json.load(f))
                n_point += 1
                self.log(logging.INFO, 'Read file {0}...'.format(file_name))
            except:
                self.log(logging.INFO, 'File not found {0}, breaking...'.format(file_name))
                break
        return(data)

    def get_key_paths(self, scan_parameter_name):
        return(self.get_value_paths(self._scan_parameter[scan_parameter_name]))

    def get_value_paths(self, scan_parameter, name_path=[]):
        name_path = copy.copy(name_path)
        values = []
        for key, param in scan_parameter.items():
            name_path.append(key)
            if (param['type'] == 'resource'):
                name_path.append('config')
                values.extend(self.get_value_paths(param['config'], name_path))
            elif (param['type'] == 'value'):
                values.append(name_path)
        return(values)

    def get_scan_key_paths(self):
        return(self.get_key_paths('scan'))

    def get_meas_key_paths(self):
        return(self.get_key_paths('meas'))

    def get_sub_item(self, key_path, value_dict):
        key_path = copy.copy(key_path)
        while (len(key_path) > 0):
            value_dict = value_dict[key_path[0]]
            del(key_path[0])
        return(value_dict['value']['value'])

    def get_array(self, parameter_path, parameter_type='scan'):
        values = []
        for point in self._data:
            values.append(self.get_sub_item(parameter_path, point))
        return(numpy.asarray(values))

    def get_printable_name(self, parameter_path):
        return('/'.join([item for item in parameter_path if (item not in ['config'])]))

    def plot_2d(self, ax, x, y, label=None, xlabel=None, ylabel=None):
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_yscale('symlog')
        ax.set_ylim(-1e-5, 1e-6)
        ax.plot(x,y, label=None)
        return(ax)

    def get_data_as_arrays(self):
        param_paths = self.get_scan_key_paths()
        value_paths = self.get_meas_key_paths()
        return([self.get_array(param) for param in param_paths],
                [self.get_array(value) for value in value_paths])

    def plot(self):
        param_paths = self.get_scan_key_paths()
        value_paths = self.get_meas_key_paths()
        fig = matplotlib.pyplot.figure()
        if (len(param_paths) == 1):
            self.log(logging.INFO, 'Getting X data...')
            x = self.get_array(param_paths[0])
            self.log(logging.INFO, 'Getting Y data...')
            y = self.get_array(value_paths[0])
            self.log(logging.INFO, 'Plotting')
            if(len(y.shape) > 1):
                num_plots = y.shape[1]
                for i in range(num_plots):
                    ax = fig.add_subplot(2,(num_plots+1)/2,i+1)
                    self.plot_2d(ax, x, y[:,i], 
                                xlabel=self.get_printable_name(param_paths[0]), 
                                ylabel=self.get_printable_name(value_paths[0]))
            else:
                ax = fig.add_subplot(1,1,1)
                self.plot_2d(ax, x, y, 
                            xlabel=self.get_printable_name(param_paths[0]), 
                            ylabel=self.get_printable_name(value_paths[0]))
            #fig.savefig('plot.png')
            fig.show()
            input()
        else:
            raise(Exception('Not yet implemented'))

if __name__ == '__main__':
    scan = sys.argv[1]
    folder = sys.argv[2]
    ScanPlotter(scan, folder)
    
