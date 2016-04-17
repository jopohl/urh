from urh.dev.Device import Device
from urh.cythonext import hackrf
import numpy as np

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
                self.set_device_parameters()

    def close(self):
        if self.is_open:
            if hackrf.exit() == self.success:
               self.is_open = False

    def start_rx_mode(self):
        hackrf.start_rx_mode(self.callback_recv)

    def stop_rx_mode(self, msg):
        print("Stopping Rx-Mode: ", msg)
        hackrf.stop_rx_mode()

    def set_device_bandwidth(self, bw):
        if self.is_open:
            hackrf.set_baseband_filter_bandwidth(bw)

    def set_device_frequency(self, value):
        if self.is_open:
            hackrf.set_freq(value)

    def set_device_gain(self, gain):
        if self.is_open:
            hackrf.set_lna_gain(gain)
            hackrf.set_vga_gain(gain)
            hackrf.set_txvga_gain(gain)

    def set_device_sample_rate(self, sample_rate):
        if self.is_open:
            hackrf.set_sample_rate(sample_rate)

    def unpack_complex(self, buffer):
        result = np.empty(len(buffer) // self.BYTES_PER_COMPLEX_NUMBER, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.int8), ('i', np.int8)])
        result.real = unpacked['r'] / 128.0
        result.imag = unpacked['i'] / 128.0
        return result