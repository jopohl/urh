import os
import socket
import sys
import tempfile
import time
from queue import Queue, Empty
from subprocess import Popen, PIPE
from threading import Thread

from PyQt5.QtCore import QThread, pyqtSignal

from urh import settings
from urh.util.Logger import logger

ON_POSIX = 'posix' in sys.builtin_module_names


class AbstractBaseThread(QThread):
    started = pyqtSignal()
    stopped = pyqtSignal()
    sender_needs_restart = pyqtSignal()

    def __init__(self, frequency, sample_rate, bandwidth, gain, if_gain, baseband_gain, receiving: bool,
                 ip='127.0.0.1', parent=None):
        super().__init__(parent)
        self.ip = ip
        self.gr_port = 1337
        self._sample_rate = sample_rate
        self._frequency = frequency
        self._gain = gain
        self._if_gain = if_gain
        self._baseband_gain = baseband_gain
        self._bandwidth = bandwidth
        self._freq_correction = 1
        self._direct_sampling_mode = 0
        self._antenna_index = 0
        self._channel_index = 0
        self._receiving = receiving  # False for Sender-Thread
        self.device = "USRP"
        self.current_index = 0

        self.is_in_spectrum_mode = False

        self.socket = None

        self.gr_python_interpreter = settings.read("gr_python_interpreter", "")

        self.queue = Queue()
        self.data = None  # Placeholder for SenderThread
        self.current_iteration = 0  # Counts number of Sendings in SenderThread

        self.gr_process = None

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self._sample_rate = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'SR:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._frequency = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'F:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, value):
        self._gain = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'G:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def if_gain(self):
        return self._if_gain

    @if_gain.setter
    def if_gain(self, value):
        self._if_gain = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'IFG:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def baseband_gain(self):
        return self._baseband_gain

    @baseband_gain.setter
    def baseband_gain(self, value):
        self._baseband_gain = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'BBG:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def bandwidth(self):
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self._bandwidth = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'BW:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def freq_correction(self):
        return self._freq_correction

    @freq_correction.setter
    def freq_correction(self, value):
        self._freq_correction = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'FC:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def channel_index(self):
        return self._channel_index

    @channel_index.setter
    def channel_index(self, value):
        self._channel_index = value

    @property
    def antenna_index(self):
        return self._antenna_index

    @antenna_index.setter
    def antenna_index(self, value):
        self._antenna_index = value

    @property
    def direct_sampling_mode(self):
        return self._direct_sampling_mode

    @direct_sampling_mode.setter
    def direct_sampling_mode(self, value):
        self._direct_sampling_mode = value
        if self.gr_process:
            try:
                self.gr_process.stdin.write(b'DSM:' + bytes(str(value), "utf8") + b'\n')
                self.gr_process.stdin.flush()
            except BrokenPipeError:
                pass

    def initialize_process(self):
        self.started.emit()

        if not hasattr(sys, 'frozen'):
            rp = os.path.realpath(os.path.join(os.path.dirname(__file__), "scripts"))
        else:
            rp = os.path.realpath(os.path.dirname(sys.executable))

        suffix = "_recv.py" if self._receiving else "_send.py"
        filename = self.device.lower().split(" ")[0] + suffix

        if not self.gr_python_interpreter:
            self.stop(
                "FATAL: Could not find a GR compatible Python interpreter. "
                "Make sure you have a running GNU Radio installation.")
            return

        options = [self.gr_python_interpreter, os.path.join(rp, filename),
                   "--sample-rate", str(int(self.sample_rate)), "--frequency", str(int(self.frequency)),
                   "--gain", str(self.gain), "--if-gain", str(self.if_gain), "--bb-gain", str(self.baseband_gain),
                   "--bandwidth", str(int(self.bandwidth)), "--freq-correction", str(self.freq_correction),
                   "--direct-sampling", str(self.direct_sampling_mode),  "--channel-index", str(self.channel_index),
                   "--port", str(self.gr_port)]

        logger.info("Starting GNU Radio")
        logger.debug(" ".join(options))
        self.gr_process = Popen(options, stdout=PIPE, stderr=PIPE, stdin=PIPE, bufsize=1)
        logger.info("Started GNU Radio")
        t = Thread(target=self.enqueue_output, args=(self.gr_process.stderr, self.queue))
        t.daemon = True  # thread dies with the program
        t.start()

    def init_recv_socket(self):
        logger.info("Initializing receive socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.info("Initialized receive socket")

        while not self.isInterruptionRequested():
            try:
                time.sleep(0.1)
                logger.info("Trying to get a connection to GNU Radio...")
                self.socket.connect((self.ip, self.gr_port))
                logger.info("Got connection")
                break
            except (ConnectionRefusedError, ConnectionResetError):
                continue
            except Exception as e:
                logger.error("Unexpected error", str(e))

    def run(self):
        pass

    def read_errors(self, initial_errors=None):
        result = [] if initial_errors is None else initial_errors
        while True:
            try:
                result.append(self.queue.get_nowait())
            except Empty:
                break

        result = b"".join(result)
        try:
            return result.decode("utf-8")
        except UnicodeDecodeError:
            return "Could not decode device message"

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def stop(self, msg: str):
        if msg and not msg.startswith("FIN"):
            self.requestInterruption()
            time.sleep(0.1)

        try:
            logger.info("Kill grc process")
            self.gr_process.kill()
            logger.info("Term grc process")
            self.gr_process.terminate()
            self.gr_process = None
        except AttributeError:
            pass

        logger.info(msg)
        self.stopped.emit()
