import numpy as np
from urh.dev.native.Device import Device
from urh.dev.native.lib import hackrf
from urh.util.Logger import logger


class HackRF(Device):
    BYTES_PER_SAMPLE = 2  # HackRF device produces 8 bit unsigned IQ data

    @staticmethod
    def initialize_hackrf(freq, sample_rate, gain, bw, ctrl_conn):
        ret = hackrf.setup()
        ctrl_conn.send("setup:" + str(ret))
        if ret != 0:
            return False

        ret = hackrf.set_freq(freq)
        ctrl_conn.send("set_freq:" + str(ret))

        ret = hackrf.set_sample_rate(sample_rate)
        ctrl_conn.send("set_sample_rate:" + str(ret))

        ret = hackrf.set_lna_gain(gain)
        ctrl_conn.send("set_lna_gain:" + str(ret))

        ret = hackrf.set_vga_gain(gain)
        ctrl_conn.send("set_vga_gain:" + str(ret))

        ret = hackrf.set_txvga_gain(gain)
        ctrl_conn.send("set_txvga_gain:" + str(ret))

        ret = hackrf.set_baseband_filter_bandwidth(bw)
        ctrl_conn.send("set_bandwidth:" + str(ret))

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
    def hackrf_receive(data_connection, ctrl_connection, freq, sample_rate, gain, bw):
        def callback_recv(buffer):
            try:
                data_connection.send_bytes(buffer)
            except (BrokenPipeError, EOFError):
                pass
            return 0

        if not HackRF.initialize_hackrf(freq, sample_rate, gain, bw, ctrl_connection):
            return False

        hackrf.start_rx_mode(callback_recv)

        exit_requested = False

        while not exit_requested:
            while ctrl_connection.poll():
                result = HackRF.process_command(ctrl_connection.recv())
                if result == "stop":
                    exit_requested = True
                    break

        HackRF.shutdown_hackrf(ctrl_connection)
        data_connection.close()
        ctrl_connection.close()

    @staticmethod
    def hackrf_send(ctrl_connection, freq, sample_rate, gain, bw,
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

        if not HackRF.initialize_hackrf(freq, sample_rate, gain, bw, ctrl_connection):
            return False

        hackrf.start_tx_mode(callback_send)

        exit_requested = False

        while not exit_requested and not sending_is_finished():
            while ctrl_connection.poll():
                result = HackRF.process_command(ctrl_connection.recv())
                if result == "stop":
                    exit_requested = True
                    break

        HackRF.shutdown_hackrf(ctrl_connection)
        ctrl_connection.close()

    @staticmethod
    def process_command(command):
        logger.debug("HackRF: {}".format(command))
        if command == "stop":
            return "stop"

        tag, value = command.split(":")
        if tag == "center_freq":
            logger.info("HackRF: Set center freq to {0}".format(int(value)))
            return hackrf.set_freq(int(value))

        elif tag == "gain":
            logger.info("HackRF: Set gain to {0}".format(int(value)))
            hackrf.set_lna_gain(int(value))
            hackrf.set_vga_gain(int(value))
            hackrf.set_txvga_gain(int(value))

        elif tag == "sample_rate":
            logger.info("HackRF: Set sample_rate to {0}".format(int(value)))
            return hackrf.set_sample_rate(int(value))

        elif tag == "bandwidth":
            logger.info("HackRF: Set bandwidth to {0}".format(int(value)))
            return hackrf.set_baseband_filter_bandwidth(int(value))

    def __init__(self, bw, freq, gain, srate, is_ringbuffer=False):
        super().__init__(bw, freq, gain, srate, is_ringbuffer)
        self.success = 0

        self.receive_process_function = HackRF.hackrf_receive
        self.send_process_function = HackRF.hackrf_send

        self._max_bandwidth = 28e6
        self._max_frequency = 6e9
        self._max_sample_rate = 20e6
        self._max_gain = 40

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

    def set_device_gain(self, gain):
        self.parent_ctrl_conn.send("gain:" + str(int(gain)))

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
