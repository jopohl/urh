from collections import OrderedDict
from multiprocessing import Array
from multiprocessing.connection import Connection

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import limesdr


class LimeSDR(Device):
    SYNC_RX_CHUNK_SIZE = 32768
    SYNC_TX_CHUNK_SIZE = 32768

    RECV_FIFO_SIZE = 1048576
    SEND_FIFO_SIZE = 8 * SYNC_TX_CHUNK_SIZE
    CONTINUOUS_TX_CHUNK_SIZE = SYNC_TX_CHUNK_SIZE * 64

    LIME_TIMEOUT_RECEIVE_MS = 10
    LIME_TIMEOUT_SEND_MS = 500

    DEVICE_LIB = limesdr
    ASYNCHRONOUS = False
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update(
        {
            Device.Command.SET_FREQUENCY.name: "set_center_frequency",
            Device.Command.SET_BANDWIDTH.name: "set_lpf_bandwidth",
            Device.Command.SET_RF_GAIN.name: "set_normalized_gain",
            Device.Command.SET_CHANNEL_INDEX.name: "set_channel",
            Device.Command.SET_ANTENNA_INDEX.name: "set_antenna",
        }
    )

    DATA_TYPE = np.float32

    @classmethod
    def get_device_list(cls):
        return limesdr.get_device_list()

    @classmethod
    def adapt_num_read_samples_to_sample_rate(cls, sample_rate):
        cls.SYNC_RX_CHUNK_SIZE = 16384 * int(sample_rate / 1e6)
        cls.RECV_FIFO_SIZE = 16 * cls.SYNC_RX_CHUNK_SIZE

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = limesdr.open(device_identifier)
        if not device_identifier:
            ctrl_connection.send("OPEN:" + str(ret))
        else:
            ctrl_connection.send("OPEN ({}):{}".format(device_identifier, ret))
        limesdr.disable_all_channels()
        if ret != 0:
            return False

        ret = limesdr.init()
        ctrl_connection.send("INIT:" + str(ret))

        return ret == 0

    @classmethod
    def init_device(
        cls, ctrl_connection: Connection, is_tx: bool, parameters: OrderedDict
    ):
        if not cls.setup_device(
            ctrl_connection, device_identifier=parameters["identifier"]
        ):
            return False

        limesdr.enable_channel(
            True, is_tx, parameters[cls.Command.SET_CHANNEL_INDEX.name]
        )
        limesdr.set_tx(is_tx)

        for parameter, value in parameters.items():
            cls.process_command((parameter, value), ctrl_connection, is_tx)

        antennas = limesdr.get_antenna_list()
        ctrl_connection.send(
            "Current normalized gain is {0:.2f}".format(limesdr.get_normalized_gain())
        )
        ctrl_connection.send(
            "Current antenna is {0}".format(antennas[limesdr.get_antenna()])
        )
        ctrl_connection.send(
            "Current chip temperature is {0:.2f}°C".format(
                limesdr.get_chip_temperature()
            )
        )

        return True

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx: bool):
        limesdr.stop_stream()
        limesdr.destroy_stream()
        limesdr.disable_all_channels()
        ret = limesdr.close()
        ctrl_connection.send("CLOSE:" + str(ret))
        return True

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing stream...")
        limesdr.setup_stream(cls.RECV_FIFO_SIZE)
        ret = limesdr.start_stream()
        ctrl_connection.send("Initialize stream:{0}".format(ret))
        return ret

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        limesdr.recv_stream(
            data_conn, cls.SYNC_RX_CHUNK_SIZE, cls.LIME_TIMEOUT_RECEIVE_MS
        )

    @classmethod
    def prepare_sync_send(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing stream...")
        limesdr.setup_stream(cls.SEND_FIFO_SIZE)
        ret = limesdr.start_stream()
        ctrl_connection.send("Initialize stream:{0}".format(ret))
        return ret

    @classmethod
    def send_sync(cls, data):
        limesdr.send_stream(data, cls.LIME_TIMEOUT_SEND_MS)

    def __init__(
        self,
        center_freq,
        sample_rate,
        bandwidth,
        gain,
        if_gain=1,
        baseband_gain=1,
        resume_on_full_receive_buffer=False,
    ):
        super().__init__(
            center_freq=center_freq,
            sample_rate=sample_rate,
            bandwidth=bandwidth,
            gain=gain,
            if_gain=if_gain,
            baseband_gain=baseband_gain,
            resume_on_full_receive_buffer=resume_on_full_receive_buffer,
        )
        self.success = 0

    def set_device_gain(self, gain):
        super().set_device_gain(gain * 0.01)

    @property
    def has_multi_device_support(self):
        return True

    @property
    def device_parameters(self):
        return OrderedDict(
            [
                (self.Command.SET_CHANNEL_INDEX.name, self.channel_index),
                # Set Antenna needs to be called before other stuff!!!
                (self.Command.SET_ANTENNA_INDEX.name, self.antenna_index),
                (self.Command.SET_FREQUENCY.name, self.frequency),
                (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                (self.Command.SET_BANDWIDTH.name, self.bandwidth),
                (self.Command.SET_RF_GAIN.name, self.gain * 0.01),
                ("identifier", self.device_serial),
            ]
        )

    @staticmethod
    def bytes_to_iq(buffer):
        return np.frombuffer(buffer, dtype=np.float32).reshape((-1, 2), order="C")

    @staticmethod
    def iq_to_bytes(samples: np.ndarray):
        arr = Array("f", 2 * len(samples), lock=False)
        numpy_view = np.frombuffer(arr, dtype=np.float32)
        numpy_view[:] = samples.flatten(order="C")
        return arr
