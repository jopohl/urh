from collections import OrderedDict
from multiprocessing import Array

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import bladerf
from multiprocessing.connection import Connection


class BladeRF(Device):
    SYNC_RX_CHUNK_SIZE = 16384
    SYNC_TX_CHUNK_SIZE = 16384

    DEVICE_LIB = bladerf
    ASYNCHRONOUS = False
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_RF_GAIN.name: "set_gain",
        Device.Command.SET_CHANNEL_INDEX.name: "set_channel"
    })

    @classmethod
    def get_device_list(cls):
        return bladerf.get_device_list()

    @classmethod
    def adapt_num_read_samples_to_sample_rate(cls, sample_rate):
        cls.SYNC_RX_CHUNK_SIZE = 16384 * int(sample_rate / 1e6)

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        if not device_identifier:
            device_identifier = ""

        ret = bladerf.open(device_identifier)
        if not device_identifier:
            ctrl_connection.send("OPEN:" + str(ret))
        else:
            ctrl_connection.send("OPEN ({}):{}".format(device_identifier, ret))

        ctrl_connection.send("If you experience problems, make sure you place a rbf file matching your device"
                             " at the correct location. See http://www.nuand.com/fpga_images/"
                             " and https://github.com/Nuand/bladeRF/wiki/FPGA-Autoloading")

        return ret == 0

    @classmethod
    def init_device(cls, ctrl_connection: Connection, is_tx: bool, parameters: OrderedDict) -> bool:
        bladerf.set_tx(is_tx)
        return super().init_device(ctrl_connection, is_tx, parameters)

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx: bool):
        ret = bladerf.close()
        ctrl_connection.send("CLOSE:" + str(ret))
        return True

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing BladeRF..")
        ret = bladerf.prepare_sync()
        return ret

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        bladerf.receive_sync(data_conn, cls.SYNC_RX_CHUNK_SIZE)

    @classmethod
    def prepare_sync_send(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing BladeRF...")
        ret = bladerf.prepare_sync()
        return ret

    @classmethod
    def send_sync(cls, data):
        bladerf.send_sync(data)

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.success = 0

    @property
    def has_multi_device_support(self):
        return True

    @property
    def device_parameters(self):
        return OrderedDict([(self.Command.SET_CHANNEL_INDEX.name, self.channel_index),
                            (self.Command.SET_FREQUENCY.name, self.frequency),
                            (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                            (self.Command.SET_BANDWIDTH.name, self.bandwidth),
                            (self.Command.SET_RF_GAIN.name, self.gain),
                            ("identifier", self.device_serial)])

    @staticmethod
    def unpack_complex(buffer):
        unpacked = np.frombuffer(buffer, dtype=np.int16)
        result = np.empty(len(unpacked)//2, dtype=np.complex64)
        result.real = unpacked[::2] / 2048
        result.imag = unpacked[1::2] / 2048
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        arr = Array("h", 2 * len(complex_samples), lock=False)
        numpy_view = np.frombuffer(arr, dtype=np.int16)
        numpy_view[:] = (2048 * complex_samples.view(np.float32)).astype(np.int16)
        return arr
