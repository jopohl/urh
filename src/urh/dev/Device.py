import threading
from multiprocessing import Queue

import numpy as np
from abc import ABCMeta, abstractmethod

import time


class Device(metaclass=ABCMeta):
    BYTES_PER_SAMPLE = None

    def __init__(self, bw, freq, gain, srate, initial_bufsize=8e9, is_ringbuffer=False):
        self.lock = threading.Lock()
        self.byte_buffer = b''

        self.__bandwidth = bw
        self.__frequency = freq
        self.__gain = gain
        self.__sample_rate = srate

        self.queue = Queue()

        buf_size = initial_bufsize
        self.is_ringbuffer = is_ringbuffer  # Ringbuffer for Live Sniffing
        self.current_index = 0
        self.is_receiving = False
        self.is_transmitting = False

        self.read_queue_thread = threading.Thread(target=self.read_queue)
        self.read_queue_thread.daemon = True

        while True:
            try:
                self.receive_buffer = np.zeros(int(buf_size), dtype=np.complex64, order='C')
                break
            except (MemoryError, ValueError):
                buf_size //= 2

    @property
    def received_data(self):
        return self.receive_buffer[:self.current_index]

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
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        if value != self.__sample_rate:
            self.__sample_rate = value
            self.set_device_sample_rate(value)

    @abstractmethod
    def set_device_sample_rate(self, sample_rate):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def start_rx_mode(self):
        pass

    @abstractmethod
    def stop_rx_mode(self, msg):
        pass

    @abstractmethod
    def start_tx_mode(self):
        pass

    @abstractmethod
    def stop_tx_mode(self, msg):
        pass

    @abstractmethod
    def unpack_complex(self, buffer, nvalues):
        pass

    @abstractmethod
    def pack_complex(self, complex_samples: np.ndarray):
        pass

    def set_device_parameters(self):
        self.set_device_bandwidth(self.bandwidth)
        self.set_device_frequency(self.frequency)
        self.set_device_gain(self.gain)
        self.set_device_sample_rate(self.sample_rate)

    def read_queue(self):
        while self.is_receiving:
            while not self.queue.empty():
                self.byte_buffer += self.queue.get()
                nsamples = len(self.byte_buffer) // self.BYTES_PER_SAMPLE
                if nsamples > 0:
                    if self.current_index + nsamples >= len(self.receive_buffer):
                        if self.is_ringbuffer:
                            self.current_index = 0
                            if nsamples >= len(self.receive_buffer):
                                self.stop_rx_mode("Receiving buffer too small.")
                        else:
                            self.stop_rx_mode("Receiving Buffer is full.")
                            return

                    end = nsamples*self.BYTES_PER_SAMPLE
                    self.receive_buffer[self.current_index:self.current_index + nsamples] = \
                        self.unpack_complex(self.byte_buffer[:end], nsamples)
                    self.current_index += nsamples
                    self.byte_buffer = self.byte_buffer[end:]
            time.sleep(0.01)

    def callback_recv(self, buffer):
        self.queue.put(buffer)
        return 0

    def callback_send(self):
        pass