import re
from collections import OrderedDict
from multiprocessing.connection import Connection
from multiprocessing import Array

from urh.dev.native.Device import Device
from urh.dev.native.lib import plutosdr

import numpy as np


class PlutoSDR(Device):
    SYNC_RX_CHUNK_SIZE = 65536
    SYNC_TX_CHUNK_SIZE = 65536

    DEVICE_LIB = plutosdr
    ASYNCHRONOUS = False

    @classmethod
    def get_device_list(cls):
        descs, uris = plutosdr.scan_devices()
        return ["{} [{}]".format(desc, uri) for desc, uri in zip(descs, uris)]

    @classmethod
    def adapt_num_read_samples_to_sample_rate(cls, sample_rate):
        pass

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        device_identifier = device_identifier if isinstance(device_identifier, str) else ""
        try:
            device_identifier = re.search("\[.*\]", device_identifier).groups(0)
        except (IndexError, AttributeError):
            pass

        if not device_identifier:
            _, uris = plutosdr.scan_devices()
            try:
                device_identifier = uris[0]
            except IndexError:
                ctrl_connection.send("Could find a connected PlutoSDR")
                return False

        ret = plutosdr.open(device_identifier)
        ctrl_connection.send("OPEN ({}):{}".format(device_identifier, ret))
        return ret == 0

    @classmethod
    def init_device(cls, ctrl_connection: Connection, is_tx: bool, parameters: OrderedDict) -> bool:
        plutosdr.set_tx(is_tx)
        return super().init_device(ctrl_connection, is_tx, parameters)

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx: bool):
        ret = plutosdr.close()
        ctrl_connection.send("CLOSE:" + str(ret))
        return True

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing PlutoSDR..")
        ret = plutosdr.setup_rx(cls.SYNC_RX_CHUNK_SIZE)
        return ret

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        plutosdr.receive_sync(data_conn)

    @classmethod
    def prepare_sync_send(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing PlutoSDR...")
        ret = plutosdr.setup_tx(cls.SYNC_TX_CHUNK_SIZE // 2)
        return ret

    @classmethod
    def send_sync(cls, data):
        plutosdr.send_sync(data)

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
        return OrderedDict([(self.Command.SET_FREQUENCY.name, self.frequency),
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
        # https://wiki.analog.com/resources/eval/user-guides/ad-fmcomms2-ebz/software/basic_iq_datafiles#binary_format
        numpy_view[:] = np.left_shift((2048 * complex_samples.view(np.float32)).astype(np.int16), 4)
        return arr
