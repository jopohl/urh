import io
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
        self.send_buffer = None
        self.send_buffer_reader = None

        self.samples_to_send = np.array([], dtype=np.complex64)
        self.sending_repeats = 1 # How often shall the sending sequence be repeated? -1 = forever
        self.current_sending_repeat = 0

        buf_size = initial_bufsize
        self.is_ringbuffer = is_ringbuffer  # Ringbuffer for Live Sniffing
        self.current_recv_index = 0
        self.current_sent_sample = 0
        self.is_receiving = False
        self.is_transmitting = False

        self.read_queue_thread = threading.Thread(target=self.read_receiving_queue)
        self.read_queue_thread.daemon = True

        self.sendbuffer_thread = threading.Thread(target=self.check_send_buffer)
        self.sendbuffer_thread.daemon = True

        while True:
            try:
                self.receive_buffer = np.zeros(int(buf_size), dtype=np.complex64, order='C')
                break
            except (MemoryError, ValueError):
                buf_size //= 2

    @property
    def received_data(self):
        return self.receive_buffer[:self.current_recv_index]

    @property
    def sent_data(self):
        return self.samples_to_send[:self.current_sent_sample]

    @property
    def sending_finished(self):
        # current_sent_sample is only set in method check_send_buffer
        return self.current_sent_sample == len(self.samples_to_send)

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
    def start_tx_mode(self, samples_to_send: np.ndarray, repeats=1):
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

    def read_receiving_queue(self):
        while self.is_receiving:
            while not self.queue.empty():
                self.byte_buffer += self.queue.get()
                nsamples = len(self.byte_buffer) // self.BYTES_PER_SAMPLE
                if nsamples > 0:
                    if self.current_recv_index + nsamples >= len(self.receive_buffer):
                        if self.is_ringbuffer:
                            self.current_recv_index = 0
                            if nsamples >= len(self.receive_buffer):
                                self.stop_rx_mode("Receiving buffer too small.")
                        else:
                            self.stop_rx_mode("Receiving Buffer is full.")
                            return

                    end = nsamples*self.BYTES_PER_SAMPLE
                    self.receive_buffer[self.current_recv_index:self.current_recv_index + nsamples] = \
                        self.unpack_complex(self.byte_buffer[:end], nsamples)
                    self.current_recv_index += nsamples
                    self.byte_buffer = self.byte_buffer[end:]
            time.sleep(0.01)

    def init_send_parameters(self, samples_to_send: np.ndarray, repeats: int):
        self.samples_to_send = samples_to_send
        self.set_device_parameters()
        self.sending_repeats = repeats
        self.current_sending_repeat = 0
        self.current_sent_sample = 0

        self.send_buffer = io.BytesIO(self.pack_complex(self.samples_to_send))
        self.send_buffer_reader = io.BufferedReader(self.send_buffer)

    def reset_send_buffer(self):
        self.current_sent_sample = 0
        self.send_buffer_reader.seek(0)

    def check_send_buffer(self):
        while self.current_sending_repeat < self.sending_repeats or self.sending_repeats == -1: # -1 = forever
            self.reset_send_buffer()

            while self.is_transmitting and self.send_buffer_reader.peek():
                time.sleep(0.1)
                self.current_sent_sample = self.send_buffer_reader.tell() // self.BYTES_PER_SAMPLE
                continue # Still data in send buffer

            self.current_sending_repeat += 1

        if self.current_sent_sample >= len(self.samples_to_send) - 1: # Mark transmission as finished
            self.current_sent_sample = len(self.samples_to_send)


    def callback_recv(self, buffer):
        self.queue.put(buffer)
        return 0

    def callback_send(self, buffer_length):
        return self.send_buffer_reader.read(buffer_length)