import os
import socket
import sys
from queue import Queue, Empty
from subprocess import Popen, PIPE
from threading import Thread

from PyQt5.QtCore import QThread, pyqtSignal

ON_POSIX = 'posix' in sys.builtin_module_names


class AbstractBaseThread(QThread):
    started = pyqtSignal()
    stopped = pyqtSignal()
    sender_needs_restart = pyqtSignal()

    def __init__(self, sample_rate, freq, gain, bandwidth, receiving: bool,
                 ip='127.0.0.1', parent=None):
        super().__init__(parent)
        self.ip = ip
        self.port = 1337
        self._sample_rate = sample_rate
        self._freq = freq
        self._gain = gain
        self._bandwidth = bandwidth
        self._receiving = receiving  # False for Sender-Thread
        self.usrp_ip = "192.168.10.2"
        self.device = "USRP"
        self.current_index = 0
        self.python2_interpreter = self.get_python2_interpreter()
        self.queue = Queue()
        self.data = None  # Placeholder for SenderThread
        self.connection = None  # For SenderThread used to connect so GnuRadio Socket
        self.current_iteration = 0  # Counts number of Sendings in SenderThread


        self.tb_process = None

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        self._sample_rate = value
        if self.tb_process:
            try:
                self.tb_process.stdin.write(b'SR:' + bytes(str(value), "utf8") + b'\n')
                self.tb_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, value):
        self._freq = value
        if self.tb_process:
            try:
                self.tb_process.stdin.write(b'F:' + bytes(str(value), "utf8") + b'\n')
                self.tb_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, value):
        self._gain = value
        if self.tb_process:
            try:
                self.tb_process.stdin.write(b'G:' + bytes(str(value), "utf8") + b'\n')
                self.tb_process.stdin.flush()
            except BrokenPipeError:
                pass

    @property
    def bandwidth(self):
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, value):
        self._bandwidth = value
        if self.tb_process:
            try:
                self.tb_process.stdin.write(b'BW:' + bytes(str(value), "utf8") + b'\n')
                self.tb_process.stdin.flush()
            except BrokenPipeError:
                pass

    def initalize_process(self):
        self.started.emit()

        if not hasattr(sys, 'frozen'):
            rp = os.path.dirname(os.path.realpath(__file__))
        else:
            rp = os.path.join(os.path.dirname(sys.executable), "dev", "gr")

        rp = os.path.realpath(os.path.join(rp, "scripts"))
        suffix = "_recv.py" if self._receiving else "_send.py"
        filename = self.device.lower() + suffix

        if self.python2_interpreter is None:
            raise Exception("Could not find python 2 interpreter. Make sure you have a running gnuradio installation.")

        options = [self.python2_interpreter, os.path.join(rp, filename),
                   "--samplerate", str(self.sample_rate), "--freq", str(self.freq),
                   "--gain", str(self.gain), "--bandwidth", str(self.bandwidth),
                   "--port", str(self.port)]

        if self.device.upper() == "USRP":
            options.extend(["--ip", self.usrp_ip])

        self.tb_process = Popen(options, stdout=PIPE, stderr=PIPE, stdin=PIPE, bufsize=1)
        t = Thread(target=self.enqueue_output, args=(self.tb_process.stderr, self.queue))
        t.daemon = True  # thread dies with the program
        t.start()

    def run(self):
        pass

    def get_python2_interpreter(self):
        paths = os.get_exec_path()

        for p in paths:
            for prog in ["python2", "python2.exe"]:
                attempt = os.path.join(p, prog)
                if os.path.isfile(attempt):
                    return attempt

        return None

    def read_errors(self):
        result = []
        while True:
            try:
                result.append(self.queue.get_nowait())
            except Empty:
                break

        result = b"".join(result)
        return result.decode("utf-8")


    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def stop(self, msg: str):
        if msg and not msg.startswith("FIN"):
            self.requestInterruption()

        if self._receiving:
            # Close Socket for Receiver Threads
            # No need to close for Sender Threads
            try:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

                self.socket.close()
            except AttributeError:
                pass

        if self.connection:
            self.connection.close()

        if self.tb_process:
            self.tb_process.kill()
            self.tb_process.terminate()
            self.tb_process = None

        print(msg)
        self.stopped.emit()
