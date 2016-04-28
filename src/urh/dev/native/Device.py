import io
import threading
from multiprocessing import Queue

import numpy as np
from abc import abstractmethod

import time

from PyQt5.QtCore import QObject, pyqtSignal

from urh.util.Formatter import Formatter
from urh.util.Logger import logger

class Device(QObject):
    BYTES_PER_SAMPLE = None
    rcv_index_changed = pyqtSignal(int, int)

    def __init__(self, bw, freq, gain, srate, bufsize=8e9, is_ringbuffer=False):
        super().__init__()

        self.__bandwidth = bw
        self.__frequency = freq
        self.__gain = gain
        self.__sample_rate = srate

        self.is_open = False

        self._max_bandwidth = 1
        self._max_frequency = 1
        self._max_sample_rate = 1
        self._max_gain = 1

        self.success = 0
        self.error_codes = {}
        self.errors = set()

        self.queue = Queue()
        self.send_buffer = None
        self.send_buffer_reader = None

        self.samples_to_send = np.array([], dtype=np.complex64)
        self.sending_repeats = 1 # How often shall the sending sequence be repeated? -1 = forever
        self.current_sending_repeat = 0

        self.is_ringbuffer = is_ringbuffer  # Ringbuffer for Spectrum Analyzer or Protocol Sniffing
        self.current_recv_index = 0
        self.current_sent_sample = 0
        self.is_receiving = False
        self.is_transmitting = False

        self.device_ip = "192.168.10.2" # For USRP

        self.receive_buffer = None
        self.receive_buffer_size = bufsize


        self.spectrum_x = None
        self.spectrum_y = None

    def _start_sendbuffer_thread(self):
        self.sendbuffer_thread = threading.Thread(target=self.check_send_buffer)
        self.sendbuffer_thread.daemon = True
        self.sendbuffer_thread.start()

    def _start_readqueue_thread(self):
        self.read_queue_thread = threading.Thread(target=self.read_receiving_queue)
        self.read_queue_thread.daemon = True
        self.read_queue_thread.start()

    def init_recv_buffer(self):
        if self.receive_buffer is None:
            while True:
                try:
                    self.receive_buffer = np.zeros(int(self.receive_buffer_size), dtype=np.complex64, order='C')
                    break
                except (OSError, MemoryError, ValueError):
                    self.receive_buffer_size //= 2
        logger.info("Initialized receiving buffer with size {0:.2f}MB".format(self.receive_buffer_size/(1024*1024)))

    def log_retcode(self, retcode: int, action: str, msg=""):
        msg = str(msg)
        if retcode == self.success:
            if msg:
                logger.info("{0}-{1} ({2}): Success".format(type(self).__name__, action, msg))
            else:
                logger.info("{0}-{1}: Success".format(type(self).__name__, action))
        else:
            if msg:
                err = "{0}-{1} ({4}): {2} ({3})".format(type(self).__name__, action, self.error_codes[retcode], retcode, msg)
            else:
                err = "{0}-{1}: {2} ({3})".format(type(self).__name__, action, self.error_codes[retcode], retcode)
            self.errors.add(err)
            logger.error(err)


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
        if value > self._max_bandwidth:
            err = "{0} bandwidth {1}Hz too high. Correcting to {2}Hz".format(type(self).__name__,
                                                                         Formatter.big_value_with_suffix(value),
                                                                         Formatter.big_value_with_suffix(self._max_bandwidth))
            self.errors.add(err)
            logger.warning(err)
            value = self._max_bandwidth

        if value != self.__bandwidth:
            self.__bandwidth = value
            if self.is_open:
                self.set_device_bandwidth(value)

    @abstractmethod
    def set_device_bandwidth(self, bandwidth):
        pass

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        if value > self._max_frequency:
            err = "{0} frequency {1}Hz too high. Correcting to {2}Hz".format(type(self).__name__,
                                                                             Formatter.big_value_with_suffix(value),
                                                                             Formatter.big_value_with_suffix(self._max_frequency))
            self.errors.add(err)
            logger.warning(err)
            value = self._max_frequency

        if value != self.__frequency:
            self.__frequency = value
            if self.is_open:
                self.set_device_frequency(value)

    @abstractmethod
    def set_device_frequency(self, frequency):
        pass

    @property
    def gain(self):
        return self.__gain

    @gain.setter
    def gain(self, value):
        if value > self._max_gain:
            err = "{0} gain {1} too high. Correcting to {2}".format(type(self).__name__, value, self._max_gain)
            self.errors.add(err)
            logger.warning(err)
            value = self._max_gain

        if value != self.__gain:
            self.__gain = value
            if self.is_open:
                self.set_device_gain(value)

    @abstractmethod
    def set_device_gain(self, gain):
        pass

    @property
    def sample_rate(self):
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        if value > self._max_sample_rate:
            err = "{0} sample rate {1}Sps too high. Correcting to {2}Sps".format(type(self).__name__,
                                                                                 Formatter.big_value_with_suffix(value),
                                                                                 Formatter.big_value_with_suffix(self._max_sample_rate))
            self.errors.add(err)
            logger.warning(err)
            value = self._max_sample_rate

        if value != self.__sample_rate:
            self.__sample_rate = value
            if self.is_open:
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
    def start_tx_mode(self, samples_to_send: np.ndarray = None, repeats=None):
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
                byte_buffer = self.queue.get()
                old_index = self.current_recv_index

                nsamples = len(byte_buffer) // self.BYTES_PER_SAMPLE
                if nsamples > 0:
                    if self.current_recv_index + nsamples >= len(self.receive_buffer):
                        if self.is_ringbuffer:
                            self.current_recv_index = 0
                            if nsamples >= len(self.receive_buffer):
                               # logger.warning("Receive buffer too small, skipping {0:d} samples".format(nsamples-len(self.receive_buffer)))
                                nsamples = len(self.receive_buffer) - 1

                        else:
                            self.stop_rx_mode("Receiving Buffer is full.")
                            return

                    end = nsamples*self.BYTES_PER_SAMPLE
                    self.receive_buffer[self.current_recv_index:self.current_recv_index + nsamples] = \
                        self.unpack_complex(byte_buffer[:end], nsamples)
                    self.current_recv_index += nsamples

                    self.rcv_index_changed.emit(old_index, self.current_recv_index)

            time.sleep(0.01)

    def init_send_parameters(self, samples_to_send: np.ndarray = None, repeats: int = None, skip_device_parameters=False):
        if not skip_device_parameters:
            self.set_device_parameters()

        if samples_to_send is not None:
            try:
                self.send_buffer_reader.close()
                self.send_buffer.close()
            except AttributeError:
                pass

            self.samples_to_send = samples_to_send

        if self.send_buffer is None or self.send_buffer.closed:
            self.send_buffer = io.BytesIO(self.pack_complex(self.samples_to_send))
            self.send_buffer_reader = io.BufferedReader(self.send_buffer)
        else:
            self.reset_send_buffer()

        if repeats is not None:
            self.sending_repeats = repeats

        self.current_sending_repeat = 0
        self.current_sent_sample = 0

    def reset_send_buffer(self):
        self.current_sent_sample = 0
        self.send_buffer_reader.seek(0)

    def check_send_buffer(self):
         # sendning_repeats -1 = forever
        assert len(self.samples_to_send) == len(self.send_buffer_reader.read()) // self.BYTES_PER_SAMPLE
        self.send_buffer.seek(0)
        while (self.current_sending_repeat < self.sending_repeats or self.sending_repeats == -1) and self.is_transmitting:
                self.reset_send_buffer()
                while self.is_transmitting and self.send_buffer_reader.peek():
                    try:
                        self.current_sent_sample = self.send_buffer_reader.tell() // self.BYTES_PER_SAMPLE
                    except ValueError:
                        # I/O operation on closed file. --> Buffer was closed
                        break
                    time.sleep(0.01)

                self.current_sent_sample = self.send_buffer_reader.tell() // self.BYTES_PER_SAMPLE
                self.current_sending_repeat += 1

        if self.current_sent_sample >= len(self.samples_to_send) - 1:
            self.current_sent_sample = len(self.samples_to_send)  # Mark transmission as finished
        else:
            logger.warning("Skipped {0:d} samples in sending".format(len(self.samples_to_send) - self.current_sent_sample))
            self.current_sent_sample = len(self.samples_to_send)


    def callback_recv(self, buffer):
        self.queue.put(buffer)
        return 0

    def callback_send(self, buffer_length):
        return self.send_buffer_reader.read(buffer_length)