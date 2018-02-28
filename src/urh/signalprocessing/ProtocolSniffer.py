import os
from datetime import datetime

import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from urh.cythonext.signalFunctions import grab_pulse_lens
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.util.util import profile


class ProtocolSniffer(ProtocolAnalyzer, QObject):
    """
    This class is used for live sniffing a protocol
    with certain signal parameters.
    """
    started = pyqtSignal()
    stopped = pyqtSignal()
    message_sniffed = pyqtSignal()

    def __init__(self, bit_len: int, center: float, noise: float, tolerance: int,
                 modulation_type: int, device: str, backend_handler: BackendHandler, network_raw_mode=False):
        signal = Signal("", "LiveSignal")
        signal.bit_len = bit_len
        signal.qad_center = center
        signal.noise_threshold = noise
        signal.tolerance = tolerance
        signal.silent_set_modulation_type(modulation_type)
        ProtocolAnalyzer.__init__(self, signal)
        QObject.__init__(self, None)

        self.network_raw_mode = network_raw_mode
        self.backend_handler = backend_handler
        self.rcv_device = VirtualDevice(self.backend_handler, device, Mode.receive,
                                        resume_on_full_receive_buffer=True, raw_mode=network_raw_mode)

        self.rcv_device.emit_data_received_signal = True
        self.rcv_device.data_received.connect(self.on_data_received)
        self.rcv_device.started.connect(self.__emit_started)
        self.rcv_device.stopped.connect(self.__emit_stopped)

        self.data_cache = []
        self.reading_data = False

        self.pause_length = 0

        self.store_messages = True

        self.__sniff_file = ""
        self.__store_data = True

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
            self.rcv_device.emit_data_received_signal = True
            self.rcv_device.data_received.connect(self.on_data_received)
            self.rcv_device.started.connect(self.__emit_started)
            self.rcv_device.stopped.connect(self.__emit_stopped)

    def sniff(self):
        self.rcv_device.start()

    @pyqtSlot(np.ndarray)
    def on_data_received(self, data: np.ndarray):
        if self.rcv_device.is_raw_mode:
            self.__demodulate_data(data)
        elif self.rcv_device.backend == Backends.network:
            # We receive the bits here
            for bit_str in self.rcv_device.data:
                msg = Message.from_plain_bits_str(bit_str)
                msg.decoder = self.decoder
                self.messages.append(msg)
                self.message_sniffed.emit()

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
        is_above_noise = np.mean(data.real ** 2 + data.imag ** 2) > self.signal.noise_threshold ** 2
        if is_above_noise:
            self.data_cache.append(data)
            self.pause_length = 0
            return
        else:
            self.pause_length += len(data)
            if self.pause_length < 10 * self.signal.bit_len:
                self.data_cache.append(data)
                return

        if len(self.data_cache) == 0:
            return

        # clear cache and start a new message
        self.signal._fulldata = np.concatenate(self.data_cache)
        self.data_cache.clear()
        self.signal._qad = None

        bit_len = self.signal.bit_len
        ppseq = grab_pulse_lens(self.signal.qad, self.signal.qad_center,
                                self.signal.tolerance, self.signal.modulation_type, self.signal.bit_len)

        bit_data, pauses, bit_sample_pos = self._ppseq_to_bits(ppseq, bit_len, write_bit_sample_pos=False)

        for bits, pause in zip(bit_data, pauses):
            message = Message(bits, pause, bit_len=bit_len, message_type=self.default_message_type,
                              decoder=self.decoder)
            self.messages.append(message)
            self.message_sniffed.emit()

    def stop(self):
        self.rcv_device.stop("Stopping receiving due to user interaction")

    def clear(self):
        self.data_cache.clear()
        self.messages.clear()

    def __emit_started(self):
        self.started.emit()

    def __emit_stopped(self):
        self.stopped.emit()
