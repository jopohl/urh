import numpy as np
import zmq

from urh import constants
from urh.dev.gr.AbstractBaseThread import AbstractBaseThread
from urh.util.LinearBuffer import LinearBuffer
from urh.util.Logger import logger


class SpectrumThread(AbstractBaseThread):
    def __init__(self, freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, ip='127.0.0.1', parent=None):
        super().__init__(freq, sample_rate, bandwidth, gain, if_gain, baseband_gain, True, ip, parent)
        self.buf_size = constants.SPECTRUM_BUFFER_SIZE
        self.spectrum_buffer = LinearBuffer(self.buf_size)
        self.data = np.zeros(self.buf_size, dtype=np.complex64)

    def run(self):
        logger.debug("Spectrum Thread: Init Process")
        self.initialize_process()
        logger.debug("Spectrum Thread: Process Intialized")
        self.init_recv_socket()
        logger.debug("Spectrum Thread: Socket initialized")

        recv = self.socket.recv
        rcvd = b""

        try:
            logger.debug("Spectrum Thread: Enter main loop")
            while not self.isInterruptionRequested():
                try:
                    rcvd += recv(32768)  # Receive Buffer = 32768 Byte
                except (zmq.error.ContextTerminated, ConnectionResetError):
                    self.stop("Stopped receiving, because connection was reset")
                    return
                except OSError as e:  # https://github.com/jopohl/urh/issues/131
                    logger.warning("Error occurred", str(e))

                if len(rcvd) < 8:
                    self.stop("Stopped receiving, because no data transmitted anymore")
                    return

                if len(rcvd) % 8 != 0:
                    continue

                try:
                    self.current_index = 1  # show GUI we are working

                    data = np.fromstring(rcvd, dtype=np.complex64)
                    self.spectrum_buffer.push(data)
                    rcvd = b""
                except ValueError:
                    self.stop("Could not receive data. Is your Hardware ok?")
        except RuntimeError as e:
            logger.error("Spectrum thread crashed", str(e.args))
