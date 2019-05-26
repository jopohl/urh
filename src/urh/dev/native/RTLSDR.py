from collections import OrderedDict

import numpy as np

from multiprocessing.connection import Connection
from urh.dev.native.Device import Device

from urh.dev.native.lib import rtlsdr
from urh.util.Logger import logger


class RTLSDR(Device):
    DEVICE_LIB = rtlsdr
    ASYNCHRONOUS = False
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_RF_GAIN.name: "set_tuner_gain",
        Device.Command.SET_RF_GAIN.name+"_get_allowed_values": "get_tuner_gains",
        Device.Command.SET_BANDWIDTH.name: "set_tuner_bandwidth",
        Device.Command.SET_FREQUENCY_CORRECTION.name: "set_freq_correction",
        Device.Command.SET_DIRECT_SAMPLING_MODE.name: "set_direct_sampling"
    })

    DATA_TYPE = np.int8

    @classmethod
    def get_device_list(cls):
        return rtlsdr.get_device_list()

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        # identifier gets set in self.receive_process_arguments
        device_number = int(device_identifier)
        ret = rtlsdr.open(device_number)
        ctrl_connection.send("OPEN (#{}):{}".format(device_number, ret))
        return ret == 0

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection):
        ret = rtlsdr.reset_buffer()
        ctrl_connection.send("RESET_BUFFER:" + str(ret))
        return ret

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        data_conn.send_bytes(rtlsdr.read_sync())

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx: bool):
        logger.debug("RTLSDR: closing device")
        ret = rtlsdr.close()
        ctrl_connection.send("CLOSE:" + str(ret))

    def __init__(self, freq, gain, srate, device_number, resume_on_full_receive_buffer=False):
        super().__init__(center_freq=freq, sample_rate=srate, bandwidth=0,
                         gain=gain, if_gain=1, baseband_gain=1,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)

        self.success = 0
        self.bandwidth_is_adjustable = self.get_bandwidth_is_adjustable()  # e.g. not in Manjaro Linux / Ubuntu 14.04

        self.device_number = device_number

        self.error_codes = {
            -100: "Method not available in installed driver."
        }

    @staticmethod
    def get_bandwidth_is_adjustable():
        return rtlsdr.bandwidth_is_adjustable()

    @property
    def device_parameters(self):
        return OrderedDict([(self.Command.SET_FREQUENCY.name, self.frequency),
                            (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                            (self.Command.SET_BANDWIDTH.name, self.bandwidth),
                            (self.Command.SET_FREQUENCY_CORRECTION.name, self.freq_correction),
                            (self.Command.SET_DIRECT_SAMPLING_MODE.name, self.direct_sampling_mode),
                            (self.Command.SET_RF_GAIN.name, self.gain),
                            ("identifier", self.device_number)])

    @property
    def has_multi_device_support(self):
        return True

    def set_device_bandwidth(self, bandwidth):
        if self.bandwidth_is_adjustable:
            super().set_device_bandwidth(bandwidth)
        else:
            logger.warning("Setting the bandwidth is not supported by your RTL-SDR driver version.")

    @staticmethod
    def bytes_to_iq(buffer):
        return np.subtract(np.frombuffer(buffer, dtype=np.int8), 127).reshape((-1, 2), order="C")
