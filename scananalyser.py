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

class ScanAnalyser():

    def __init__(self, scan_parameter, scan_path, scan_data=None, logger=sys.stdout):
        self.set_logger(logger)
        if (type(scan_parameter) == str):
            self._scan_parameter = getattr(scans, scan_parameter)()
            self.log(logging.INFO, 'Using scan {0}...'.format(scan_parameter))
        else:
            self._scan_parameter = scan_parameter
        self._scan_path = scan_path
        self.log(logging.INFO, 'PATH {0}...'.format(scan_path))
        if (scan_data is not None):
            self._data = scan_data
        else:
            self._data = self.get_data(self._scan_path)
        self._param_paths, self._value_paths = self.get_value_and_param_paths()

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
            root_path = copy.copy(name_path)
            root_path.append(key)
            if (param['type'] == 'resource'):
                root_path.append('config')
                values.extend(self.get_value_paths(param['config'], root_path))
            elif (param['type'] == 'value'):
                values.append(root_path)
        return(values)

    def get_scan_key_paths(self):
        return(self.get_key_paths('scan'))

    def get_meas_key_paths(self):
        return(self.get_key_paths('meas'))

    def get_sub_item_by_index(self, key_path, index):
        return(self.get_sub_item(key_path, self._data[index]))

    def get_sub_item(self, key_path, value_dict):
        key_path = copy.copy(key_path)
        while (len(key_path) > 0):
            value_dict = value_dict[key_path[0]]
            del(key_path[0])
        try:
            return(value_dict['value']['value'])
        except:
            # fix inconsitency in scan and data files, remove
            return(value_dict['values'])

    def get_array(self, parameter_path, parameter_type='scan'):
        values = []
        for point in self._data:
            values.append(self.get_sub_item(parameter_path, point))
        return(numpy.asarray(values))

    def get_printable_name(self, parameter_path, seperator='/'):
        return(seperator.join([item for item in parameter_path if (item not in ['config'])]))

    def plot_axis(self, ax, x, y, label=None, xlabel=None, ylabel=None):
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_yscale('symlog', linthreshy=10e-10)
        ax.plot(x,y, label=None)
        return(ax)

    def get_data_as_arrays(self):
        return([self.get_array(param) for param in self._param_paths],
                [self.get_array(value) for value in self._value_paths])

    def get_max_param_value(self, index=0):
        value = numpy.max(self.get_array(self._param_paths[index]))
        self.log(logging.DEBUG, 'Maximum value: {0}...'.format(value))
        return(value)

    def get_min_index_between_pads(self, pads):
        data = self.get_array(self._value_paths[0])
        min_index = numpy.argmin(numpy.abs(numpy.subtract(*[data[:,index] for index in pads])))
        self.log(logging.DEBUG, 'Minimum difference at measurement {0}...'.format(min_index))
        return(min_index)

    def get_index_from_pads(self, pads):
        if (type(pads) == list):
            return([index-1 for index in pads])
        else:
            return(pads-1)

    def get_center(self, pads, param_key='currents'):
        value_indexes = self.get_index_from_pads(pads)
        min_index = self.get_min_index_between_pads(value_indexes)
        return(self.get_sub_item_by_index(self.get_param_by_key(param_key), min_index))

    def get_value_and_param_paths(self):
        return(self.get_scan_key_paths(), self.get_meas_key_paths())

    def plot_2d(self, fig):
        self.log(logging.INFO, 'Getting X data...')
        x = self.get_array(self._x_key)
        self.log(logging.INFO, 'Getting Y data...')
        y = self.get_array(self._y_key)
        self.log(logging.INFO, 'Plotting')
        if(len(y.shape) > 1):
            num_plots = y.shape[1]
            for i in range(num_plots):
                ax = fig.add_subplot(2,(num_plots+1)/2,i+1)
                self.plot_axis(ax, x, y[:,i], **self.get_2d_labels())
        else:
            ax = fig.add_subplot(1,1,1)
            self.plot_axis(ax, x, y, **self.get_2d_labels())

    def publish_plot(self, fig):
        print(self.get_2d_labels('-'))
        fig.savefig(os.path.join(self._scan_path, 
                                 'xy_scan.png'.format(**self.get_2d_labels('-'))))

    def display_plot(self, fig):
        fig.show()

    def get_2d_labels(self, separator='/'):
        return({
            'xlabel': self.get_printable_name(self._x_key, separator), 
            'ylabel': self.get_printable_name(self._y_key, separator),
            })

    def get_3d_labels(self, separator='/'):
        labels = self.get_2d_labels(separator)
        labels.update({'zlabel': self.get_printable_name(self._z_key, separator)})
        return(labels)

    def get_array_by_key(self, key):
        return(self.get_array(self.get_paths_by_key(key)))

    def get_indexes_by_key(self, key):
        return(self.get_sub_item(key, self._scan_parameter['scan']))

    def get_reshape_order(self, x,y,z):
        print(x.shape[0],y.shape[0],z.shape[0])
        x_len = x.shape[0]-1
        y_len = y.shape[0]-1
        search_index = x_len if (x_len < y_len) else y_len
        x_val = self.get_sub_item_by_index(self._x_key, search_index)
        y_val = self.get_sub_item_by_index(self._y_key, search_index)
        if (abs(x[search_index]-x_val)<abs(y[search_index]-y_val)):
            return('C')
        else:
            return('F')
        

    def matshow_axis(self, ax, x, y, z, 
                     label=None, 
                     xlabel=None, 
                     ylabel=None, 
                     zlabel=None,
                     vmax=None):
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if (z.shape[0] != x.shape[0]*y.shape[0]):
            numpy.pad(z, (x.shape[0]*y.shape[0]-z.shape[0]), 'constant', constant_values=0)
        z = z.reshape(x.shape[0], y.shape[0], order=self.get_reshape_order(x,y,z))
        try:        
            z = numpy.flip(z, axis=1)
        except:
            pass
        norm = matplotlib.colors.SymLogNorm(linthresh=1e-9,
                                            linscale=1e-9,
                                            vmin = 0,
                                            vmax=vmax)
        ax.imshow(z,
                  aspect='equal',
                  extent = (numpy.max(x), numpy.min(x), numpy.max(y), numpy.min(y)),
                  norm = norm,
                  origin='upper')

    def get_center_2d(self):
        z = self.get_array(self._z_key)
        std_dev = numpy.std(z, axis=1)
        min_index = numpy.argmin(std_dev)
        self.log(logging.DEBUG, 'Lowest std dev at measurement point {0}'.format(min_index))
        x = self.get_sub_item_by_index(self._x_key, min_index)
        y = self.get_sub_item_by_index(self._y_key, min_index)
        return(x, y)
        
    def plot_to_do():
        x = self.get_sub_item_by_index(self._x_key, min_index)
        y = self.get_sub_item_by_index(self._y_key, min_index)
        self.log(logging.INFO, 'Getting X data...')
        x = self.get_indexes_by_key(self._x_key)
        self.log(logging.INFO, 'Getting Y data...')
        y = self.get_indexes_by_key(self._y_key)
        

    def plot_3d(self, fig):
        self.log(logging.INFO, 'Getting X data...')
        x = self.get_indexes_by_key(self._x_key)
        self.log(logging.INFO, 'Getting Y data...')
        y = self.get_indexes_by_key(self._y_key)
        self.log(logging.INFO, 'Getting Z data...')
        z = self.get_array(self._z_key)
        self.log(logging.INFO, 'Plotting')
        if(len(z.shape) > 1):
            vmax = numpy.max(z)
            num_plots = z.shape[1]
            kw_args = self.get_3d_labels()
            kw_args.update({'vmax':vmax})
            for i in range(num_plots):
                ax = fig.add_subplot(2,(num_plots+1)/2,i+1)
                self.matshow_axis(ax, x, y, z[:,i], **kw_args)
        else:
            ax = fig.add_subplot(1,1,1)
            self.matshow_axis(ax, x, y, z, **self.get_3d_labels())   

    def get_paths_by_key(self, key, path_list=None):
        if (path_list is None):
            path_list = self._param_paths + self._value_paths
        return([path for path in path_list if path[-1] == key][0])

    def plot(self, display_plot=False, **kw_args):
        fig = matplotlib.pyplot.figure()
        self._x_key = self.get_paths_by_key(kw_args['x_key'])
        self._y_key = self.get_paths_by_key(kw_args['y_key'])
        if (len(self._param_paths) == 1):
            self.plot_2d(fig)
        else:
            self._z_key = self.get_paths_by_key(kw_args['z_key'])
            self.plot_3d(fig)
        self.publish_plot(fig)
        if(display_plot):
            self.display_plot(fig)
            input('Press any key to continue')

if __name__ == '__main__':
    scan = sys.argv[1]
    folder = sys.argv[2]
    scan_plotter = ScanAnalyser(scan, folder)
    scan_plotter.plot(x_key='xbpm_x_translation',
                      y_key='xbpm_y_translation',
                      z_key='currents')
    print(scan_plotter.get_center_2d())
    #print(scan_plotter.get_center([2,4]))
    
