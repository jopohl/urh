import numpy as np
import time

from urh.dev.native.Device import Device
from urh.dev.native.lib import hackrf
from urh.util.Logger import logger


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

    def reopen(self):
        if self.is_open:
            hackrf.reopen()

    def open(self, init=True):
        if not self.is_open:
            if init:
                ret = hackrf.setup()
            else:
                ret = hackrf.open()

            self.is_open = ret == self.success
            self.log_retcode(ret, "open")

    def close(self, exit=True):
        if self.is_open:
            logger.info("HackRF: Attempting to close...")
            time.sleep(0.01)
            ret = hackrf.close()
            self.is_open = ret != self.success

            if self.is_open:
                logger.error("Failed to close HackRF")
            else:
                logger.info("Successfully closed HackRF")

            self.log_retcode(ret, "close")
            if exit:
                self.exit()

    def exit(self):
        return hackrf.exit()

    def start_rx_mode(self):
        if self.is_open:
            self.init_recv_buffer()
            self.set_device_parameters()
            ret = hackrf.start_rx_mode(self.callback_recv)
            self.is_receiving = ret == self.success

            if self.is_receiving:
                logger.info("HackRF: Starting receiving thread")
                self._start_readqueue_thread()

            self.log_retcode(ret, "start_rx_mode")
        else:
            self.log_retcode(self.error_not_open, "start_rx_mode")

    def stop_rx_mode(self, msg):
        self.is_receiving = False

        logger.info("HackRF: Stopping RX Mode: " + msg)

        if hasattr(self, "read_queue_thread") and self.read_queue_thread.is_alive():
            try:
                self.read_queue_thread.join(0.001)
                logger.info("HackRF: Joined read_queue_thread")
            except RuntimeError:
                logger.error("HackRF: Could not join read_queue_thread")

        if self.is_open:
            logger.info("stopping HackRF rx mode ({0})".format(msg))
            logger.warning(
                "closing because stop_rx_mode of HackRF is bugged and will not allow re receive without close")
            self.close(exit=False)

    def switch_from_rx2tx(self):
        # https://github.com/mossmann/hackrf/pull/246/commits/4f9665fb3b43462e39a1592fc34f3dfb50de4a07
        self.reopen()

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
