from collections import OrderedDict

import numpy as np
from multiprocessing import Array

from urh.dev.native.Device import Device
from urh.dev.native.lib import usrp
from multiprocessing.connection import Connection


class USRP(Device):
    SYNC_RX_CHUNK_SIZE = 16384
    SYNC_TX_CHUNK_SIZE = 16384 * 2
    CONTINUOUS_TX_CHUNK_SIZE = -1  # take everything from queue

    DEVICE_LIB = usrp
    ASYNCHRONOUS = False

    @classmethod
    def get_device_list(cls):
        return usrp.find_devices("")

    @classmethod
    def adapt_num_read_samples_to_sample_rate(cls, sample_rate):
        cls.SYNC_RX_CHUNK_SIZE = 16384 * int(sample_rate / 1e6)

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = usrp.open(device_identifier)
        if device_identifier:
            ctrl_connection.send("OPEN ({}):{}".format(device_identifier, ret))
        else:
            ctrl_connection.send("OPEN:" + str(ret))
        success = ret == 0
        if success:
            device_repr = usrp.get_device_representation()
            ctrl_connection.send(device_repr)
        return success

    @classmethod
    def init_device(cls, ctrl_connection: Connection, is_tx: bool, parameters: OrderedDict):
        usrp.set_tx(is_tx)
        return super().init_device(ctrl_connection, is_tx, parameters)

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx: bool):
        usrp.stop_stream()
        usrp.destroy_stream()
        ret = usrp.close()
        ctrl_connection.send("CLOSE:" + str(ret))
        return True

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing stream...")
        usrp.setup_stream()
        return usrp.start_stream(cls.SYNC_RX_CHUNK_SIZE)

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        usrp.recv_stream(data_conn, cls.SYNC_RX_CHUNK_SIZE)

    @classmethod
    def prepare_sync_send(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing stream...")
        usrp.setup_stream()
        ret = usrp.start_stream(0)
        ctrl_connection.send("Initialize stream:{0}".format(ret))
        return ret

    @classmethod
    def send_sync(cls, data):
        usrp.send_stream(data)

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.success = 0

    def set_device_gain(self, gain):
        super().set_device_gain(gain * 0.01)

    @property
    def has_multi_device_support(self):
        return True

    @property
    def device_parameters(self):
        return OrderedDict([(self.Command.SET_CHANNEL_INDEX.name, self.channel_index),
                            # Set Antenna needs to be called before other stuff!!!
                            (self.Command.SET_ANTENNA_INDEX.name, self.antenna_index),
                            (self.Command.SET_FREQUENCY.name, self.frequency),
                            (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                            (self.Command.SET_BANDWIDTH.name, self.bandwidth),
                            (self.Command.SET_RF_GAIN.name, self.gain * 0.01),
                            ("identifier", self.device_serial)])

    @staticmethod
    def unpack_complex(buffer):
        return np.frombuffer(buffer, dtype=np.complex64)

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        # We can pass the complex samples directly to the USRP Send API
        arr = Array("f", 2 * len(complex_samples), lock=False)
        numpy_view = np.frombuffer(arr, dtype=np.float32)
        numpy_view[:] = complex_samples.view(np.float32)
        return arr
