from multiprocessing import Array
from multiprocessing.connection import Connection

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import hackrf


class HackRF(Device):
    DEVICE_LIB = hackrf
    ASYNCHRONOUS = True
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_freq",
        Device.Command.SET_BANDWIDTH.name: "set_baseband_filter_bandwidth"
    })

    @classmethod
    def get_device_list(cls):
        result = hackrf.get_device_list()
        if result is None:
            return []
        return result

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = hackrf.setup(device_identifier)
        msg = "SETUP"
        if device_identifier:
            msg += " ({})".format(device_identifier)
        msg += ": "+str(ret)
        ctrl_connection.send(msg)

        return ret == 0

    @classmethod
    def shutdown_device(cls, ctrl_conn: Connection, is_tx: bool):
        if is_tx:
            result = hackrf.stop_tx_mode()
            ctrl_conn.send("STOP TX MODE:" + str(result))
        else:
            result = hackrf.stop_rx_mode()
            ctrl_conn.send("STOP RX MODE:" + str(result))

        result = hackrf.close()
        ctrl_conn.send("CLOSE:" + str(result))

        result = hackrf.exit()
        ctrl_conn.send("EXIT:" + str(result))

        return True

    @classmethod
    def enter_async_receive_mode(cls, data_connection: Connection, ctrl_connection: Connection):
        ret = hackrf.start_rx_mode(data_connection.send_bytes)
        ctrl_connection.send("Start RX MODE:" + str(ret))
        return ret

    @classmethod
    def enter_async_send_mode(cls, callback):
        return hackrf.start_tx_mode(callback)

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.success = 0

        self.error_codes = {
            0: "HACKRF_SUCCESS",
            1: "HACKRF_TRUE",
            1337: "TIMEOUT ERROR",
            -2: "HACKRF_ERROR_INVALID_PARAM",
            -5: "HACKRF_ERROR_NOT_FOUND",
            -6: "HACKRF_ERROR_BUSY",
            -11: "HACKRF_ERROR_NO_MEM",
            -1000: "HACKRF_ERROR_LIBUSB",
            -1001: "HACKRF_ERROR_THREAD",
            -1002: "HACKRF_ERROR_STREAMING_THREAD_ERR",
            -1003: "HACKRF_ERROR_STREAMING_STOPPED",
            -1004: "HACKRF_ERROR_STREAMING_EXIT_CALLED",
            -4242: "HACKRF NOT OPEN",
            -9999: "HACKRF_ERROR_OTHER"
        }

    @property
    def has_multi_device_support(self):
        return hackrf.has_multi_device_support()

    @staticmethod
    def unpack_complex(buffer):
        unpacked = np.frombuffer(buffer, dtype=[('r', np.int8), ('i', np.int8)])
        result = np.empty(len(unpacked), dtype=np.complex64)
        result.real = (unpacked['r'] + 0.5) / 127.5
        result.imag = (unpacked['i'] + 0.5) / 127.5
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        assert complex_samples.dtype == np.complex64
        arr = Array("B", 2*len(complex_samples), lock=False)
        numpy_view = np.frombuffer(arr, dtype=np.int8)
        numpy_view[:] = (127.5 * ((complex_samples.view(np.float32)) - 0.5 / 127.5)).astype(np.int8)
        return arr
