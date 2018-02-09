import collectorobject
import logging
import epics
import time
import numpy

class Epics(collectorobject.Resource):

    KEYS = {
        'shutter_open': 'OP-CTRL:SH_ON',
        'storage_ring_current': 'ED-PP',
        'photon_energy_d': 'OP-MO:E_SET',
        'photon_energy_rbv': 'OP-MO:E_RBV',
        'frontend_slits_width': 'OP-FEAU:HWIDTH_RBV',
        'jj_slits_v_size': 'ES-JJ:SVsize',
        'jj_slits_h_size': 'ES-JJ:SHsize',
        'xbpm_z_translation_d': 'ES-PP:M23.VAL',
        'xbpm_y_translation_d': 'ES-PP:M24.VAL',
        'xbpm_x_translation_d': 'ES-PP:M25.VAL',
        'xbpm_z_translation_rbv': 'ES-PP:M23.RBV',
        'xbpm_y_translation_rbv': 'ES-PP:M24.RBV',
        'xbpm_x_translation_rbv': 'ES-PP:M25.RBV',
        'xbpm_bias_state': 'KEI10:VOLTOUT',
        'xbpm_bias_voltage': 'KEI10:SETVOLTAGE',
        'diode_bias_state': 'KEI12:VOLTOUT',
        'diode_bias_voltage': 'KEI12:SETVOLTAGE',
        'diode_current': 'KEI12:READOUT',
        'diode_range': 'KEI12:RANGE',
        'filter_wheel': 'ES-FW:FILTER'
    }

    AH501D_KEYS = {
        'num_channels': 'NumChannels',
        'resolution': 'Resolution',
        'acquire_mode': 'AcquireMode',
        'num_acquire': 'NumAcquire',
        'sample_time': 'SampleTime',
        'averaging_time': 'AveragingTime',
        'current_range': 'Range',
        'acquire': 'Acquire',
        'mean_value_0': 'Current1:MeanValue',
        'mean_value_1': 'Current2:MeanValue',
        'mean_value_2': 'Current3:MeanValue',
        'mean_value_3': 'Current4:MeanValue'
        }

    AH501D_NO_RBV_KEYS = {
        'current_offset_0': 'CurrentOffset1',
        'current_offset_1': 'CurrentOffset2',
        'current_offset_2': 'CurrentOffset3',
        'current_offset_3': 'CurrentOffset4',
        'compute_current_offset_0': 'ComputeCurrentOffset1',
        'compute_current_offset_1': 'ComputeCurrentOffset2',
        'compute_current_offset_2': 'ComputeCurrentOffset3',
        'compute_current_offset_3': 'ComputeCurrentOffset4'
        }
    
    def __init__(self, beam_line, logger=sys.stdout):
        self.beam_line = beam_line
        super(Epics, self).__init__(logger)
        

    def initialize(self, config, beam_line):
        self.ah501d = "ES-QEM1:"
        self.build_getter_setter(self.beam_line, self.ah501d, self.AH501D_KEYS, True)
        self.build_getter_setter(self.beam_line, self.ah501d, self.AH501D_NO_RBV_KEYS, False)
        self.build_getter_setter(self.beam_line, '', self.KEYS, False)
        self.get_xbpm_x_translation = self.get_xbpm_x_translation_rbv
        self.get_xbpm_y_translation = self.get_xbpm_y_translation_rbv
        self.get_xbpm_z_translation = self.get_xbpm_z_translation_rbv
        self.set_xbpm_x_translation = self.set_xbpm_x_translation_d
        self.set_xbpm_y_translation = self.set_xbpm_y_translation_d
        self.set_xbpm_z_translation = self.set_xbpm_z_translation_d
        self.get_photon_energy = self.get_photon_energy_rbv
        self.set_photon_energy = self.set_photon_energy_d
        super(Epics, self).initialize(config)

    def compute_offset(self):
        self.log(logging.INFO, 'Compute Offsets')
        self.acquire()
        for i in range(4):
            getattr(self, 'set_compute_current_offset_{0}'.format(i))

    def build_getter_setter(self, beam_line, device, config, rbv):
        for key, value in config.items():
            if (rbv):
                setattr(self, '_{0}_rbv'.format(key),
                        epics.PV(self.get_device_command_str(beam_line, device, '{0}{1}'.format(value, '_RBV'))))
            setattr(self, '_{0}'.format(key),
                    epics.PV(self.get_device_command_str(beam_line, device, value)))
            setattr(self, 'get_{0}'.format(key),
                    getattr(self, '_{0}{1}'.format(key,'_rbv' if rbv else '')).get)
            setattr(self, 'set_{0}'.format(key),
                    getattr(self, '_{0}'.format(key)).put)

    def get_device_command_str(self, beam_line, device, command):
        return('{0}-{1}{2}'.format(beam_linedevice, command))

    def get_command(self, device, command):
        epics.caget(self.get_device_command_str(device, command))

    def put_command(self, device, command, value):
        epics.caput(self.get_device_command_str(device, command), value)

    def calculate_current(self, index):
        value = getattr(self, 'get_mean_value_{0}'.format(index))()
        self.log(logging.DEBUG, 'Channel {0}, value: {1}'.format(index, value))
        current_range = [2.5e-3, 2.5e-6, 2.5e-9][self.get_current_range()]
        self.log(logging.DEBUG, 'Channel {0}, current_range: {1}'.format(index, current_range))
        resolution = [16, 24][self.get_resolution()]
        self.log(logging.DEBUG, 'Channel {0}, resolution: {1}'.format(index, resolution))
        current = float(2*current_range)/(2**resolution-1)*value
        self.log(logging.INFO, 'Channel {0}, value: {1}'.format(index, current))
        return(current)

    def acquire(self):
        acquire_time = self.get_averaging_time()*2
        self.set_acquire(1)
        time.sleep(acquire_time)

    def get_currents(self):
        self.acquire()
        return([self.calculate_current(i) for i in range(4)])

