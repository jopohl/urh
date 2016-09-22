import socket

import numpy as np

from urh.dev.gr.AbstractBaseThread import AbstractBaseThread


class SpectrumThread(AbstractBaseThread):
    def __init__(self, sample_rate, freq, gain, bandwidth, ip='127.0.0.1', parent=None):
        super().__init__(sample_rate, freq, gain, bandwidth, True, ip, parent)
        buf_size = int(sample_rate)
        self.data = np.zeros(buf_size, dtype=np.complex64)
        self.x = None
        self.y = None

    def run(self):
        self.initalize_process()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        while not self.isInterruptionRequested():
            try:
                self.socket.connect((self.ip, self.port))
                break
            except (ConnectionRefusedError, ConnectionResetError):
                continue

        recv = self.socket.recv
        rcvd = b""

        while not self.isInterruptionRequested():
            try:
                rcvd += recv(32768)  # Receive Buffer = 32768 Byte
            except ConnectionResetError:
                self.stop("Stopped receiving, because connection was reset")
                return

            if len(rcvd) < 8:
                self.stop("Stopped receiving, because no data transmitted anymore")
                return

            if len(rcvd) % 8 != 0:
                continue

            try:
                tmp = np.fromstring(rcvd, dtype=np.complex64)

                len_tmp = len(tmp)
                if self.current_index + len_tmp >= len(self.data):
                    self.data[self.current_index:] = tmp[:len(self.data) - self.current_index]
                    tmp = tmp[len(self.data) - self.current_index:]
                    w = np.abs(np.fft.fft(self.data))
                    freqs = np.fft.fftfreq(len(w), 1 / self.sample_rate)
                    idx = np.argsort(freqs)
                    self.x = freqs[idx].astype(np.float32)
                    self.y = w[idx].astype(np.float32)

                    self.data = np.zeros(len(self.data), dtype=np.complex64)
                    self.data[0:len(tmp)] = tmp
                    self.current_index = len(tmp)
                    continue

                self.data[self.current_index:self.current_index + len_tmp] = tmp
                self.current_index += len_tmp
                rcvd = b""
            except ValueError:
                self.stop("Could not receive data. Is your Hardware ok?")