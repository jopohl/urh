import threading
import numpy as np
from abc import ABCMeta, abstractmethod
class Device(metaclass=ABCMeta):
    def __init__(self, bw, freq, gain, srate, initial_bufsize=8e9, is_ringbuffer=False):
        self.lock = threading.Lock()
        self.byte_buffer = b''

        self.__bandwidth = bw
        self.__frequency = freq
        self.__gain = gain
        self.__sample_rate = srate

        buf_size = initial_bufsize
        self.is_ringbuffer = is_ringbuffer  # Ringbuffer for Live Sniffing
        self.current_index = 0
        while True:
            try:
                self.data = np.zeros(buf_size, dtype=np.complex64)
                break
            except (MemoryError, ValueError):
                buf_size //= 2



    @property
    def bandwidth(self):
        return self.__bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        if value != self.__bandwidth:
            self.__bandwidth = value
            self.set_device_bandwidth(value)

    @abstractmethod
    def set_device_bandwidth(self, bandwidth):
        pass

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        if value != self.__frequency:
            self.__frequency = value
            self.set_device_frequency(value)

    @abstractmethod
    def set_device_frequency(self, frequency):
        pass

    @property
    def gain(self):
        return self.__gain

    @gain.setter
    def gain(self, value):
        if value != self.__gain:
            self.__gain = value
            self.set_device_gain(value)

    @abstractmethod
    def set_device_gain(self, gain):
        pass

    @property
    def sample_rate(self):
        return self.sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        if value != self.__sample_rate:
            self.__sample_rate = value
            self.set_device_sample_rate(value)

    @abstractmethod
    def set_device_sample_rate(self, sample_rate):
        pass

    def callback_recv(self, buffer):
        with self.lock:
            self.byte_buffer += buffer

            r = np.empty(len(self.byte_buffer) // 4, dtype=np.float16)
            i = np.empty(len(self.byte_buffer) // 4, dtype=np.float16)
            c = np.empty(len(self.byte_buffer) // 4, dtype=np.complex64)
            if self.current_index + len(c) >= len(self.data):
                if self.is_ringbuffer:
                    self.current_index = 0
                    if len(c) >= len(self.data):
                        self.stop("Receiving buffer too small.")
                else:
                    self.stop("Receiving Buffer is full.")
                    return

            for j in range(0, len(self.byte_buffer), 4):
                r[j // 4] = np.frombuffer(self.byte_buffer[j:j + 2], dtype=np.float16) / 32767.5
                i[j // 4] = np.frombuffer(self.byte_buffer[j + 2:j + 4], dtype=np.float16) / 32767.5
            # r2 = np.fromstring(buffer[], dtype=np.float16) / 32767.5
            c.real = r
            c.imag = i
            self.data[self.current_index:self.current_index + len(c)] = c
            self.current_index += len(c)
            l = 4*(len(self.byte_buffer)//4)
            self.byte_buffer = self.byte_buffer[l:l+len(self.byte_buffer)%4]

        return 0