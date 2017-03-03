import numpy as np
import time

from multiprocessing import Value

from multiprocessing import Process

from multiprocessing import Pipe

from urh.dev.native.Device import Device
from urh.dev.native.lib import hackrf
from urh.util.Logger import logger

def hackrf_run(connection, mode, freq, sample_rate, gain, bw):
    def callback_recv(buffer):
        try:
            connection.send_bytes(buffer)
        except BrokenPipeError:
            pass
        return 0


    hackrf.setup()
    hackrf.open()
    hackrf.set_freq(freq)
    hackrf.set_sample_rate(sample_rate)
    hackrf.set_lna_gain(gain)
    hackrf.set_vga_gain(gain)
    hackrf.set_txvga_gain(gain)
    hackrf.set_baseband_filter_bandwidth(bw)

    if mode == 0:
        hackrf.start_rx_mode(callback_recv)
    else:
        # TODO refactor send mode
        pass
        #hackrf.start_tx_mode()

    exit_requested = False

    while not exit_requested:
        while connection.poll():
            result = process_command(connection.recv())
            if result == "stop":
                exit_requested = True
                break

    logger.debug("HackRF: closing device")
    hackrf.close()
    hackrf.exit()
    connection.close()


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

class HackRF(Device):
    BYTES_PER_SAMPLE = 2  # HackRF device produces 8 bit unsigned IQ data

    def __init__(self, bw, freq, gain, srate, is_ringbuffer=False):
        super().__init__(bw, freq, gain, srate, is_ringbuffer)
        self.success = 0

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


    def open(self, init=True):
        pass  # happens in process

    def close(self, exit=True):
        pass  # happens in process

    def exit(self):
        pass  # happens in process


    def start_rx_mode(self):
        self.init_recv_buffer()

        self.is_open = True
        self.is_receiving = True
        self.receive_process = Process(target=hackrf_run, args=(self.child_conn, 0, self.frequency,
                                                                self.sample_rate, self.gain, self.bandwidth
                                                                  ))
        self.receive_process.daemon = True
        self._start_read_rcv_buffer_thread()
        self.receive_process.start()

    def stop_rx_mode(self, msg):
        self.is_receiving = False
        self.parent_conn.send("stop")

        logger.info("HackRF: Stopping RX Mode: " + msg)

        if hasattr(self, "receive_process"):
            self.receive_process.join(0.3)
            if self.receive_process.is_alive():
                logger.warning("HackRF: Receive process is still alive, terminating it")
                self.receive_process.terminate()
                self.receive_process.join()
                self.parent_conn, self.child_conn = Pipe()

        if hasattr(self, "read_queue_thread") and self.read_recv_buffer_thread.is_alive():
            try:
                self.read_recv_buffer_thread.join(0.001)
                logger.info("HackRF: Joined read_queue_thread")
            except RuntimeError:
                logger.error("HackRF: Could not join read_queue_thread")

    def start_tx_mode(self, samples_to_send: np.ndarray = None, repeats=None, resume=False):
        if self.is_open:
            self.init_send_parameters(samples_to_send, repeats, resume=resume)
            retcode = hackrf.start_tx_mode(self.callback_send)

            if retcode == self.success:
                self.is_transmitting = True
                self._start_sendbuffer_thread()
            else:
                self.is_transmitting = False
        else:
            retcode = self.error_not_open
        self.log_retcode(retcode, "start_tx_mode")

    def stop_tx_mode(self, msg):
        self.is_transmitting = False
        try:
            self.send_buffer_reader.close()
            self.send_buffer.close()
        except AttributeError:
            logger.warning("HackRF: Could not close send buffer, because it was not open yet")

        if self.is_open:
            logger.info("stopping HackRF tx mode ({0})".format(msg))
            logger.info("closing because stop_tx_mode of HackRF is bugged and never returns")
            self.close(exit=False)

    def set_device_bandwidth(self, bw):
        if self.is_open:
            retcode = hackrf.set_baseband_filter_bandwidth(bw)
        else:
            retcode = self.error_not_open
        self.log_retcode(retcode, "set_bandwidth", bw)

    def set_device_frequency(self, value):
        if self.is_open:
            retcode = hackrf.set_freq(value)
        else:
            retcode = self.error_not_open
        self.log_retcode(retcode, "set_frequency", value)

    def set_device_gain(self, gain):
        if self.is_open:
            hackrf.set_lna_gain(gain)
            hackrf.set_vga_gain(gain)
            hackrf.set_txvga_gain(gain)

    def set_device_sample_rate(self, sample_rate):
        if self.is_open:
            retcode = hackrf.set_sample_rate(sample_rate)
        else:
            retcode = self.error_not_open

        self.log_retcode(retcode, "set_sample_rate", sample_rate)

    def reopen(self):
        if self.is_open:
            hackrf.reopen()

    def switch_from_rx2tx(self):
        # https://github.com/mossmann/hackrf/pull/246/commits/4f9665fb3b43462e39a1592fc34f3dfb50de4a07
        self.reopen()

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
        return (127.5 * ((complex_samples.view(np.float32)) - 0.5/127.5)).astype(np.int8).tostring()
