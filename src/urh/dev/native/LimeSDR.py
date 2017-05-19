from collections import OrderedDict

import numpy as np
from urh.dev.native.Device import Device
from urh.dev.native.lib import limesdr
from multiprocessing.connection import Connection


class LimeSDR(Device):
    READ_SAMPLES = 32768
    SEND_SAMPLES = 32768
    CONTINUOUS_SEND_SAMPLES = SEND_SAMPLES * 64

    RECV_FIFO_SIZE = 1048576
    SEND_FIFO_SIZE = 8 * SEND_SAMPLES
    SEND_BUFFER_SIZE = SEND_SAMPLES  # for compatibility with API
    CONTINUOUS_SEND_BUFFER_SIZE = CONTINUOUS_SEND_SAMPLES

    LIME_TIMEOUT_RECEIVE_MS = 10
    LIME_TIMEOUT_SEND_MS = 500

    BYTES_PER_SAMPLE = 8  # We use dataFmt_t.LMS_FMT_F32 so we have 32 bit floats for I and Q
    DEVICE_LIB = limesdr
    ASYNCHRONOUS = False
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_center_frequency",
        Device.Command.SET_BANDWIDTH.name: "set_lpf_bandwidth",
        Device.Command.SET_RF_GAIN.name: "set_normalized_gain",
        Device.Command.SET_CHANNEL_INDEX.name: "set_channel",
        Device.Command.SET_ANTENNA_INDEX.name: "set_antenna"
    })

    @classmethod
    def adapt_num_read_samples_to_sample_rate(cls, sample_rate):
        cls.READ_SAMPLES = 16384 * int(sample_rate/1e6)
        cls.RECV_FIFO_SIZE = 16 * cls.READ_SAMPLES

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = limesdr.open()
        ctrl_connection.send("OPEN:" + str(ret))
        limesdr.disable_all_channels()
        if ret != 0:
            return False

        ret = limesdr.init()
        ctrl_connection.send("INIT:" + str(ret))

        return ret == 0

    @classmethod
    def init_device(cls, ctrl_connection: Connection, is_tx: bool, parameters: OrderedDict):
        if not cls.setup_device(ctrl_connection, device_identifier=None):
            return False

        limesdr.set_tx(is_tx)

        for parameter, value in parameters.items():
            cls.process_command((parameter, value), ctrl_connection, is_tx)

        antennas = limesdr.get_antenna_list()
        ctrl_connection.send("Current normalized gain is {0:.2f}".format(limesdr.get_normalized_gain()))
        ctrl_connection.send("Current antenna is {0}".format(antennas[limesdr.get_antenna()]))
        ctrl_connection.send("Current chip temperature is {0:.2f}°C".format(limesdr.get_chip_temperature()))

        limesdr.enable_channel(True, is_tx, parameters[cls.Command.SET_CHANNEL_INDEX.name])

        return True

    @classmethod
    def shutdown_device(cls, ctrl_connection):
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

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        limesdr.recv_stream(data_conn, cls.READ_SAMPLES, cls.LIME_TIMEOUT_RECEIVE_MS)

    @classmethod
    def prepare_sync_send(cls, ctrl_connection: Connection):
        ctrl_connection.send("Initializing stream...")
        limesdr.setup_stream(cls.SEND_FIFO_SIZE)
        ret = limesdr.start_stream()
        ctrl_connection.send("Initialize stream:{0}".format(ret))

    @classmethod
    def send_sync(cls, data):
        limesdr.send_stream(data, cls.LIME_TIMEOUT_SEND_MS)

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.success = 0

    def set_device_gain(self, gain):
        super().set_device_gain(gain * 0.01)

    @property
    def device_parameters(self):
        return OrderedDict([(self.Command.SET_CHANNEL_INDEX.name, self.channel_index),
                            # Set Antenna needs to be called before other stuff!!!
                            (self.Command.SET_ANTENNA_INDEX.name, self.antenna_index),
                            (self.Command.SET_FREQUENCY.name, self.frequency),
                            (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                            (self.Command.SET_BANDWIDTH.name, self.bandwidth),
                            (self.Command.SET_RF_GAIN.name, self.gain * 0.01)])

    @staticmethod
    def unpack_complex(buffer, nvalues: int):
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.float32), ('i', np.float32)])
        result.real = unpacked["r"]
        result.imag = unpacked["i"]
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        # We can pass the complex samples directly to the LimeSDR Send API
        return complex_samples.view(np.float32)
