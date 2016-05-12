import os
import time

import gc
import numpy as np
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from urh.cythonext.signalFunctions import grab_pulse_lens
from urh.dev.BackendHandler import BackendHandler
from urh.dev.VirtualDevice import VirtualDevice, Mode

from urh.dev.gr.ReceiverThread import ReceiverThread
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock
from urh.signalprocessing.Signal import Signal
from urh.util.Errors import Errors


class ProtocolSniffer(ProtocolAnalyzer, QObject):
    """
    This class is used for live sniffing a protocol
    with certain signal parameters.
    """
    started = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, bit_len: int, center: float, noise: float, tolerance:
    int, modulation_type: int, sample_rate: float, freq: float, gain: int,
                 bandwidth: float, device: str, usrp_ip="192.168.10.2"):
        signal = Signal("", "LiveSignal")
        signal.bit_len = bit_len
        signal.qad_center = center
        signal.noise_treshold = noise
        signal.tolerance = tolerance
        signal.silent_set_modulation_type(modulation_type)
        ProtocolAnalyzer.__init__(self, signal)
        QObject.__init__(self, None)

        self.backend_handler = BackendHandler()
        self.rcv_device = VirtualDevice(self.backend_handler, device, Mode.receive, bandwidth, freq, gain, sample_rate, device_ip=usrp_ip, is_ringbuffer=True)

        self.rcv_device.index_changed.connect(self.on_rcv_thread_index_changed)
        self.rcv_device.started.connect(self.__emit_started)
        self.rcv_device.stopped.connect(self.__emit_stopped)

        self.rcv_timer = QTimer()
        self.rcv_timer.setInterval(1000)
        self.rcv_timer.timeout.connect(self.on_rcv_timer_timeout)

        self.rel_symbol_len = self._read_symbol_len()

        self.data_cache = []
        self.conseq_non_data = 0
        self.reading_data = False

        self.store_blocks = True

        self.__sniff_file = ""
        self.__store_data = True

    def plain_to_string(self, view: int, show_pauses=True, start=0) -> str:
        """

        :param view: 0 - Bits ## 1 - Hex ## 2 - ASCII
        """
        return '\n'.join(block.view_to_string(view, False, show_pauses) for
                         block in self.blocks[start:])

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
            gc.collect()
            self.rcv_device = VirtualDevice(self.backend_handler, value, self.rcv_device.mode, self.rcv_device.bandwidth, self.rcv_device.frequency, self.rcv_device.gain,
                                        self.rcv_device.sample_rate, device_ip=self.rcv_device.ip, is_ringbuffer=True)
            self.rcv_device.index_changed.connect(self.on_rcv_thread_index_changed)
            self.rcv_device.started.connect(self.__emit_started)
            self.rcv_device.stopped.connect(self.__emit_stopped)

    @property
    def usrp_ip(self):
        return self.rcv_device.ip

    @usrp_ip.setter
    def usrp_ip(self, value: str):
        self.rcv_device.ip = value

    def sniff(self):
        self.rcv_device.start()
        self.rcv_timer.start()

    @pyqtSlot(int, int)
    def on_rcv_thread_index_changed(self, old_index, new_index):
        signal = self.signal

        data = self.rcv_device.data[old_index:new_index]
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

        signal._fulldata = np.concatenate(self.data_cache)
        del self.data_cache[:]
        signal._qad = None

        bit_len = signal.bit_len
        ppseq = grab_pulse_lens(signal.qad, signal.qad_center,
                                signal.tolerance, signal.modulation_type)

        bit_data, pauses, bit_sample_pos = self._ppseq_to_bits(ppseq, bit_len, self.rel_symbol_len)

        i = 0
        first_block = True
        old_nblocks = len(self.blocks)
        for bits, pause in zip(bit_data, pauses):
            if first_block or self.blocks[-1].pause > 8 * bit_len:
                # Create new Block
                middle_bit_pos = bit_sample_pos[i][int(len(bits) / 2)]
                start, end = middle_bit_pos, middle_bit_pos + bit_len
                rssi = np.mean(np.abs(signal._fulldata[start:end]))
                block = ProtocolBlock(bits, pause, self.bit_alignment_positions,
                                      bit_len=bit_len, rssi=rssi)
                self.blocks.append(block)
                first_block = False
            else:
                # Append to last block
                block = self.blocks[-1]
                nzeros = int(np.round(block.pause / bit_len))
                block.plain_bits.extend([False] * nzeros)
                block.plain_bits.extend(bits)
                block.pause = pause
            i += 1

        self.qt_signals.data_sniffed.emit(old_nblocks)

        if self.sniff_file and not os.path.isdir(self.sniff_file):
            # Write Header
            if not os.path.isfile(self.sniff_file):
                with open(self.sniff_file, "w") as f:
                    f.write("PROTOCOL:\n\n")

            with open(self.sniff_file, "a") as myfile:
                if self.plain_bits_str:
                    myfile.write("\n")

                myfile.write("\n".join(self.plain_bits_str))

        if not self.__store_data:
            self.blocks[:] = []

    def __are_bits_in_data(self, data):
        signal = self.signal
        signal._fulldata = data
        signal._qad = None

        bit_len = signal.bit_len
        ppseq = grab_pulse_lens(signal.qad, signal.qad_center,
                                signal.tolerance, signal.modulation_type)

        bit_data, pauses = self._ppseq_to_bits(ppseq, bit_len, self.rel_symbol_len)

        return bool(bit_data)


    def stop(self):
        self.rcv_timer.stop()
        self.rcv_device.stop("Stopping receiving due to user interaction")
        QApplication.processEvents()
        time.sleep(0.1)

    def clear(self):
        del self.data_cache[:]
        del self.blocks[:]

    def on_rcv_timer_timeout(self):
        new_errors = self.rcv_device.read_errors()
        self.qt_signals.sniff_device_errors_changed.emit(new_errors)
        if "No devices found for" in new_errors:
            self.rcv_device.stop("Could not establish connection to USRP")
            Errors.usrp_ip_not_found()
            self.stop()

        elif "FATAL: No supported devices found" in new_errors or \
                        "HACKRF_ERROR_NOT_FOUND" in new_errors:
            self.rcv_device.stop("Could not establish connection to HackRF")
            Errors.hackrf_not_found()
            self.stop()

        elif "No module named gnuradio" in new_errors:
            self.rcv_device.stop("Did not find gnuradio.")
            Errors.gnuradio_not_installed()
            self.stop()

        elif "Address already in use" in new_errors:
            self.rcv_device.port += 1
            self.stop()
            self.sniff()


    def __emit_started(self):
        self.started.emit()

    def __emit_stopped(self):
        self.stopped.emit()
