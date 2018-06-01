import time
from enum import Enum

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject

from urh.dev import config
from urh.dev.BackendHandler import Backends, BackendHandler
from urh.dev.native.Device import Device
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.util.Logger import logger


class Mode(Enum):
    receive = 1
    send = 2
    spectrum = 3


class VirtualDevice(QObject):
    """
    Wrapper class for providing sending methods for grc and native devices

    """
    started = pyqtSignal()
    stopped = pyqtSignal()
    sender_needs_restart = pyqtSignal()

    fatal_error_occurred = pyqtSignal(str)
    ready_for_action = pyqtSignal()

    continuous_send_msg = "Continuous send mode is not supported for GNU Radio backend. " \
                          "You can change the configured device backend in options."

    def __init__(self, backend_handler, name: str, mode: Mode, freq=None, sample_rate=None, bandwidth=None,
                 gain=None, if_gain=None, baseband_gain=None, samples_to_send=None,
                 device_ip=None, sending_repeats=1, parent=None, resume_on_full_receive_buffer=False, raw_mode=True,
                 portnumber=1234):
        super().__init__(parent)
        self.name = name
        self.mode = mode
        self.backend_handler = backend_handler

        freq = config.DEFAULT_FREQUENCY if freq is None else freq
        sample_rate = config.DEFAULT_SAMPLE_RATE if sample_rate is None else sample_rate
        bandwidth = config.DEFAULT_BANDWIDTH if bandwidth is None else bandwidth
        gain = config.DEFAULT_GAIN if gain is None else gain
        if_gain = config.DEFAULT_IF_GAIN if if_gain is None else if_gain
        baseband_gain = config.DEFAULT_BB_GAIN if baseband_gain is None else baseband_gain

        resume_on_full_receive_buffer = self.mode == Mode.spectrum or resume_on_full_receive_buffer

        if self.name == NetworkSDRInterfacePlugin.NETWORK_SDR_NAME:
            self.backend = Backends.network
        else:
            try:
                self.backend = self.backend_handler.device_backends[name.lower()].selected_backend
            except KeyError:
                logger.warning("Invalid device name: {0}".format(name))
                self.backend = Backends.none
                self.__dev = None
                return

        if self.backend == Backends.grc:
            if mode == Mode.receive:
                from urh.dev.gr.ReceiverThread import ReceiverThread
                self.__dev = ReceiverThread(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain,
                                            parent=parent, resume_on_full_receive_buffer=resume_on_full_receive_buffer)
            elif mode == Mode.send:
                from urh.dev.gr.SenderThread import SenderThread
                self.__dev = SenderThread(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain,
                                          parent=parent)
                self.__dev.data = samples_to_send
                self.__dev.samples_per_transmission = len(samples_to_send) if samples_to_send is not None else 2 ** 15
            elif mode == Mode.spectrum:
                from urh.dev.gr.SpectrumThread import SpectrumThread
                self.__dev = SpectrumThread(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain,
                                            parent=parent)
            else:
                raise ValueError("Unknown mode")
            self.__dev.device = name
            self.__dev.started.connect(self.emit_started_signal)
            self.__dev.stopped.connect(self.emit_stopped_signal)
            self.__dev.sender_needs_restart.connect(self.emit_sender_needs_restart)
        elif self.backend == Backends.native:
            name = self.name.lower()
            if name in map(str.lower, BackendHandler.DEVICE_NAMES):
                if name == "hackrf":
                    from urh.dev.native.HackRF import HackRF
                    self.__dev = HackRF(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain,
                                        resume_on_full_receive_buffer)
                elif name.replace("-", "") == "rtlsdr":
                    from urh.dev.native.RTLSDR import RTLSDR
                    self.__dev = RTLSDR(freq, gain, sample_rate, device_number=0,
                                        resume_on_full_receive_buffer=resume_on_full_receive_buffer)
                elif name.replace("-", "") == "rtltcp":
                    from urh.dev.native.RTLSDRTCP import RTLSDRTCP
                    self.__dev = RTLSDRTCP(freq, gain, sample_rate, bandwidth, device_number=0,
                                           resume_on_full_receive_buffer=resume_on_full_receive_buffer)
                elif name == "limesdr":
                    from urh.dev.native.LimeSDR import LimeSDR
                    self.__dev = LimeSDR(freq, gain, sample_rate, bandwidth, gain,
                                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
                elif name.startswith("airspy"):
                    from urh.dev.native.AirSpy import AirSpy
                    self.__dev = AirSpy(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain,
                                        resume_on_full_receive_buffer=resume_on_full_receive_buffer)
                elif name.startswith("usrp"):
                    from urh.dev.native.USRP import USRP
                    self.__dev = USRP(freq, gain, sample_rate, bandwidth, gain,
                                      resume_on_full_receive_buffer=resume_on_full_receive_buffer)
                elif name.startswith("sdrplay"):
                    from urh.dev.native.SDRPlay import SDRPlay
                    self.__dev = SDRPlay(freq, gain, bandwidth, gain, if_gain=if_gain,
                                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
                elif name == "soundcard":
                    from urh.dev.native.SoundCard import SoundCard
                    self.__dev = SoundCard(sample_rate, resume_on_full_receive_buffer=resume_on_full_receive_buffer)
                else:
                    raise NotImplementedError("Native Backend for {0} not yet implemented".format(name))

            elif name == "test":
                # For Unittests Only
                self.__dev = Device(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain,
                                    resume_on_full_receive_buffer)
            else:
                raise ValueError("Unknown device name {0}".format(name))
            self.__dev.portnumber = portnumber
            self.__dev.device_ip = device_ip
            if mode == Mode.send:
                self.__dev.init_send_parameters(samples_to_send, sending_repeats)
        elif self.backend == Backends.network:
            self.__dev = NetworkSDRInterfacePlugin(raw_mode=raw_mode,
                                                   resume_on_full_receive_buffer=resume_on_full_receive_buffer,
                                                   spectrum=self.mode == Mode.spectrum, sending=self.mode == Mode.send)
            self.__dev.send_connection_established.connect(self.emit_ready_for_action)
            self.__dev.receive_server_started.connect(self.emit_ready_for_action)
            self.__dev.error_occurred.connect(self.emit_fatal_error_occurred)
            self.__dev.samples_to_send = samples_to_send
        elif self.backend == Backends.none:
            self.__dev = None
        else:
            raise ValueError("Unsupported Backend")

        if mode == Mode.spectrum:
            self.__dev.is_in_spectrum_mode = True

    @property
    def has_multi_device_support(self):
        return hasattr(self.__dev, "has_multi_device_support") and self.__dev.has_multi_device_support

    @property
    def device_serial(self):
        if hasattr(self.__dev, "device_serial"):
            return self.__dev.device_serial
        else:
            return None

    @device_serial.setter
    def device_serial(self, value):
        if hasattr(self.__dev, "device_serial"):
            self.__dev.device_serial = value

    @property
    def device_number(self):
        if hasattr(self.__dev, "device_number"):
            return self.__dev.device_number
        else:
            return None

    @device_number.setter
    def device_number(self, value):
        if hasattr(self.__dev, "device_number"):
            self.__dev.device_number = value

    @property
    def bandwidth(self):
        return self.__dev.bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self.__dev.bandwidth = value

    @property
    def bandwidth_is_adjustable(self):
        if self.backend == Backends.grc:
            return True
        elif self.backend == Backends.native:
            return self.__dev.bandwidth_is_adjustable
        elif self.backend == Backends.network:
            return True
        else:
            raise ValueError("Unsupported Backend")

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
        elif self.backend == Backends.network:
            pass
        else:
            raise ValueError("Unsupported Backend")

    @property
    def num_samples_to_send(self) -> int:
        if self.backend in (Backends.native, Backends.network):
            return self.__dev.num_samples_to_send
        else:
            raise ValueError(self.continuous_send_msg)

    @num_samples_to_send.setter
    def num_samples_to_send(self, value: int):
        if self.backend in (Backends.native, Backends.network):
            self.__dev.num_samples_to_send = value
        else:
            raise ValueError(self.continuous_send_msg)

    @property
    def is_send_continuous(self) -> bool:
        if self.backend in (Backends.native, Backends.network):
            return self.__dev.sending_is_continuous
        else:
            raise ValueError(self.continuous_send_msg)

    @is_send_continuous.setter
    def is_send_continuous(self, value: bool):
        if self.backend in (Backends.native, Backends.network):
            self.__dev.sending_is_continuous = value
        else:
            raise ValueError(self.continuous_send_msg)

    @property
    def is_raw_mode(self) -> bool:
        if self.backend == Backends.network:
            return self.__dev.raw_mode
        else:
            return True

    @property
    def continuous_send_ring_buffer(self):
        if self.backend in (Backends.native, Backends.network):
            return self.__dev.continuous_send_ring_buffer
        else:
            raise ValueError(self.continuous_send_msg)

    @continuous_send_ring_buffer.setter
    def continuous_send_ring_buffer(self, value):
        if self.backend in (Backends.native, Backends.network):
            self.__dev.continuous_send_ring_buffer = value
        else:
            raise ValueError(self.continuous_send_msg)

    @property
    def is_in_spectrum_mode(self):
        if self.backend in (Backends.grc, Backends.native, Backends.network):
            return self.__dev.is_in_spectrum_mode
        else:
            raise ValueError("Unsupported Backend")

    @is_in_spectrum_mode.setter
    def is_in_spectrum_mode(self, value: bool):
        if self.backend in (Backends.grc, Backends.native, Backends.network):
            self.__dev.is_in_spectrum_mode = value
        else:
            raise ValueError("Unsupported Backend")

    @property
    def gain(self):
        return self.__dev.gain

    @gain.setter
    def gain(self, value):
        try:
            self.__dev.gain = value
        except AttributeError as e:
            logger.warning(str(e))

    @property
    def if_gain(self):
        try:
            return self.__dev.if_gain
        except AttributeError as e:
            logger.warning(str(e))

    @if_gain.setter
    def if_gain(self, value):
        try:
            self.__dev.if_gain = value
        except AttributeError as e:
            logger.warning(str(e))

    @property
    def baseband_gain(self):
        return self.__dev.baseband_gain

    @baseband_gain.setter
    def baseband_gain(self, value):
        self.__dev.baseband_gain = value

    @property
    def sample_rate(self):
        return self.__dev.sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self.__dev.sample_rate = value

    @property
    def channel_index(self) -> int:
        return self.__dev.channel_index

    @channel_index.setter
    def channel_index(self, value: int):
        self.__dev.channel_index = value

    @property
    def antenna_index(self) -> int:
        return self.__dev.antenna_index

    @antenna_index.setter
    def antenna_index(self, value: int):
        self.__dev.antenna_index = value

    @property
    def freq_correction(self):
        return self.__dev.freq_correction

    @freq_correction.setter
    def freq_correction(self, value):
        self.__dev.freq_correction = value

    @property
    def direct_sampling_mode(self) -> int:
        return self.__dev.direct_sampling_mode

    @direct_sampling_mode.setter
    def direct_sampling_mode(self, value):
        self.__dev.direct_sampling_mode = value

    @property
    def samples_to_send(self):
        if self.backend == Backends.grc:
            return self.__dev.data
        elif self.backend in (Backends.native, Backends.network):
            return self.__dev.samples_to_send
        else:
            raise ValueError("Unsupported Backend")

    @samples_to_send.setter
    def samples_to_send(self, value):
        if self.backend == Backends.grc:
            self.__dev.data = value
        elif self.backend == Backends.native:
            self.__dev.init_send_parameters(value, self.num_sending_repeats)
        elif self.backend == Backends.network:
            self.__dev.samples_to_send = value
        else:
            raise ValueError("Unsupported Backend")

    @property
    def ip(self):
        if self.backend == Backends.grc:
            return self.__dev.device_ip
        elif self.backend == Backends.native:
            return self.__dev.device_ip
        else:
            raise ValueError("Unsupported Backend")

    @ip.setter
    def ip(self, value):
        if self.backend == Backends.grc:
            self.__dev.device_ip = value
        elif self.backend == Backends.native:
            self.__dev.device_ip = value
        elif self.backend in (Backends.none, Backends.network):
            pass
        else:
            raise ValueError("Unsupported Backend")

    @property
    def port(self):
        if self.backend in (Backends.grc, Backends.native, Backends.network):
            return self.__dev.port
        else:
            raise ValueError("Unsupported Backend")

    @port.setter
    def port(self, value):
        if self.backend in (Backends.grc, Backends.native, Backends.network):
            self.__dev.port = value
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
        elif self.backend == Backends.network:
            if self.mode == Mode.send:
                raise NotImplementedError("Todo")
            else:
                if self.__dev.raw_mode:
                    return self.__dev.receive_buffer
                else:
                    return self.__dev.received_bits
        else:
            raise ValueError("Unsupported Backend")

    @data.setter
    def data(self, value):
        if self.backend == Backends.grc:
            self.__dev.data = value
        elif self.backend == Backends.native:
            if self.mode == Mode.send:
                self.__dev.samples_to_send = value
            else:
                self.__dev.receive_buffer = value
        else:
            logger.warning("{}:{} has no data".format(self.__class__.__name__, self.backend.name))

    def free_data(self):
        if self.backend == Backends.grc:
            self.__dev.data = None
        elif self.backend == Backends.native:
            self.__dev.samples_to_send = None
            self.__dev.receive_buffer = None
        elif self.backend == Backends.network:
            self.__dev.free_data()
        elif self.backend == Backends.none:
            pass
        else:
            raise ValueError("Unsupported Backend")

    @property
    def resume_on_full_receive_buffer(self) -> bool:
        return self.__dev.resume_on_full_receive_buffer

    @resume_on_full_receive_buffer.setter
    def resume_on_full_receive_buffer(self, value: bool):
        if value != self.__dev.resume_on_full_receive_buffer:
            self.__dev.resume_on_full_receive_buffer = value
            if self.backend == Backends.native:
                self.__dev.receive_buffer = None
            elif self.backend == Backends.grc:
                self.__dev.data = None

    @property
    def num_sending_repeats(self):
        return self.__dev.sending_repeats

    @num_sending_repeats.setter
    def num_sending_repeats(self, value):
        self.__dev.sending_repeats = value

    @property
    def current_index(self):
        if self.backend == Backends.grc:
            return self.__dev.current_index
        elif self.backend == Backends.native:
            if self.mode == Mode.send:
                return self.__dev.current_sent_sample
            else:
                return self.__dev.current_recv_index
        elif self.backend == Backends.network:
            if self.mode == Mode.send:
                return self.__dev.current_sent_sample
            else:
                return self.__dev.current_receive_index
        else:
            raise ValueError("Unsupported Backend")

    @current_index.setter
    def current_index(self, value):
        if self.backend == Backends.grc:
            self.__dev.current_index = value
        elif self.backend == Backends.native:
            if self.mode == Mode.send:
                self.__dev.current_sent_sample = value
            else:
                self.__dev.current_recv_index = value
        elif self.backend == Backends.network:
            if self.mode == Mode.send:
                self.__dev.current_sent_sample = value
            else:
                self.__dev.current_receive_index = value
        else:
            raise ValueError("Unsupported Backend")

    @property
    def current_iteration(self):
        if self.backend == Backends.grc:
            return self.__dev.current_iteration
        elif self.backend in (Backends.native, Backends.network):
            return self.__dev.current_sending_repeat
        else:
            raise ValueError("Unsupported Backend")

    @current_iteration.setter
    def current_iteration(self, value):
        if self.backend == Backends.grc:
            self.__dev.current_iteration = value
        elif self.backend in (Backends.native, Backends.network):
            self.__dev.current_sending_repeat = value
        else:
            raise ValueError("Unsupported Backend")

    @property
    def sending_finished(self):
        if self.backend == Backends.grc:
            return self.__dev.current_iteration is None
        elif self.backend in (Backends.native, Backends.network):
            return self.__dev.sending_finished
        else:
            raise ValueError("Unsupported Backend")

    @property
    def spectrum(self):
        if self.mode == Mode.spectrum:
            if self.backend == Backends.grc:
                return self.__dev.x, self.__dev.y
            elif self.backend == Backends.native or self.backend == Backends.network:
                w = np.abs(np.fft.fft(self.__dev.receive_buffer))
                freqs = np.fft.fftfreq(len(w), 1 / self.sample_rate)
                idx = np.argsort(freqs)
                return freqs[idx].astype(np.float32), w[idx].astype(np.float32)
        else:
            raise ValueError("Spectrum x only available in spectrum mode")

    def start(self):
        if self.backend == Backends.grc:
            self.__dev.setTerminationEnabled(True)
            self.__dev.terminate()
            time.sleep(0.1)
            self.__dev.start()  # Already connected to started signal in constructor
        elif self.backend == Backends.native:
            if self.mode == Mode.send:
                self.__dev.start_tx_mode(resume=True)
            else:
                self.__dev.start_rx_mode()

            self.emit_started_signal()
        elif self.backend == Backends.network:
            if self.mode == Mode.receive or self.mode == Mode.spectrum:
                self.__dev.start_tcp_server_for_receiving()
            else:
                self.__dev.start_raw_sending_thread()

            self.emit_started_signal()
        else:
            raise ValueError("Unsupported Backend")

    def stop(self, msg: str):
        if self.backend == Backends.grc:
            self.__dev.stop(msg)  # Already connected to stopped in constructor
        elif self.backend == Backends.native:
            if self.mode == Mode.send:
                self.__dev.stop_tx_mode(msg)
            else:
                self.__dev.stop_rx_mode(msg)
            self.emit_stopped_signal()
        elif self.backend == Backends.network:
            self.__dev.stop_tcp_server()
            self.__dev.stop_sending_thread()
            self.emit_stopped_signal()
        elif self.backend == Backends.none:
            pass
        else:
            logger.error("Stop device: Unsupported backend " + str(self.backend))

    def stop_on_error(self, msg: str):
        if self.backend == Backends.grc:
            self.__dev.stop(msg)  # Already connected to stopped in constructor
        elif self.backend == Backends.native:
            self.read_messages()  # Clear errors
            self.__dev.stop_rx_mode("Stop on error")
            self.__dev.stop_tx_mode("Stop on error")
            self.emit_stopped_signal()
        else:
            raise ValueError("Unsupported Backend")

    def cleanup(self):
        if self.backend == Backends.grc:
            if self.mode == Mode.send:
                self.__dev.socket.close()
                time.sleep(0.1)
            self.__dev.quit()
            self.data = None

        elif self.backend == Backends.native:
            self.data = None

        elif self.backend == Backends.none:
            pass

        else:
            raise ValueError("Unsupported Backend")

    def emit_stopped_signal(self):
        self.stopped.emit()

    def emit_started_signal(self):
        self.started.emit()

    def emit_sender_needs_restart(self):
        self.sender_needs_restart.emit()

    def read_messages(self) -> str:
        """
        returns a string of new device messages separated by newlines

        :return:
        """
        if self.backend == Backends.grc:
            errors = self.__dev.read_errors()

            if "FATAL: " in errors:
                self.fatal_error_occurred.emit(errors[errors.index("FATAL: "):])

            return errors
        elif self.backend == Backends.native:
            messages = "\n".join(self.__dev.device_messages)
            self.__dev.device_messages.clear()

            if messages and not messages.endswith("\n"):
                messages += "\n"

            if "successfully started" in messages:
                self.ready_for_action.emit()
            elif "failed to start" in messages:
                self.fatal_error_occurred.emit(messages[messages.index("failed to start"):])

            return messages
        elif self.backend == Backends.network:
            return ""
        else:
            raise ValueError("Unsupported Backend")

    def set_server_port(self, port: int):
        if self.backend == Backends.network:
            self.__dev.server_port = port
        else:
            raise ValueError("Setting port only supported for NetworkSDR Plugin")

    def set_client_port(self, port: int):
        if self.backend == Backends.network:
            self.__dev.client_port = port
        else:
            raise ValueError("Setting port only supported for NetworkSDR Plugin")

    def get_device_list(self):
        if hasattr(self.__dev, "get_device_list"):
            return self.__dev.get_device_list()
        else:
            return []

    def increase_gr_port(self):
        if self.backend == Backends.grc:
            self.__dev.gr_port += 1
            logger.info("Retry with port " + str(self.__dev.gr_port))
        else:
            raise ValueError("Only for GR backend")

    def emit_ready_for_action(self):
        """
        Notify observers that device is successfully initialized
        :return:
        """
        self.ready_for_action.emit()

    def emit_fatal_error_occurred(self, msg: str):
        self.fatal_error_occurred.emit(msg)
