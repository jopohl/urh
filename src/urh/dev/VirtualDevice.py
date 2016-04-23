import time

from PyQt5.QtCore import pyqtSignal

from urh import constants

from urh.dev.BackendHandler import Backends, BackendHandler
from enum import Enum

from urh.dev.gr.ReceiverThread import ReceiverThread
from urh.dev.gr.SenderThread import SenderThread
from urh.dev.gr.SpectrumThread import SpectrumThread
from urh.dev.native.HackRF import HackRF


class Mode(Enum):
    receive = 1
    send = 2
    spectrum = 3

class VirtualDevice(object):
    """
    Wrapper class for providing sending methods for grc and native devices

    """
    started = pyqtSignal()
    stopped = pyqtSignal()
    sender_needs_restart = pyqtSignal()


    def __init__(self, name: str, mode: Mode, bw, freq, gain, samp_rate, samples_to_send=None,
                 device_ip=None, sending_repeats=1, parent=None):
        self.name = name
        self.backend_handler = BackendHandler()
        self.backend = self.backend_handler.device_backends[name].selected_backend
        self.mode = mode

        if self.backend == Backends.grc:
            if mode == Mode.receive:
                self.__dev = ReceiverThread(samp_rate, freq, gain, bw, parent=parent)
            elif mode == Mode.send:
                self.__dev = SenderThread(samp_rate, freq, gain, bw, parent=parent)
                self.__dev.data = samples_to_send
                self.__dev.samples_per_transmission = len(samples_to_send)
            elif mode == Mode.spectrum:
                self.__dev = SpectrumThread(samp_rate, freq, gain, bw, parent=parent)
            else:
                raise ValueError("Unknown mode")
            self.__dev.usrp_ip = device_ip
            self.__dev.device = name
            self.__dev.started.connect(self.emit_started_signal)
            self.__dev.stopped.connect(self.emit_stopped_signal)
            self.__dev.sender_needs_restart.connect(self.emit_sender_needs_restart)
        elif self.backend == Backends.native:
            name = self.name.lower()
            if name in BackendHandler.DEVICE_NAMES:
                is_ringbuffer = self.mode == Mode.spectrum
                if name == "hackrf":
                    self.__dev = HackRF(bw, freq, gain, samp_rate, is_ringbuffer=is_ringbuffer)
                else:
                    raise NotImplementedError("Native Backend for {0} not yet implemented".format(name))
            else:
                raise ValueError("Unknown device name {0}".format(name))
            self.__dev.device_ip = device_ip
            if mode == Mode.send:
                self.__dev.init_send_parameters(samples_to_send, sending_repeats)
        else:
            raise ValueError("Unsupported Backend")

    @property
    def bandwidth(self):
        return self.__dev.bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self.__dev.bandwidth = value

    @property
    def frequency(self):
        if self.backend == Backends.grc:
            return self.__dev.freq
        elif self.backend == Backends.native:
            return self.__dev.frequency
        else:
            raise ValueError("Unsupported Backend")

    @frequency.setter
    def frequency(self, value):
        if self.backend == Backends.grc:
            self.__dev.freq = value
        elif self.backend == Backends.native:
            self.__dev.frequency = value
        else:
            raise ValueError("Unsupported Backend")

    @property
    def gain(self):
        return self.__dev.gain

    @gain.setter
    def gain(self, value):
        self.__dev.gain = value

    @property
    def sample_rate(self):
        return self.__dev.sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__dev.sample_rate = value

    @property
    def samples_to_send(self):
        if self.backend == Backends.grc:
            return self.__dev.data
        elif self.backend == Backends.native:
            return self.__dev.samples_to_send
        else:
            raise ValueError("Unsupported Backend")

    @property
    def ip(self):
        if self.backend == Backends.grc:
            return self.__dev.usrp_ip
        elif self.backend == Backends.native:
            return self.__dev.device_ip
        else:
            raise ValueError("Unsupported Backend")

    @ip.setter
    def ip(self, value):
        if self.backend == Backends.grc:
            self.__dev.usrp_ip = value
        elif self.backend == Backends.native:
            self.__dev.device_ip = value
        else:
            raise ValueError("Unsupported Backend")

    @property
    def data(self):
        if self.backend == Backends.grc:
            return self.__dev.data
        elif self.backend == Backends.native:
            if self.mode == Mode.send:
                return self.__dev.samples_to_send
            else:
                return self.__dev.receive_buffer
        else:
            raise ValueError("Unsupported Backend")

    @property
    def num_sending_repeats(self):
        if self.mode == Mode.send:
            if self.backend == Backends.grc:
                return self.__dev.max_repeats
            elif self.backend == Backends.native:
                return self.__dev.sending_repeats
            else:
                raise ValueError("Unsupported Backend")

    @num_sending_repeats.setter
    def num_sending_repeats(self, value):
        if self.mode == Mode.send:
            if self.backend == Backends.grc:
                if value != self.__dev.max_repeats:
                    self.__dev.max_repeats = value
                    self.__dev.current_iteration = 0
            elif self.backend == Backends.native:
                self.__dev.sending_repeats = value if value != 0 else -1
            else:
                raise ValueError("Unsupported Backend")

    def start(self):
        if self.backend == Backends.grc:
            self.__dev.setTerminationEnabled(True)
            self.__dev.terminate()
            time.sleep(0.1)
            self.__dev.start() # Already connected to started signal in constructor
        elif self.backend == Backends.native:
            if not self.__dev.is_open:
                self.__dev.open()

            if self.mode == Mode.send:
                self.__dev.start_tx_mode()

            self.emit_started_signal()
        else:
            raise ValueError("Unsupported Backend")


    def stop(self, msg: str):
        if self.backend == Backends.grc:
            self.__dev.stop(msg) # Already connected to stopped in constructor
        elif self.backend == Backends.native:
            if self.mode == Mode.send:
                self.__dev.stop_tx_mode(msg)
            else:
                self.__dev.stop_rx_mode(msg)
            self.emit_stopped_signal()
        else:
            raise ValueError("Unsupported Backend")


    def emit_stopped_signal(self):
        self.stopped.emit()

    def emit_started_signal(self):
        self.started.emit()

    def emit_sender_needs_restart(self):
        self.sender_needs_restart.emit()