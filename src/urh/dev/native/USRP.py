from collections import OrderedDict

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import usrp
from multiprocessing.connection import Connection

class USRP(Device):
    READ_SAMPLES = 8192

    BYTES_PER_SAMPLE = 8
    DEVICE_LIB = usrp
    ASYNCHRONOUS = False

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = usrp.open(device_identifier)
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
    def shutdown_device(cls, ctrl_connection):
        usrp.destroy_stream()
        ret = usrp.close()
        ctrl_connection.send("CLOSE:" + str(ret))
        return True

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing stream...")
        usrp.setup_stream()
        ctrl_connection.send("Initialized stream")

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        usrp.recv_stream(data_conn, USRP.READ_SAMPLES)

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.device_args = ""
        self.success = 0

    @property
    def device_parameters(self):
        return OrderedDict([(self.Command.SET_CHANNEL_INDEX.name, self.channel_index),
                            # Set Antenna needs to be called before other stuff!!!
                            (self.Command.SET_ANTENNA_INDEX.name, self.antenna_index),
                            (self.Command.SET_FREQUENCY.name, self.frequency),
                            (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                            (self.Command.SET_BANDWIDTH.name, self.bandwidth),
                            (self.Command.SET_RF_GAIN.name, self.gain),
                            ("identifier", self.device_args)])


    @staticmethod
    def unpack_complex(buffer, nvalues: int):
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.float32), ('i', np.float32)])
        result.real = unpacked["r"]
        result.imag = unpacked["i"]
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        # We can pass the complex samples directly to the USRP Send API
        return complex_samples.view(np.float32)
