import time
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Value

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import rtlsdr
from urh.util.Logger import logger


def receive_sync(rcv_queue: Queue, is_receiving_p: Value):
    while is_receiving_p.value == 1:
        rcv_queue.put(rtlsdr.read_sync(1024))
        time.sleep(0.01)
    return True


class RTLSDR(Device):
    BYTES_PER_SAMPLE = 2  # RTLSDR device produces 8 bit unsigned IQ data

    def __init__(self, freq, gain, srate, device_number, is_ringbuffer=False):
        super().__init__(0, freq, gain, srate, is_ringbuffer)

        self.success = 0

        self.is_receiving_p = Value('i', 0)
        """
        Shared Value to communicate with the receiving process.

        """

        self.bandwidth_is_adjustable = False
        self._max_frequency = 6e9
        self._max_sample_rate = 3200000
        self._max_frequency = 6e9
        # TODO: Consider get_tuner_gains for allowed gains

        self.device_number = device_number

    def open(self):
        if not self.is_open:
            ret = rtlsdr.open(self.device_number)
            self.log_retcode(ret, "open")

            ret = rtlsdr.reset_buffer()
            self.log_retcode(ret, "reset_buffer")

            self.is_open = ret == self.success
            self.log_retcode(ret, "open")

    def close(self):
        rtlsdr.close()

    def start_rx_mode(self):
        if self.is_open:
            self.init_recv_buffer()
            self.set_device_parameters()

            self.is_receiving = True

            self.is_receiving_p = Value('i', 1)
            self.receive_process = Process(target=receive_sync, args=(self.queue, self.is_receiving_p))
            self.receive_process.daemon = True
            self.receive_process.start()

            if self.is_receiving:
                logger.info("RTLSDR: Starting receiving thread")
                self._start_readqueue_thread()

        else:
            self.log_retcode(self.error_not_open, "start_rx_mode")

    def stop_rx_mode(self, msg):
        self.is_receiving = False
        self.is_receiving_p.value = 0

        logger.info("RTLSDR: Stopping RX Mode: " + msg)

        if hasattr(self, "read_queue_thread") and self.read_queue_thread.is_alive():
            try:
                self.read_queue_thread.join(0.001)
                logger.info("RTLSDR: Joined read_queue_thread")
            except RuntimeError:
                logger.error("RTLSDR: Could not join read_queue_thread")

        if hasattr(self, "receive_process") and self.receive_process.is_alive():
            if self.receive_process.is_alive():
                self.receive_process.join()
                if not self.receive_process.is_alive():
                    logger.info("RTLSDR: Terminated async read process")
                else:
                    logger.warning("RTLSDR: Could not terminate async read process")

    @staticmethod
    def unpack_complex(buffer, nvalues: int):
        """
        The raw, captured IQ data is 8 bit unsigned data.

        :return:
        """
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.uint8), ('i', np.uint8)])
        result.real = (unpacked['r'] / 127.5) - 1.0
        result.imag = (unpacked['i'] / 127.5) - 1.0
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        return (127.5 * (complex_samples.view(np.float32) + 1.0)).astype(np.uint8).tostring()
