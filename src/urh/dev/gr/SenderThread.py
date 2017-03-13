import select
import socket

import numpy
import numpy as np
import time
import zmq

from urh.dev.gr.AbstractBaseThread import AbstractBaseThread
from urh.util.Logger import logger


class SenderThread(AbstractBaseThread):
    MAX_SAMPLES_PER_TRANSMISSION = 65536

    def __init__(self, freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, ip='127.0.0.1', parent=None):
        super().__init__(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, False, ip, parent)

        self.data = numpy.empty(1, dtype=numpy.complex64)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.gr_port = self.socket.bind_to_random_port("tcp://{0}".format(self.ip))
        self.max_repeats = 1  # How often shall we send the data?

        self.__samples_per_transmission = self.MAX_SAMPLES_PER_TRANSMISSION

    @property
    def repeat_endless(self):
        return self.max_repeats == 0 or self.max_repeats == -1

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
        self.initialize_process()
        len_data = len(self.data)
        self.current_iteration = self.current_iteration if self.current_iteration is not None else 0
        time.sleep(1)

        try:
            while self.current_index < len_data and not self.isInterruptionRequested():
                time.sleep(0.1 * (self.samples_per_transmission / self.MAX_SAMPLES_PER_TRANSMISSION))
                self.socket.send(self.data[self.current_index:self.current_index + self.samples_per_transmission].tostring())
                self.current_index += self.samples_per_transmission

                if self.current_index >= len_data:
                    self.current_iteration += 1
                else:
                    continue

                if self.repeat_endless or self.current_iteration < self.max_repeats:
                    self.current_index = 0

            self.current_index = len_data - 1
            self.current_iteration = None
            self.stop("FIN - All data was sent successfully")
        except RuntimeError:
            logger.error("Sender thread crashed.")
