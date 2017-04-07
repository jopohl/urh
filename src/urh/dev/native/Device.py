import threading
import time
from multiprocessing import Pipe
from multiprocessing import Value, Process
from pickle import UnpicklingError
from enum import Enum

import numpy as np
import psutil
from PyQt5.QtCore import QObject, pyqtSignal

from urh import constants
from urh.util.Logger import logger


class Device(QObject):
    class Command(Enum):
        STOP = 0
        SET_FREQUENCY = 1
        SET_SAMPLE_RATE = 2
        SET_BANDWIDTH = 3
        SET_RF_GAIN = 4
        SET_IF_GAIN = 5
        SET_BB_GAIN = 6
        SET_DIRECT_SAMPLING_MODE = 7
        SET_FREQUENCY_CORRECTION = 8

    BYTES_PER_SAMPLE = None
    rcv_index_changed = pyqtSignal(int, int)

    DEVICE_LIB = None
    DEVICE_METHODS = {
        Command.SET_FREQUENCY: "set_freq",
        Command.SET_SAMPLE_RATE: "set_sample_rate",
        Command.SET_BANDWIDTH: "set_bandwidth",
        Command.SET_RF_GAIN: "set_rf_gain",
        Command.SET_IF_GAIN: {"rx": "set_if_rx_gain", "tx": "set_if_tx_gain"},
        Command.SET_BB_GAIN: {"rx": "set_baseband_gain"}
    }

    @classmethod
    def process_command(cls, command, ctrl_connection, is_tx: bool):
        is_rx = not is_tx
        if command == cls.Command.STOP:
            return cls.Command.STOP

        tag, value = command

        try:
            if isinstance(cls.DEVICE_METHODS[tag], str):
                method_name = cls.DEVICE_METHODS[tag]
            elif isinstance(cls.DEVICE_METHODS[tag], dict):
                method_name = cls.DEVICE_METHODS[tag]["rx" if is_rx else "tx"]
            else:
                method_name = None
        except KeyError:
            method_name = None

        if method_name:
            ret = getattr(cls.DEVICE_LIB, method_name)(value)
            ctrl_connection.send("{0} to {1}:{2}".format(tag.name, value, ret))

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1, is_ringbuffer=False):
        super().__init__()

        self.error_not_open = -4242

        self.__bandwidth = bandwidth
        self.__frequency = center_freq
        self.__gain = gain  # = rf_gain
        self.__if_gain = if_gain
        self.__baseband_gain = baseband_gain
        self.__sample_rate = sample_rate

        self.__freq_correction = 0
        self.__direct_sampling_mode = 0

        self.bandwidth_is_adjustable = True

        self._current_sent_sample = Value("L", 0)
        self._current_sending_repeat = Value("L", 0)

        self.success = 0
        self.error_codes = {}
        self.device_messages = []

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

        self.device_ip = "192.168.10.2"  # For USRP and RTLSDRTCP

        self.receive_buffer = None

        self.spectrum_x = None
        self.spectrum_y = None

    def _start_read_rcv_buffer_thread(self):
        self.read_recv_buffer_thread = threading.Thread(target=self.read_receiving_queue)
        self.read_recv_buffer_thread.daemon = True
        self.read_recv_buffer_thread.start()

    def _start_read_message_thread(self):
        self.read_dev_msg_thread = threading.Thread(target=self.read_device_messages)
        self.read_dev_msg_thread.daemon = True
        self.read_dev_msg_thread.start()

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
        return self.child_data_conn, self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, self.gain, self.if_gain, self.baseband_gain

    @property
    def send_process_arguments(self):
        return self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, \
               self.gain, self.if_gain, self.baseband_gain, self.send_buffer, \
               self._current_sent_sample, self._current_sending_repeat, self.sending_repeats

    def init_recv_buffer(self):
        if self.receive_buffer is None:
            if self.is_ringbuffer:
                num_samples = constants.SPECTRUM_BUFFER_SIZE
            else:
                # Take 60% of avail memory
                threshold = constants.SETTINGS.value('ram_threshold', 0.6, float)
                num_samples = threshold * (psutil.virtual_memory().available / 8)
            self.receive_buffer = np.zeros(int(num_samples), dtype=np.complex64, order='C')
            logger.info(
                "Initialized receiving buffer with size {0:.2f}MB".format(self.receive_buffer.nbytes / (1024 * 1024)))

    def log_retcode(self, retcode: int, action: str, msg=""):
        msg = str(msg)
        error_code_msg = self.error_codes[retcode] if retcode in self.error_codes else "Error Code: " + str(retcode)

        if retcode == self.success:
            if msg:
                formatted_message = "{0}-{1} ({2}): Success".format(type(self).__name__, action, msg)
            else:
                formatted_message = "{0}-{1}: Success".format(type(self).__name__, action)
            logger.info(formatted_message)
        else:
            if msg:
                formatted_message = "{0}-{1} ({4}): {2} ({3})".format(type(self).__name__, action, error_code_msg, retcode, msg)
            else:
                formatted_message = "{0}-{1}: {2} ({3})".format(type(self).__name__, action, error_code_msg, retcode)
            logger.error(formatted_message)

        self.device_messages.append(formatted_message)

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

        if value != self.__bandwidth:
            self.__bandwidth = value
            self.set_device_bandwidth(value)

    def set_device_bandwidth(self, bw):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_BANDWIDTH, int(bw)))
        except BrokenPipeError:
            pass

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        if value != self.__frequency:
            self.__frequency = value
            self.set_device_frequency(value)

    def set_device_frequency(self, value):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_FREQUENCY, int(value)))
        except BrokenPipeError:
            pass

    @property
    def gain(self):
        return self.__gain

    @gain.setter
    def gain(self, value):
        if value != self.__gain:
            self.__gain = value
            self.set_device_gain(value)

    def set_device_gain(self, gain):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_RF_GAIN, int(gain)))
        except BrokenPipeError:
            pass

    @property
    def if_gain(self):
        return self.__if_gain

    @if_gain.setter
    def if_gain(self, value):
        if value != self.__if_gain:
            self.__if_gain = value
            self.set_device_if_gain(value)

    def set_device_if_gain(self, if_gain):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_IF_GAIN, int(if_gain)))
        except BrokenPipeError:
            pass

    @property
    def baseband_gain(self):
        return self.__baseband_gain

    @baseband_gain.setter
    def baseband_gain(self, value):
        if value != self.__baseband_gain:
            self.__baseband_gain = value
            self.set_device_baseband_gain(value)

    def set_device_baseband_gain(self, baseband_gain):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_BB_GAIN, int(baseband_gain)))
        except BrokenPipeError:
            pass

    @property
    def sample_rate(self):
        return self.__sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        if value != self.__sample_rate:
            self.__sample_rate = value
            self.set_device_sample_rate(value)

    def set_device_sample_rate(self, sample_rate):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_SAMPLE_RATE, int(sample_rate)))
        except BrokenPipeError:
            pass

    @property
    def freq_correction(self):
        return self.__freq_correction

    @freq_correction.setter
    def freq_correction(self, value):
        if value != self.__freq_correction:
            self.__freq_correction = value
            self.set_device_freq_correction(value)

    def set_device_freq_correction(self, value):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_FREQUENCY_CORRECTION, int(value)))
        except BrokenPipeError:
            pass

    @property
    def direct_sampling_mode(self):
        return self.__direct_sampling_mode

    @direct_sampling_mode.setter
    def direct_sampling_mode(self, value):
        if value != self.__direct_sampling_mode:
            self.__direct_sampling_mode = value
            self.set_device_direct_sampling_mode(value)

    def set_device_direct_sampling_mode(self, value):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_DIRECT_SAMPLING_MODE, int(value)))
        except BrokenPipeError:
            pass

    def start_rx_mode(self):
        self.init_recv_buffer()
        self.parent_data_conn, self.child_data_conn = Pipe()
        self.parent_ctrl_conn, self.child_ctrl_conn = Pipe()

        self.is_receiving = True
        logger.info("{0}: Starting RX Mode".format(self.__class__.__name__))
        self.receive_process = Process(target=self.receive_process_function,
                                       args=self.receive_process_arguments)
        self.receive_process.daemon = True
        self._start_read_rcv_buffer_thread()
        self._start_read_message_thread()
        try:
            self.receive_process.start()
        except OSError as e:
            logger.error(repr(e))
            self.device_messages.add(repr(e))

    def stop_rx_mode(self, msg):
        self.is_receiving = False
        try:
            self.parent_ctrl_conn.send(self.Command.STOP)
        except BrokenPipeError:
            pass

        logger.info("{0}: Stopping RX Mode: {1}".format(self.__class__.__name__, msg))

        if hasattr(self, "receive_process") and self.receive_process.is_alive():
            self.receive_process.join(0.5)
            if self.receive_process.is_alive():
                logger.warning("{0}: Receive process is still alive, terminating it".format(self.__class__.__name__))
                self.receive_process.terminate()
                self.receive_process.join()
                self.child_ctrl_conn.close()
                self.child_data_conn.close()

    def start_tx_mode(self, samples_to_send: np.ndarray = None, repeats=None, resume=False):
        self.parent_ctrl_conn, self.child_ctrl_conn = Pipe()
        self.init_send_parameters(samples_to_send, repeats, resume=resume)
        self.is_transmitting = True

        logger.info("{0}: Starting TX Mode".format(self.__class__.__name__))

        self.transmit_process = Process(target=self.send_process_function,
                                        args=self.send_process_arguments)

        self.transmit_process.daemon = True
        self._start_read_message_thread()
        self.transmit_process.start()

    def stop_tx_mode(self, msg):
        self.is_transmitting = False
        try:
            self.parent_ctrl_conn.send(self.Command.STOP)
        except BrokenPipeError:
            pass

        logger.info("{0}: Stopping TX Mode: {1}".format(self.__class__.__name__, msg))

        if hasattr(self, "transmit_process") and self.transmit_process.is_alive():
            self.transmit_process.join(0.5)
            if self.transmit_process.is_alive():
                logger.warning("{0}: Transmit process is still alive, terminating it".format(self.__class__.__name__))
                self.transmit_process.terminate()
                self.transmit_process.join()
                self.child_ctrl_conn.close()

    @staticmethod
    def unpack_complex(buffer, nvalues):
        pass

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        pass

    def read_device_messages(self):
        while self.is_receiving or self.is_transmitting:
            try:
                message = self.parent_ctrl_conn.recv()
                action, return_code = message.split(":")
                self.log_retcode(int(return_code), action)
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
                                #logger.warning("Receive buffer too small, skipping {0:d} samples".format(nsamples - len(self.receive_buffer)))
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

    def init_send_parameters(self, samples_to_send: np.ndarray = None, repeats: int = None, resume=False):
        if samples_to_send is not None:
            self.samples_to_send = samples_to_send
            self.send_buffer = None

        if self.send_buffer is None:
            self.send_buffer = self.pack_complex(self.samples_to_send)
        elif not resume:
            self.current_sending_repeat = 0

        if repeats is not None:
            self.sending_repeats = repeats
