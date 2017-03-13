import numpy as np
from urh.dev.native.Device import Device
from urh.dev.native.lib import hackrf
from urh.util.Logger import logger


class HackRF(Device):
    BYTES_PER_SAMPLE = 2  # HackRF device produces 8 bit unsigned IQ data

    @staticmethod
    def initialize_hackrf(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, ctrl_conn, is_tx):
        ret = hackrf.setup()
        ctrl_conn.send("setup:" + str(ret))
        if ret != 0:
            return False

        ret = hackrf.set_freq(freq)
        ctrl_conn.send("set_center_freq to {0}:{1}".format(freq, ret))

        ret = hackrf.set_sample_rate(sample_rate)
        ctrl_conn.send("set_sample_rate to {0}:{1}".format(sample_rate, ret))

        ret = hackrf.set_rf_gain(gain)
        ctrl_conn.send("set_rf_gain to {0}:{1}".format(gain, ret))

        if is_tx:
            ret = hackrf.set_if_tx_gain(if_gain)
            ctrl_conn.send("set_if_gain to {0}:{1}".format(if_gain, ret))
        else:
            ret = hackrf.set_if_rx_gain(if_gain)
            ctrl_conn.send("set_if_gain to {0}:{1}".format(if_gain, ret))

            ret = hackrf.set_baseband_gain(baseband_gain)
            ctrl_conn.send("set_baseband_gain to {0}:{1}".format(baseband_gain, ret))

        ret = hackrf.set_baseband_filter_bandwidth(bandwidth)
        ctrl_conn.send("set_bandwidth to {0}:{1}".format(bandwidth, ret))

        return True

    @staticmethod
    def shutdown_hackrf(ctrl_conn):
        logger.debug("HackRF: closing device")
        ret = hackrf.close()
        ctrl_conn.send("close:" + str(ret))

        ret = hackrf.exit()
        ctrl_conn.send("exit:" + str(ret))

        return True

    @staticmethod
    def hackrf_receive(data_connection, ctrl_connection, freq, sample_rate, bandwidth, gain, if_gain, baseband_gain):
        def callback_recv(buffer):
            try:
                data_connection.send_bytes(buffer)
            except (BrokenPipeError, EOFError):
                pass
            return 0

        if not HackRF.initialize_hackrf(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, ctrl_connection, is_tx=False):
            return False

        hackrf.start_rx_mode(callback_recv)

        exit_requested = False

        while not exit_requested:
            while ctrl_connection.poll():
                result = HackRF.process_command(ctrl_connection.recv(), ctrl_connection, is_tx=False)
                if result == "stop":
                    exit_requested = True
                    break

        HackRF.shutdown_hackrf(ctrl_connection)
        data_connection.close()
        ctrl_connection.close()

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
            while ctrl_connection.poll():
                result = HackRF.process_command(ctrl_connection.recv(), ctrl_connection, is_tx=True)
                if result == "stop":
                    exit_requested = True
                    break

        if exit_requested:
            logger.debug("HackRF: exit requested. Stopping sending")
        if sending_is_finished():
            logger.debug("HackRF: sending is finished.")

        HackRF.shutdown_hackrf(ctrl_connection)
        ctrl_connection.close()

    @staticmethod
    def process_command(command, ctrl_connection, is_tx: bool):
        is_rx = not is_tx
        if command == "stop":
            return "stop"

        tag, value = command.split(":")
        if tag == "center_freq":
            ret = hackrf.set_freq(int(value))
            ctrl_connection.send("set_center_freq to {0}:{1}".format(value, ret))

        elif tag == "rf_gain":
            ret = hackrf.set_rf_gain(int(value))
            ctrl_connection.send("set_rf_gain to {0}:{1}".format(value, ret))

        elif tag == "if_gain" and is_rx:
            ret = hackrf.set_if_rx_gain(int(value))
            ctrl_connection.send("set_if_gain to {0}:{1}".format(value, ret))

        elif tag == "if_gain" and is_tx:
            ret = hackrf.set_if_tx_gain(int(value))
            ctrl_connection.send("set_if_gain to {0}:{1}".format(value, ret))

        elif tag == "baseband_gain" and is_rx:
            ret = hackrf.set_baseband_gain(int(value))
            ctrl_connection.send("set_baseband_gain to {0}:{1}".format(value, ret))

        elif tag == "sample_rate":
            ret = hackrf.set_sample_rate(int(value))
            ctrl_connection.send("set_sample_rate to {0}:{1}".format(value, ret))

        elif tag == "bandwidth":
            ret = hackrf.set_baseband_filter_bandwidth(int(value))
            ctrl_connection.send("set_bandwidth to {0}:{1}".format(value, ret))

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1, is_ringbuffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain, is_ringbuffer=is_ringbuffer)
        self.success = 0

        self.receive_process_function = HackRF.hackrf_receive
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
