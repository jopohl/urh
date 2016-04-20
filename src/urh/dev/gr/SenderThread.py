import select
import socket

import numpy
import numpy as np

from urh.dev.gr.AbstractBaseThread import AbstractBaseThread


class SenderThread(AbstractBaseThread):
    MAX_SAMPLES_PER_TRANSMISSION = 65536


    def __init__(self, sample_rate, freq, gain, bandwidth, ip='127.0.0.1', parent=None):
        super().__init__(sample_rate, freq, gain, bandwidth, False, ip, parent)

        self.data = numpy.empty(1, dtype=numpy.complex64)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while self.port < 65535:
            try:
                self.socket.bind((self.ip, self.port))
                self.socket.listen(1)
                break
            except OSError:
                self.port += 1

        self.repeat_endless = False
        self.max_repeats = 1 # How often shall we send the data?

        self.__samples_per_transmission = self.MAX_SAMPLES_PER_TRANSMISSION

    @property
    def samples_per_transmission(self):
        return self.__samples_per_transmission

    @samples_per_transmission.setter
    def samples_per_transmission(self, val: int):
        if val >= self.MAX_SAMPLES_PER_TRANSMISSION:
            self.__samples_per_transmission = self.MAX_SAMPLES_PER_TRANSMISSION
        elif val <= 1:
            self.__samples_per_transmission = 1
        else:
            self.__samples_per_transmission = 2 ** (int(np.log2(val)) - 1)

    def run(self):
        self.initalize_process()
        len_data = len(self.data)
        self.current_iteration = self.current_iteration if self.current_iteration is not None else 0
        self.connection, addr = self.socket.accept()
        while self.current_index < len_data and not self.isInterruptionRequested():
            try:
                _, outputready, _ = select.select([], [self.connection], [])
            except select.error:
                self.current_index = 0
                self.stop("There was an error in select.")
                break

            if self.connection in outputready:
                try:
                    self.connection.send(
                        self.data[self.current_index:self.current_index + self.samples_per_transmission].tobytes())
                except OSError:
                    self.current_index = 0
                    # Pipe is broken, restart Thread with new Port
                    self.sender_needs_restart.emit()
                    # self.stop("Could not send data: " + str(e))
                    return

                self.current_index += self.samples_per_transmission

            if self.current_index >= len_data:
                self.current_iteration += 1

                if self.repeat_endless or self.current_iteration < self.max_repeats:
                    self.current_index = 0

        self.current_index = len_data - 1
        self.current_iteration = None
        self.stop("FIN - All data was sent successfully")
