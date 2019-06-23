import os
import time
from datetime import datetime
from threading import Thread

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from urh.cythonext.signal_functions import grab_pulse_lens

from urh.ainterpretation import AutoInterpretation
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.util.Logger import logger


class ProtocolSniffer(ProtocolAnalyzer, QObject):
    """
    This class is used for live sniffing a protocol
    with certain signal parameters.
    """
    started = pyqtSignal()
    stopped = pyqtSignal()
    message_sniffed = pyqtSignal(int)

    BUFFER_SIZE_MB = 100

    def __init__(self, samples_per_symbol: int, center: float, center_spacing: float,
                 noise: float, tolerance: int, modulation_type: str, bits_per_symbol: int,
                 device: str, backend_handler: BackendHandler, network_raw_mode=False):
        signal = Signal("", "LiveSignal")
        signal.samples_per_symbol = samples_per_symbol
        signal.center = center
        signal.center_spacing = center_spacing
        signal.noise_threshold = noise
        signal.tolerance = tolerance
        signal.silent_set_modulation_type(modulation_type)
        signal.bits_per_symbol = bits_per_symbol
        ProtocolAnalyzer.__init__(self, signal)
        QObject.__init__(self, None)

        self.network_raw_mode = network_raw_mode
        self.backend_handler = backend_handler
        self.rcv_device = VirtualDevice(self.backend_handler, device, Mode.receive,
                                        resume_on_full_receive_buffer=True, raw_mode=network_raw_mode)

        signal.iq_array = IQArray(None, self.rcv_device.data_type, 0)

        self.sniff_thread = Thread(target=self.check_for_data, daemon=True)

        self.rcv_device.started.connect(self.__emit_started)
        self.rcv_device.stopped.connect(self.__emit_stopped)

        self.__buffer = IQArray(None, np.float32, 0)
        self.__init_buffer()
        self.__current_buffer_index = 0

        self.reading_data = False
        self.adaptive_noise = False
        self.automatic_center = False

        self.pause_length = 0
        self.is_running = False

        self.store_messages = True

        self.__sniff_file = ""
        self.__store_data = True

    def __add_to_buffer(self, data: np.ndarray):
        n = len(data)
        if n + self.__current_buffer_index > len(self.__buffer):
            n = len(self.__buffer) - self.__current_buffer_index - 1
            logger.warning("Buffer of protocol sniffer is full")

        self.__buffer[self.__current_buffer_index:self.__current_buffer_index + n] = data[:n]
        self.__current_buffer_index += n

    def __clear_buffer(self):
        self.__current_buffer_index = 0

    def __buffer_is_full(self):
        return self.__current_buffer_index >= len(self.__buffer) - 2

    def __init_buffer(self):
        self.__buffer = IQArray(None, self.rcv_device.data_type, int(self.BUFFER_SIZE_MB * 1000 * 1000 / 8))
        self.__current_buffer_index = 0

    def decoded_to_string(self, view: int, start=0, include_timestamps=True):
        result = []
        for msg in self.messages[start:]:
            result.append(self.message_to_string(msg, view, include_timestamps))
        return "\n".join(result)

    def message_to_string(self, message: Message, view: int, include_timestamps=True):
        msg_str_data = []
        if include_timestamps:
            msg_date = datetime.fromtimestamp(message.timestamp)
            msg_str_data.append(msg_date.strftime("[%Y-%m-%d %H:%M:%S.%f]"))
        msg_str_data.append(message.view_to_string(view, decoded=True, show_pauses=False))
        return " ".join(msg_str_data)

    @property
    def sniff_file(self):
        return self.__sniff_file

    @sniff_file.setter
    def sniff_file(self, val):
        self.__sniff_file = val
        if self.__sniff_file:
            self.__store_data = False

    @property
    def device_name(self):
        return self.rcv_device.name

    @device_name.setter
    def device_name(self, value: str):
        if value != self.rcv_device.name:
            self.rcv_device.free_data()
            self.rcv_device = VirtualDevice(self.backend_handler, value, Mode.receive, device_ip="192.168.10.2",
                                            resume_on_full_receive_buffer=True, raw_mode=self.network_raw_mode)
            self.rcv_device.started.connect(self.__emit_started)
            self.rcv_device.stopped.connect(self.__emit_stopped)

            self.signal.iq_array = IQArray(None, self.rcv_device.data_type, 0)

            self.__init_buffer()

    def sniff(self):
        self.is_running = True
        self.rcv_device.start()
        self.sniff_thread = Thread(target=self.check_for_data, daemon=True)
        self.sniff_thread.start()

    def check_for_data(self):
        old_index = 0
        while self.is_running:
            time.sleep(0.01)
            if self.rcv_device.is_raw_mode:
                if old_index <= self.rcv_device.current_index:
                    data = self.rcv_device.data[old_index:self.rcv_device.current_index]
                else:
                    data = np.concatenate((self.rcv_device.data[old_index:],
                                           self.rcv_device.data[:self.rcv_device.current_index]))
                old_index = self.rcv_device.current_index
                self.__demodulate_data(data)
            elif self.rcv_device.backend == Backends.network:
                # We receive the bits here
                for bit_str in self.rcv_device.data:
                    msg = Message.from_plain_bits_str(bit_str)
                    msg.decoder = self.decoder
                    self.messages.append(msg)
                    self.message_sniffed.emit(len(self.messages) - 1)

                self.rcv_device.free_data()  # do not store received bits twice

            if self.sniff_file and not os.path.isdir(self.sniff_file):
                plain_bits_str = self.plain_bits_str
                if plain_bits_str:
                    with open(self.sniff_file, "a") as f:
                        f.write("\n".join(plain_bits_str) + "\n")

            if not self.__store_data:
                self.messages.clear()

    def __demodulate_data(self, data):
        """
        Demodulates received IQ data and adds demodulated bits to messages
        :param data:
        :return:
        """
        if len(data) == 0:
            return

        power_spectrum = data.real ** 2.0 + data.imag ** 2.0
        is_above_noise = np.sqrt(np.mean(power_spectrum)) > self.signal.noise_threshold

        if self.adaptive_noise and not is_above_noise:
            self.signal.noise_threshold = 0.9 * self.signal.noise_threshold + 0.1 * np.sqrt(np.max(power_spectrum))

        if is_above_noise:
            self.__add_to_buffer(data)
            self.pause_length = 0
            if not self.__buffer_is_full():
                return
        else:
            self.pause_length += len(data)
            if self.pause_length < 10 * self.signal.samples_per_symbol:
                self.__add_to_buffer(data)
                if not self.__buffer_is_full():
                    return

        if self.__current_buffer_index == 0:
            return

        # clear cache and start a new message
        self.signal.iq_array = IQArray(self.__buffer[0:self.__current_buffer_index])
        self.__clear_buffer()
        self.signal._qad = None

        samples_per_symbol = self.signal.samples_per_symbol
        if self.automatic_center:
            self.signal.center = AutoInterpretation.detect_center(self.signal.qad, max_size=150*samples_per_symbol)

        ppseq = grab_pulse_lens(self.signal.qad, self.signal.center,
                                self.signal.tolerance, self.signal.modulation_type, self.signal.samples_per_symbol,
                                self.signal.bits_per_symbol, self.signal.center_spacing)

        bit_data, pauses, bit_sample_pos = self._ppseq_to_bits(ppseq, samples_per_symbol,
                                                               self.signal.bits_per_symbol, write_bit_sample_pos=False)

        for bits, pause in zip(bit_data, pauses):
            message = Message(bits, pause, samples_per_symbol=samples_per_symbol, message_type=self.default_message_type,
                              decoder=self.decoder)
            self.messages.append(message)
            self.message_sniffed.emit(len(self.messages) - 1)

    def stop(self):
        self.is_running = False
        self.rcv_device.stop("Stopping receiving due to user interaction")
        if self.sniff_thread.is_alive():
            self.sniff_thread.join(0.1)
        if self.sniff_thread.is_alive():
            logger.error("Sniff thread is still alive")

    def clear(self):
        self.__clear_buffer()
        self.messages.clear()

    def __emit_started(self):
        self.started.emit()

    def __emit_stopped(self):
        if hasattr(self, "stopped"):
            self.stopped.emit()
