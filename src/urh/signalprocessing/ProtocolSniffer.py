import os

import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from urh.cythonext.signalFunctions import grab_pulse_lens
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.VirtualDevice import VirtualDevice, Mode
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class ProtocolSniffer(ProtocolAnalyzer, QObject):
    """
    This class is used for live sniffing a protocol
    with certain signal parameters.
    """
    started = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, bit_len: int, center: float, noise: float, tolerance: int,
                 modulation_type: int, device: str, backend_handler: BackendHandler):
        signal = Signal("", "LiveSignal")
        signal.bit_len = bit_len
        signal.qad_center = center
        signal.noise_threshold = noise
        signal.tolerance = tolerance
        signal.silent_set_modulation_type(modulation_type)
        ProtocolAnalyzer.__init__(self, signal)
        QObject.__init__(self, None)

        self.backend_handler = backend_handler
        self.rcv_device = VirtualDevice(self.backend_handler, device, Mode.receive,
                                        resume_on_full_receive_buffer=True, raw_mode=False)

        self.rcv_device.index_changed.connect(self.on_rcv_thread_index_changed)
        self.rcv_device.started.connect(self.__emit_started)
        self.rcv_device.stopped.connect(self.__emit_stopped)

        self.data_cache = []
        self.conseq_non_data = 0
        self.reading_data = False

        self.store_messages = True

        self.__sniff_file = ""
        self.__store_data = True

    def decoded_to_string(self, view: int, start=0):
        return '\n'.join(msg.view_to_string(view, decoded=True, show_pauses=False) for msg in self.messages[start:])

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
                                            resume_on_full_receive_buffer=True, raw_mode=False)
            self.rcv_device.index_changed.connect(self.on_rcv_thread_index_changed)
            self.rcv_device.started.connect(self.__emit_started)
            self.rcv_device.stopped.connect(self.__emit_stopped)

    def sniff(self):
        self.rcv_device.start()

    @pyqtSlot(int, int)
    def on_rcv_thread_index_changed(self, old_index, new_index):
        old_nmsgs = len(self.messages)
        if self.rcv_device.backend in (Backends.native, Backends.grc):
            if old_index == new_index:
                return
            self.__demodulate_data(self.rcv_device.data[old_index:new_index])
        elif self.rcv_device.backend == Backends.network:
            # We receive the bits here
            for bit_str in self.rcv_device.data:
                msg = Message.from_plain_bits_str(bit_str)
                msg.decoder = self.decoder
                self.messages.append(msg)

            self.rcv_device.free_data()  # do not store received bits twice

        self.qt_signals.data_sniffed.emit(old_nmsgs)

        if self.sniff_file and not os.path.isdir(self.sniff_file):
            with open(self.sniff_file, "a") as myfile:
                myfile.write("\n".join(self.plain_bits_str))

        if not self.__store_data:
            self.messages.clear()

    def __demodulate_data(self, data):
        """
        Demodulates received IQ data and adds demodulated bits to messages
        :param data:
        :return:
        """
        if self.__are_bits_in_data(data):
            self.reading_data = True
        elif self.conseq_non_data == 5:
            self.reading_data = False
            self.conseq_non_data = 0
        else:
            self.conseq_non_data += 1

        if self.reading_data:
            self.data_cache.append(data)
            return
        elif len(self.data_cache) == 0:
            return

        self.signal._fulldata = np.concatenate(self.data_cache)
        self.data_cache.clear()
        self.signal._qad = None

        bit_len = self.signal.bit_len
        ppseq = grab_pulse_lens(self.signal.qad, self.signal.qad_center,
                                self.signal.tolerance, self.signal.modulation_type)

        bit_data, pauses, bit_sample_pos = self._ppseq_to_bits(ppseq, bit_len)

        i = 0
        first_msg = True

        for bits, pause in zip(bit_data, pauses):
            if first_msg or self.messages[-1].pause > 8 * bit_len:
                # Create new Message
                middle_bit_pos = bit_sample_pos[i][int(len(bits) / 2)]
                start, end = middle_bit_pos, middle_bit_pos + bit_len
                rssi = np.mean(np.abs(self.signal._fulldata[start:end]))
                message = Message(bits, pause, bit_len=bit_len, rssi=rssi, message_type=self.default_message_type,
                                  decoder=self.decoder)
                self.messages.append(message)
                first_msg = False
            else:
                # Append to last message
                message = self.messages[-1]
                nzeros = int(np.round(message.pause / bit_len))
                message.plain_bits.extend([False] * nzeros)
                message.plain_bits.extend(bits)
                message.pause = pause
            i += 1

    def __are_bits_in_data(self, data):
        self.signal._fulldata = data
        self.signal._qad = None

        bit_len = self.signal.bit_len
        ppseq = grab_pulse_lens(self.signal.qad, self.signal.qad_center,
                                self.signal.tolerance, self.signal.modulation_type)

        bit_data, pauses, _ = self._ppseq_to_bits(ppseq, bit_len)

        return bool(bit_data)

    def stop(self):
        self.rcv_device.stop("Stopping receiving due to user interaction")

    def clear(self):
        self.data_cache.clear()
        self.messages.clear()

    def __emit_started(self):
        self.started.emit()

    def __emit_stopped(self):
        self.stopped.emit()
