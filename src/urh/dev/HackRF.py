from urh.dev.Device import Device
from urh.cythonext import hackrf
import numpy as np
from urh.util.Logger import logger

class HackRF(Device):
    BYTES_PER_COMPLEX_NUMBER = 2

    def __init__(self, bw, freq, gain, srate, initial_bufsize=8e9, is_ringbuffer=False):
        super().__init__(bw, freq, gain, srate, initial_bufsize, is_ringbuffer)
        self.is_open = False
        self.success = 0

    def open(self):
        if not self.is_open:
            if hackrf.setup() == self.success:
                self.is_open = True
                logger.info("successfully opened HackRF")
                self.set_device_parameters()

    def close(self):
        if self.is_open:
            if hackrf.exit() == self.success:
                logger.info("successfully closed HackRF")
                self.is_open = False

    def start_rx_mode(self):
        if hackrf.start_rx_mode(self.callback_recv) == self.success:
            logger.info("successfully started HackRF rx mode")
        else:
            logger.error("could not start HackRF rx mode")

    def stop_rx_mode(self, msg):
        if hackrf.stop_rx_mode() == self.success:
            logger.info("stopped HackRF rx mode (" + str(msg) + ")")
        else:
            logger.error("could not stop HackRF rx mode")

    def set_device_bandwidth(self, bw):
        if self.is_open:

            if hackrf.set_baseband_filter_bandwidth(bw) == self.success:
                logger.info("successfully set HackRF bandwidth to {0}".format(bw))
            else:
                logger.error("failed to set HackRF bandwidth to {0}".format(bw))

    def set_device_frequency(self, value):
        if self.is_open:
            if hackrf.set_freq(value) == self.success:
                logger.info("successfully set HackRF frequency to {0}".format(value))
            else:
                logger.error("failed to set HackRF frequency to {0}".format(value))

    def set_device_gain(self, gain):
        if self.is_open:
            hackrf.set_lna_gain(gain)
            hackrf.set_vga_gain(gain)
            hackrf.set_txvga_gain(gain)

    def set_device_sample_rate(self, sample_rate):
        if self.is_open:
            if hackrf.set_sample_rate(sample_rate) == self.success:
                logger.info("successfully set HackRF sample rate to {0}".format(sample_rate))
            else:
                logger.error("failed to set HackRF sample rate to {0}".format(sample_rate))


    def unpack_complex(self, nvalues: int):
        result = np.empty(nvalues, dtype=np.complex64)
        buffer = self.byte_buffer[:nvalues * self.BYTES_PER_COMPLEX_NUMBER]
        unpacked = np.frombuffer(buffer, dtype=[('r', np.uint8), ('i', np.uint8)])
        result.real = unpacked['r'] / 128.0
        result.imag = unpacked['i'] / 128.0
        return result
