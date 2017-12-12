import collectorobject
import logging
import time
import epics
import numpy

class Epics(collectorobject.Resource):

    KEYS = {
        'shutter_open': 'X10SA-ES-PH1:SET',

        #'storage_ring_current': 'X10SA-ED-PP',
        'storage_ring_current': 'ARIDI-PCT:CURRENT',

        'aperature': 'X10SA-ES-APT:SET',
        'xbpm_y_translation_d': 'X10SA-ES-OMS4:MOTY.VAL',
        'xbpm_x_translation_d': 'X10SA-ES-OMS4:MOTX.VAL',
        'xbpm_y_translation_rbv': 'X10SA-ES-OMS4:MOTY.RBV',
        'xbpm_x_translation_rbv': 'X10SA-ES-OMS4:MOTX.RBV',
        'diode_current': 'X10SA-ES-XEYE_K:READOUT',
        'diode_range': 'X10SA-ES-XEYE_K:RANGE',
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
        'mean_value_3': 'Current4:MeanValue',
        'xbpm_bias_state': 'BiasState',
        'xbpm_bias_voltage': 'BiasVoltage'
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

    def initialize(self, config):
        self.ah501d = "X10SA-ES-SSBPM2:"
        self.build_getter_setter(self.ah501d, self.AH501D_KEYS, True)
        self.build_getter_setter(self.ah501d, self.AH501D_NO_RBV_KEYS, False)
        self.build_getter_setter('', self.KEYS, False)
        self.get_xbpm_x_translation = self.get_xbpm_x_translation_rbv
        self.get_xbpm_y_translation = self.get_xbpm_y_translation_rbv
        #self.get_xbpm_z_translation = self.get_xbpm_z_translation_rbv
        self.set_xbpm_x_translation = self.set_xbpm_x_translation_d
        self.set_xbpm_y_translation = self.set_xbpm_y_translation_d
        #self.set_xbpm_z_translation = self.set_xbpm_z_translation_d
        #self.get_filter_wheel = self.get_filter_wheel_d
        #self.get_photon_energy = self.get_photon_energy_rbv
        #self.set_photon_energy = self.set_photon_energy_d
        super(Epics, self).initialize(config)

    def set_filter_wheel(self, value):
        self.set_filter_wheel_d(value)
        time.sleep(5)

    def compute_offset(self):
        self.log(logging.INFO, 'Compute Offsets')
        self.acquire()
        for i in range(4):
            getattr(self, 'set_compute_current_offset_{0}'.format(i))

    def build_getter_setter(self, device, config, rbv):
        for key, value in config.items():
            if (rbv):
                setattr(self, '_{0}_rbv'.format(key),
                        epics.PV(self.get_device_command_str(device, '{0}{1}'.format(value, '_RBV'))))
            setattr(self, '_{0}'.format(key),
                    epics.PV(self.get_device_command_str(device, value)))
            setattr(self, 'get_{0}'.format(key),
                    getattr(self, '_{0}{1}'.format(key,'_rbv' if rbv else '')).get)
            setattr(self, 'set_{0}'.format(key),
                    getattr(self, '_{0}'.format(key)).put)

    def get_device_command_str(self, device, command):
        return('{0}{1}'.format(device, command))

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

