import numpy as np

from multiprocessing.connection import Connection

from urh.dev.native.Device import Device
from urh.dev.native.lib import hackrf
from urh.util.Logger import logger


class HackRF(Device):
    BYTES_PER_SAMPLE = 2  # HackRF device produces 8 bit unsigned IQ data
    DEVICE_LIB = hackrf
    ASYNCHRONOUS = True
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_freq",
        Device.Command.SET_BANDWIDTH.name: "set_baseband_filter_bandwidth"
    })

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = hackrf.setup()
        ctrl_connection.send("SETUP:" + str(ret))
        return ret == 0

    @classmethod
    def shutdown_device(cls, ctrl_conn: Connection):
        logger.debug("HackRF: closing device")
        ret = hackrf.close()
        ctrl_conn.send("CLOSE:" + str(ret))

        ret = hackrf.exit()
        ctrl_conn.send("EXIT:" + str(ret))

        return True

    @classmethod
    def enter_async_receive_mode(cls, data_connection: Connection):
        hackrf.start_rx_mode(data_connection.send_bytes)

    @classmethod
    def enter_async_send_mode(cls, callback):
        hackrf.start_tx_mode(callback)

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

    @staticmethod
    def unpack_complex(buffer, nvalues: int):
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.int8), ('i', np.int8)])
        result.real = (unpacked['r'] + 0.5) / 127.5
        result.imag = (unpacked['i'] + 0.5) / 127.5
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        assert complex_samples.dtype == np.complex64
        return (127.5 * ((complex_samples.view(np.float32)) - 0.5 / 127.5)).astype(np.int8)
