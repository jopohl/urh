import threading

import numpy as np
from abc import abstractmethod

import time

import psutil
from PyQt5.QtCore import QObject, pyqtSignal
from multiprocessing import Pipe

from multiprocessing import Value, Process

from pickle import UnpicklingError

from urh.util.Formatter import Formatter
from urh.util.Logger import logger


class Device(QObject):
    BYTES_PER_SAMPLE = None
    rcv_index_changed = pyqtSignal(int, int)

    def __init__(self, bw, freq, gain, srate, is_ringbuffer=False):
        super().__init__()

        self.error_not_open = -4242

        self.__bandwidth = bw
        self.__frequency = freq
        self.__gain = gain
        self.__sample_rate = srate

        self.bandwidth_is_adjustable = True

        self._current_sent_sample = Value("L", 0)
        self._current_sending_repeat = Value("L", 0)

        self._max_bandwidth = 1
        self._max_frequency = 1
        self._max_sample_rate = 1
        self._max_gain = 1

        self.success = 0
        self.error_codes = {}
        self.errors = set()

        self.receive_process_function = None
        self.send_process_function = None

        self.parent_data_conn, self.child_data_conn = Pipe()
        self.parent_ctrl_conn, self.child_ctrl_conn = Pipe()
        self.send_buffer = None
        self.send_buffer_reader = None

        self.samples_to_send = np.array([], dtype=np.complex64)
        self.sending_repeats = 1  # How often shall the sending sequence be repeated? 0 = forever

        self.is_ringbuffer = is_ringbuffer  # Ringbuffer for Spectrum Analyzer or Protocol Sniffing
        self.current_recv_index = 0
        self.is_receiving = False
        self.is_transmitting = False

        self.device_ip = "192.168.10.2"     # For USRP and RTLSDRTCP

        self.receive_buffer = None

        self.spectrum_x = None
        self.spectrum_y = None

    def _start_read_rcv_buffer_thread(self):
        self.read_recv_buffer_thread = threading.Thread(target=self.read_receiving_queue)
        self.read_recv_buffer_thread.daemon = True
        self.read_recv_buffer_thread.start()

    def _start_read_error_thread(self):
        self.read_dev_error_thread = threading.Thread(target=self.read_device_errors)
        self.read_dev_error_thread.daemon = True
        self.read_dev_error_thread.start()

    @property
    def current_sent_sample(self):
        return self._current_sent_sample.value // self.BYTES_PER_SAMPLE

    @current_sent_sample.setter
    def current_sent_sample(self, value: int):
        self._current_sent_sample.value = value * self.BYTES_PER_SAMPLE

    @property
    def current_sending_repeat(self):
        return self._current_sending_repeat.value

    @current_sending_repeat.setter
    def current_sending_repeat(self, value: int):
        self._current_sending_repeat.value = value

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.frequency, self.sample_rate, self.gain, self.bandwidth

    @property
    def send_process_arguments(self):
        return self.child_ctrl_conn, self.frequency, self.sample_rate, self.gain, self.bandwidth, self.send_buffer, \
               self._current_sent_sample, self._current_sending_repeat, self.sending_repeats

    def init_recv_buffer(self):
        if self.receive_buffer is None:
            if self.is_ringbuffer:
                nsamples = 10 ** 5
            else:
                # Take 60% of avail memory
                nsamples = 0.6 * (psutil.virtual_memory().free / 8)
            self.receive_buffer = np.zeros(int(nsamples), dtype=np.complex64, order='C')
            logger.info(
                "Initialized receiving buffer with size {0:.2f}MB".format(self.receive_buffer.nbytes / (1024 * 1024)))

    def log_retcode(self, retcode: int, action: str, msg=""):
        msg = str(msg)
        error_code_msg = self.error_codes[retcode] if retcode in self.error_codes else "Error Code: " + str(retcode)
        if retcode == self.success:
            if msg:
                logger.info("{0}-{1} ({2}): Success".format(type(self).__name__, action, msg))
            else:
                logger.info("{0}-{1}: Success".format(type(self).__name__, action))
        else:
            if msg:
                err = "{0}-{1} ({4}): {2} ({3})".format(type(self).__name__, action, error_code_msg, retcode, msg)
            else:
                err = "{0}-{1}: {2} ({3})".format(type(self).__name__, action, error_code_msg, retcode)
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
        return self.current_sent_sample == len(self.samples_to_send)

    @property
    def bandwidth(self):
        return self.__bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        if not self.bandwidth_is_adjustable:
            return

        if value > self._max_bandwidth:
            err = "{0} bandwidth {1}Hz too high. Correcting to {2}Hz".format(type(self).__name__,
                                                                             Formatter.big_value_with_suffix(value),
                                                                             Formatter.big_value_with_suffix(
                                                                                 self._max_bandwidth))
            self.errors.add(err)
            logger.warning(err)
            value = self._max_bandwidth

        if value != self.__bandwidth:
            self.__bandwidth = value
            self.set_device_bandwidth(value)

    def set_device_bandwidth(self, bw):
        self.parent_ctrl_conn.send("bandwidth:" + str(int(bw)))

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        if value > self._max_frequency:
            err = "{0} frequency {1}Hz too high. Correcting to {2}Hz".format(type(self).__name__,
                                                                             Formatter.big_value_with_suffix(value),
                                                                             Formatter.big_value_with_suffix(
                                                                                 self._max_frequency))
            self.errors.add(err)
            logger.warning(err)
            value = self._max_frequency

        if value != self.__frequency:
            self.__frequency = value
            self.set_device_frequency(value)

    def set_device_frequency(self, value):
        self.parent_ctrl_conn.send("center_freq:" + str(int(value)))

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
            self.set_device_gain(value)

    @abstractmethod
    def set_device_gain(self, gain):
        # todo: split to if gain etc
        self.parent_ctrl_conn.send("tuner_gain:" + str(int(gain)))
        pass

    @property
    def sample_rate(self):
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        if value > self._max_sample_rate:
            err = "{0} sample rate {1}Sps too high. Correcting to {2}Sps".format(type(self).__name__,
                                                                                 Formatter.big_value_with_suffix(value),
                                                                                 Formatter.big_value_with_suffix(
                                                                                     self._max_sample_rate))
            self.errors.add(err)
            logger.warning(err)
            value = self._max_sample_rate

        if value != self.__sample_rate:
            self.__sample_rate = value
            self.set_device_sample_rate(value)

    def set_device_sample_rate(self, sample_rate):
        self.parent_ctrl_conn.send("sample_rate:" + str(int(sample_rate)))

    def start_rx_mode(self):
        self.init_recv_buffer()

        self.is_receiving = True
        logger.info("{0}: Starting RX Mode".format(self.__class__.__name__))
        self.receive_process = Process(target=self.receive_process_function,
                                       args=self.receive_process_arguments)
        self.receive_process.daemon = True
        self._start_read_rcv_buffer_thread()
        self._start_read_error_thread()
        try:
            self.receive_process.start()
        except OSError as e:
            logger.error(repr(e))
            self.errors.add(repr(e))

    def stop_rx_mode(self, msg):
        self.is_receiving = False
        self.parent_ctrl_conn.send("stop")

        logger.info("{0}: Stopping RX Mode: {1}".format(self.__class__.__name__, msg))

        if hasattr(self, "receive_process") and self.receive_process.is_alive():
            self.receive_process.join(0.5)
            if self.receive_process.is_alive():
                logger.warning("{0}: Receive process is still alive, terminating it".format(self.__class__.__name__))
                self.receive_process.terminate()
                self.receive_process.join()
                self.child_ctrl_conn.close()
                self.child_data_conn.close()

            time.sleep(0.1)
            self.parent_data_conn, self.child_data_conn = Pipe()
            self.parent_ctrl_conn, self.child_ctrl_conn = Pipe()

    def start_tx_mode(self, samples_to_send: np.ndarray = None, repeats=None, resume=False):
        self.init_send_parameters(samples_to_send, repeats, resume=resume)
        self.is_transmitting = True

        self.transmit_process = Process(target=self.send_process_function,
                                        args=self.send_process_arguments)

        self.transmit_process.daemon = True
        self._start_read_error_thread()
        self.transmit_process.start()

    def stop_tx_mode(self, msg):
        self.is_transmitting = False
        self.parent_ctrl_conn.send("stop")

        logger.info("{0}: Stopping TX Mode: {1}".format(self.__class__.__name__, msg))

        if hasattr(self, "transmit_process") and self.transmit_process.is_alive():
            self.transmit_process.join(0.5)
            if self.transmit_process.is_alive():
                logger.warning("{0}: Transmit process is still alive, terminating it".format(self.__class__.__name__))
                self.transmit_process.terminate()
                self.transmit_process.join()
            self.parent_ctrl_conn, self.child_ctrl_conn = Pipe()

    @staticmethod
    def unpack_complex(buffer, nvalues):
        pass

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        pass

    def set_device_parameters(self):
        self.set_device_bandwidth(self.bandwidth)
        self.set_device_frequency(self.frequency)
        self.set_device_gain(self.gain)
        self.set_device_sample_rate(self.sample_rate)

    def read_device_errors(self):
        while self.is_receiving or self.is_transmitting:
            try:
                error = self.parent_ctrl_conn.recv()
                action, error_code = error.split(":")
                self.log_retcode(int(error_code), action)
            except (EOFError, UnpicklingError, ConnectionResetError):
                break
        self.is_transmitting = False
        self.is_receiving = False
        logger.debug("Exiting read device errors thread")

    def read_receiving_queue(self):
        while self.is_receiving:
            try:
                byte_buffer = self.parent_data_conn.recv_bytes()

                nsamples = len(byte_buffer) // self.BYTES_PER_SAMPLE
                if nsamples > 0:
                    if self.current_recv_index + nsamples >= len(self.receive_buffer):
                        if self.is_ringbuffer:
                            self.current_recv_index = 0
                            if nsamples >= len(self.receive_buffer):
                                logger.warning("Receive buffer too small, skipping {0:d} samples".format(
                                    nsamples - len(self.receive_buffer)))
                                nsamples = len(self.receive_buffer) - 1

                        else:
                            self.stop_rx_mode(
                                "Receiving buffer is full {0}/{1}".format(self.current_recv_index + nsamples,
                                                                          len(self.receive_buffer)))
                            return

                    end = nsamples * self.BYTES_PER_SAMPLE
                    self.receive_buffer[self.current_recv_index:self.current_recv_index + nsamples] = \
                        self.unpack_complex(byte_buffer[:end], nsamples)

                    old_index = self.current_recv_index
                    self.current_recv_index += nsamples

                    self.rcv_index_changed.emit(old_index, self.current_recv_index)
            except BrokenPipeError:
                pass
            except EOFError:
                logger.info("EOF Error: Ending receive thread")
                break

            time.sleep(0.01)

        logger.debug("Exiting read_receive_queue thread.")

    def init_send_parameters(self, samples_to_send: np.ndarray = None, repeats: int = None,
                             skip_device_parameters=False, resume=False):
        if not skip_device_parameters:
            self.set_device_parameters()

        if samples_to_send is not None:
            self.samples_to_send = samples_to_send
            self.send_buffer = None

        if self.send_buffer is None:
            self.send_buffer = self.pack_complex(self.samples_to_send)
        elif not resume:
            self.current_sending_repeat = 0

        if repeats is not None:
            self.sending_repeats = repeats
