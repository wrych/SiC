import matplotlib.pyplot
import os
import json
import numpy
import copy
import sys
import logging
import traceback
import time

import scans


def get_preconfigured_logger():
    logging.basicConfig(level=logging.DEBUG)
    return(logging.getLogger('plot_scan'))


class ScanAnalyser():

    def __init__(self, scan_path, scan_parameter=None, scan_data=None, logger=sys.stdout):
        self.set_logger(logger)
        self._scan_path = scan_path
        self.set_scan_paramter(scan_parameter)
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

    def set_scan_paramter(self, scan_parameter):
        if (type(scan_parameter) == str):
            self._scan_parameter = getattr(scans, scan_parameter)()
            self.log(logging.INFO, 'Using scan {0}...'.format(scan_parameter))
        elif (scan_parameter is None):
            self._scan_parameter = self.get_scan_config_from_file()
        else:
            self._scan_parameter = scan_parameter

    def get_scan_config_from_file(self):
        with open(os.path.join(self._scan_path, 'scan_params.json'), 'r') as f:
            return(json.load(f))

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

    def get_sub_item_by_index(self, key_path, index, key='value'):
        return(self.get_sub_item(key_path, self._data[index], key))

    def get_sub_item(self, key_path, value_dict, key='value'):
        key_path = copy.copy(key_path)
        while (len(key_path) > 0):
            value_dict = value_dict[key_path[0]]
            del(key_path[0])
        try:
            return(value_dict['value'][key])
        except:
            # fix inconsitency in scan and data files, remove
            return(value_dict['values'])

    def get_array_and_norm(self, parameter_path, norm_by_key=None, parameter_type='scan'):
        array = self.get_array(parameter_path, parameter_type)
        if (norm_by_key is None):
            return(array)
        else:
            norm = self.get_array(norm_by_key)
            median = numpy.median(norm)
            try:
                for i in range(array.shape[1]):
                    array[:, i] = array[:, i]/norm*median
            except IndexError:
                array = array/norm*median
            return(array)

    def get_array(self, parameter_path, parameter_type='scan'):
        self.log(logging.DEBUG, 'Getting data {0}'.format(parameter_path[-1]))
        values = []
        for point in self._data:
            values.append(self.get_sub_item(parameter_path, point))
        return(numpy.asarray(values))

    def get_printable_name(self, parameter_path, seperator='/', unit=True):
        path_str = seperator.join([item for item in parameter_path if (item not in ['config'])])
        if (unit):
            return('{0} [{1}]'.format(path_str,
                                      self.get_sub_item_by_index(parameter_path, 0, 'unit')))
        else:
            return(path_str)

    def plot_axis(self, ax, x, y,
                  label=None,
                  xlabel=None,
                  ylabel=None,
                  xlim=None,
                  ylim=None,
                  legend=False,
                  title=None,
                  scale='symlog'):
        if (title is not None):
            ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if (scale == 'symlog'):
            ax.set_yscale('symlog', linthreshy=10e-10)
        else:
            pass
        ax.plot(x, y, label=label)
        ax.set_xlim(xlim)
        if (ylim is not None):
            ax.set_ylim((ylim[0], ylim[1]*1.5))
        if(legend):
            ax.legend()
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

    def get_file_name(self, x_key, y_key, z_key=None, pre=None, format=None):
        pre = pre if (pre is not None) else ''
        if (z_key is None):
            file_str = '{0}{xlabel}vs{ylabel}.{1}'.format(pre, format, **self.get_names(x_key, y_key, separator='-'))
        else:
            file_str = '{0}{xlabel}vs{ylabel}vs{zlabel}.{1}'.format(pre, format, **self.get_names(x_key, y_key, z_key, separator='-'))  
        return(file_str)

    def get_title(self, x_key, y_key, z_key=None, pre=None):
        pre = pre if (pre is not None) else ''
        if (z_key is None):
            title = '{0} {xlabel} vs {ylabel}'.format(pre, **self.get_labels(x_key, y_key, separator='-', unit=False))
        else:
            title = '{0} {xlabel} vs {ylabel} vs {zlabel}'.format(pre, **self.get_labels(x_key, y_key, z_key, separator='-', unit=False))  
        return(title)

    def save_plot(self, fig, x_key, y_key, z_key=None, pre=None):
        file_path = os.path.join(self._scan_path,self.get_file_name(x_key, y_key, z_key, pre=pre, format='png'))
        self.log(logging.INFO, 'Saving plot to: {0}'.format(file_path))
        fig.savefig(file_path)

    def display_plot(self, fig):
        fig.show()

    def get_names(self, x_key, y_key, z_key=None, separator='-'):
        return(self.get_labels(x_key, y_key, z_key, separator, unit=False))

    def get_labels(self, x_key, y_key, z_key=None, separator='/', unit=True):
        label_dict = {
            'xlabel': self.get_printable_name(x_key, separator, unit=unit),
            'ylabel': self.get_printable_name(y_key, separator, unit=unit)
            }
        if (z_key is not None):
            label_dict.update({'zlabel': self.get_printable_name(z_key, separator, unit=unit)})
        return(label_dict)

    def get_array_by_key(self, key):
        return(self.get_array(self.get_paths_by_key(key)))

    def get_indexes_by_key(self, key):
        return(numpy.array(self.get_sub_item(key, self._scan_parameter['scan'])))

    def get_reshape_order(self, x, y, z):
        return('f')

    def matshow_axis(self, ax, x, y, z,
                     label=None,
                     xlabel=None,
                     ylabel=None,
                     zlabel=None,
                     norm=None,
                     cmap=None):
        if (label is not None):
            ax.set_title(label)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if (z.shape[0] != x.shape[0]*y.shape[0]):
            numpy.pad(z, (x.shape[0]*y.shape[0]-z.shape[0]), 'constant', constant_values=0)
        z = z.reshape(x.shape[0], y.shape[0], order=self.get_reshape_order(x,y,z))
        cax = ax.imshow(z,
                        aspect='equal',
                        extent=(numpy.min(x), numpy.max(x), numpy.min(y), numpy.max(y)),
                        norm=norm,
                        cmap=cmap,
                        origin='upper')
        return(cax)

    def get_center_2d(self):
        z = self.get_array(self._z_key)
        std_dev = numpy.std(z, axis=1)
        min_index = numpy.argmin(std_dev)
        self.log(logging.DEBUG, 'Lowest std dev at measurement point {0}'.format(min_index))
        x = self.get_sub_item_by_index(self._x_key, min_index)
        y = self.get_sub_item_by_index(self._y_key, min_index)
        return(x, y)

    def save_data(self, x_key, y_key, z_key=None, pre=None):
        data = {}
        data['x'] = self.get_array(x_key)
        data['y'] = self.get_array(y_key)
        try:
            data['z'] = self.get_array(z_key)
        except:
            pass
        file_path = os.path.join(self._scan_path, self.get_file_name(x_key, y_key, z_key, pre, format='txt'))
        self.log(logging.INFO, 'Saving data to: {0}'.format(file_path))
        with open(file_path, 'w') as f:
            for index in range(data['x'].shape[0]):
                f.write('{0}\n'.format('\t'.join([str(data[key][index]) for key in data])))

    def plot_2d_per_pad(self, x, y, x_key, y_key, display_plot):
        fig = self.get_fig()
        num_plots = y.shape[1]
        ylims = numpy.min(y), numpy.max(y)
        for i in range(num_plots):
            ax = fig.add_subplot(2, (num_plots+1)/2, i+1)
            kw_args = self.get_labels(x_key, y_key)
            kw_args.update({
                'ylim': ylims,
                'title': 'Pad {0}'.format(i)
                })
            self.plot_axis(ax, x, y[:, i], **kw_args)
        self.publish_plot(fig, display_plot, x_key, y_key, name='4pad')

    def plot_2d_overall(self, x, y, x_key, y_key, display_plot):
        fig = self.get_fig()
        num_plots = y.shape[1]
        for i in range(num_plots):
            ax = fig.add_subplot(2, 1, 1)
            kw_args = self.get_labels(x_key, y_key)
            kw_args.update({
                'label': 'Pad {0}'.format(i),
                'legend': True,
                'title': 'Pad Overlayed'
                })
            self.plot_axis(ax, x, y[:, i], **kw_args)
        ax = fig.add_subplot(2, 1, 2)
        y = numpy.sum(y, axis=1)
        median = numpy.median(y)
        y /= median
        kw_args.update({
                'label': None,
                'legend': False,
                'title': 'Pad Sum',
                'ylim': [0.9, 1.1/1.5],
                'scale': 'linear'
                })
        self.plot_axis(ax, x, y, **kw_args)
        self.publish_plot(fig, display_plot, x_key, y_key, name='overall')

    def plot_2d(self, x_key, y_key, display_plot, norm_by_key=None):
        x = self.get_array(x_key)
        y = self.get_array_and_norm(y_key, norm_by_key=norm_by_key)
        self.log(logging.INFO, 'Plotting')
        if(len(y.shape) > 1):
            self.plot_2d_per_pad(x, y, x_key, y_key, display_plot)
            self.plot_2d_overall(x, y, x_key, y_key, display_plot)
        else:
            ax = fig.add_subplot(1, 1, 1)
            self.plot_axis(ax, x, y, **self.get_labels())

    def get_fig(self):
        return(matplotlib.pyplot.figure(figsize=(12, 9)))

    def add_color_bar(self, fig, ax, cmap, label=''):
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.8, top=0.9, wspace=None, hspace=None)
        cax = fig.add_axes([0.85, 0.1, 0.05, 0.8])
        fig.colorbar(ax, cmap=cmap, cax=cax, label=label)

    def get_cmap(self, value_type):
        if (value_type == 'abs'):
            return(matplotlib.pyplot.get_cmap('plasma'))
        elif (value_type == 'flat'):
            return(matplotlib.pyplot.get_cmap('coolwarm'))

    def get_norm(self, vmin, vmax, scale='linear'):
        if (scale == 'symlog'):
            norm = matplotlib.colors.SymLogNorm(linthresh=1e-10,
                                            linscale=1e-10,
                                            vmin=vmin,
                                            vmax=vmax)
        else:
            norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
        return(norm)

    def plot_3d_per_pad(self, x, y, z, x_key, y_key, z_key, display_plot):
        fig = self.get_fig()
        fig.suptitle(self.get_title(x_key, y_key, z_key, pre='Pads'))
        norm = self.get_norm(numpy.min(z), numpy.max(z))
        cmap = self.get_cmap('abs')
        kw_args = self.get_labels(x_key, y_key, z_key)
        kw_args.update({
            'norm': norm,
            'cmap': cmap
            })
        num_plots = z.shape[1]
        for i in range(num_plots):
            ax = fig.add_subplot(2, (num_plots+1)/2, i+1)
            kw_args.update({'label': 'Pad {0}'.format(i+1)})
            cax = self.matshow_axis(ax, x, y, z[:, i], **kw_args)
        self.add_color_bar(fig, cax, cmap, label=kw_args['zlabel'])
        self.publish_plot(fig, display_plot, x_key, y_key, z_key, name='4pads')

    def plot_3d_sum(self, x, y, z, x_key, y_key, z_key, display_plot):
        self.plot_3d_single(x, y, z, x_key, y_key, z_key, display_plot, 
                            name='sum',
                            zlabel='Summed Currents [A]')

    def plot_3d_rel(self, x, y, z, x_key, y_key, z_key, display_plot):
        median = numpy.median(z)
        z /= median 
        self.plot_3d_single(x, y, z, x_key, y_key, z_key, display_plot, 
                            cmap='flat', 
                            name='rel',
                            zlabel='Normalized Summed Currents []')

    def plot_3d_std(self, x, y, z, x_key, y_key, z_key, display_plot):
        self.plot_3d_single(x, y, z, x_key, y_key, z_key, display_plot, 
                            name='std',
                            zlabel='Current Standard Deviation []')

    def plot_3d_single(self, x, y, z, x_key, y_key, z_key, 
                       display_plot,
                       cmap='abs',
                       name=None,
                       zlabel=None):
        fig = self.get_fig()
        fig.suptitle(self.get_title(x_key, y_key, z_key, pre=name))
        scale = 'linear' 
        norm = self.get_norm(numpy.min(z), numpy.max(z), scale=scale)
        cmap = self.get_cmap(cmap)
        kw_args = self.get_labels(x_key, y_key, z_key)
        kw_args.update({
            'norm': norm,
            'cmap': cmap
            })
        ax = fig.add_subplot(1, 1, 1)
        cax = self.matshow_axis(ax, x, y, z, **kw_args)
        if (zlabel is None):
            zlabel = kw_args['zlabel']
        self.add_color_bar(fig, cax, cmap, label=zlabel)
        self.publish_plot(fig, display_plot, x_key, y_key, z_key, name=name)

    def plot_3d(self, x_key, y_key, z_key, display_plot, norm_by_key=None):
        x = self.get_indexes_by_key(x_key)
        y = self.get_indexes_by_key(y_key)
        z = self.get_array_and_norm(z_key, norm_by_key=norm_by_key)
        self.log(logging.INFO, 'Plotting')
        if(len(z.shape) > 1):
            self.plot_3d_per_pad(x, y, z, x_key, y_key, z_key, display_plot)
            z = numpy.sum(z, axis=1)
            self.plot_3d_sum(x, y, z, x_key, y_key, z_key, display_plot)
            self.plot_3d_rel(x, y, z, x_key, y_key, z_key, display_plot)
            self.plot_3d_std(x, y, z, x_key, y_key, z_key, display_plot)
        else:
            self.plot_3d_single(x, y, z, x_key, y_key, z_key, display_plot)
            self.plot_3d_rel(x, y, z, x_key, y_key, z_key, display_plot)
            self.plot_3d_std(x, y, z, x_key, y_key, z_key, display_plot)

    def publish_plot(self, fig, display_plot, x_key, y_key, z_key=None, name=None):
        self.save_plot(fig, x_key, y_key, z_key, name)
        if(display_plot):
            self.display_plot(fig)
            time.sleep(3)

    def get_paths_by_key(self, key, path_list=None):
        if (path_list is None):
            path_list = self._param_paths + self._value_paths
        return([path for path in path_list if path[-1] == key][0])

    def plot(self, x_key, y_key, display_plot=False, z_key=None, norm_by_key=None):
        x_key = self.get_paths_by_key(x_key)
        y_key = self.get_paths_by_key(y_key)
        if (norm_by_key is not None):
            norm_by_key = self.get_paths_by_key(norm_by_key)
        try:
            if (len(self._param_paths) == 1):
                self.plot_2d(x_key, y_key, display_plot)
                self.save_data(x_key, y_key, norm_by_key=norm_by_key)
            else:
                z_key = self.get_paths_by_key(z_key)
                self.plot_3d(x_key, y_key, z_key, display_plot, norm_by_key=norm_by_key)
                self.save_data(x_key, y_key, z_key)
        except Exception as e:
            self.log(logging.WARN, 'Could not plot data.')
            self.log(logging.INFO, e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, file=sys.stdout)
            print(e)

if __name__ == '__main__':
    folder = sys.argv[1]
    scan_plotter = ScanAnalyser(folder)
    scan_plotter.plot(x_key='xbpm_x_translation',
                      y_key='xbpm_y_translation',
                      z_key='diode_current',
                      norm_by_key=None)
    #scan_plotter.plot(x_key='xbpm_bias_voltage',
    #                  y_key='currents')
    #print(scan_plotter.get_center_2d())
    #print(scan_plotter.get_center([2,4]))
    
