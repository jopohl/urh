import numpy as np
import time

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
    def setup_device(cls, ctrl_connection):
        ret = hackrf.setup()
        ctrl_connection.send("SETUP:" + str(ret))
        return ret == 0

    @classmethod
    def shutdown_device(cls, ctrl_conn):
        logger.debug("HackRF: closing device")
        ret = hackrf.close()
        ctrl_conn.send("CLOSE:" + str(ret))

        ret = hackrf.exit()
        ctrl_conn.send("EXIT:" + str(ret))

        return True

    @classmethod
    def enter_async_receive_mode(cls, data_connection: Connection):
        hackrf.start_rx_mode(data_connection.send_bytes)

    @staticmethod
    def hackrf_send(ctrl_connection, freq, sample_rate, bandwidth, gain, if_gain, baseband_gain,
                    send_buffer, current_sent_index, current_sending_repeat, sending_repeats):
        def sending_is_finished():
            if sending_repeats == 0:  # 0 = infinity
                return False

            return current_sending_repeat.value >= sending_repeats and current_sent_index.value >= len(send_buffer)

        def callback_send(buffer_length):
            try:
                if sending_is_finished():
                    return b""

                result = send_buffer[current_sent_index.value:current_sent_index.value + buffer_length]
                current_sent_index.value += buffer_length
                if current_sent_index.value >= len(send_buffer) - 1:
                    current_sending_repeat.value += 1
                    if current_sending_repeat.value < sending_repeats or sending_repeats == 0:  # 0 = infinity
                        current_sent_index.value = 0
                    else:
                        current_sent_index.value = len(send_buffer)

                return result
            except (BrokenPipeError, EOFError):
                return b""

        if not HackRF.initialize_hackrf(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, ctrl_connection, is_tx=True):
            return False

        hackrf.start_tx_mode(callback_send)

        exit_requested = False

        while not exit_requested and not sending_is_finished():
            time.sleep(0.5)
            while ctrl_connection.poll():
                result = HackRF.process_command(ctrl_connection.recv(), ctrl_connection, is_tx=True)
                if result == HackRF.Command.STOP.name:
                    exit_requested = True
                    break

        if exit_requested:
            logger.debug("HackRF: exit requested. Stopping sending")
        if sending_is_finished():
            logger.debug("HackRF: sending is finished.")

        HackRF.shutdown_hackrf(ctrl_connection)
        ctrl_connection.close()

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1, is_ringbuffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain, is_ringbuffer=is_ringbuffer)
        self.success = 0

        self.receive_process_function = HackRF.device_receive
        self.send_process_function = HackRF.hackrf_send

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
        # tostring() is a compatibility (numpy<1.9) alias for tobytes(). Despite its name it returns bytes not strings.
        return (127.5 * ((complex_samples.view(np.float32)) - 0.5 / 127.5)).astype(np.int8).tostring()
