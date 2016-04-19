import struct

import time

from urh.dev.Device import Device
from urh.cythonext import hackrf
import numpy as np
from urh.util.Logger import logger


class HackRF(Device):
    BYTES_PER_SAMPLE = 2  # HackRF device produces 8 bit unsigned IQ data

    def __init__(self, bw, freq, gain, srate, initial_bufsize=8e9, is_ringbuffer=False):
        super().__init__(bw, freq, gain, srate, initial_bufsize, is_ringbuffer)
        self.is_open = False
        self.success = 0

        self.__lut = np.zeros(0xffff + 1, dtype=np.complex64)
        self.little_endian = False
        for i in range(0, 0xffff + 1):
            if self.little_endian:
                real = (float(np.int8(i & 0xff))) * (1.0 / 128.0)
                imag = (float(np.int8(i >> 8))) * (1.0 / 128.0)
            else:
                real = (float(np.int8(i >> 8))) * (1.0 / 128.0)
                imag = (float(np.int8(i & 0xff))) * (1.0 / 128.0)

            self.__lut[i] = complex(real, imag)

    def reopen(self):
        if self.is_open:
            hackrf.reopen()

    def open(self):
        if not self.is_open:
            if hackrf.setup() == self.success:
                self.is_open = True
                logger.info("successfully opened HackRF")
            else:
                logger.warning("failed to open HackRF")

    def close(self):
        if self.is_open:
            if hackrf.exit() == self.success:
                logger.info("successfully closed HackRF")
                self.is_open = False

    def start_rx_mode(self):
        if self.is_open:
            self.set_device_parameters()
            if hackrf.start_rx_mode(self.callback_recv) == self.success:
                self.is_receiving = True
                self.read_queue_thread.start()
                logger.info("successfully started HackRF rx mode")
            else:
                self.is_receiving = False
                logger.error("could not start HackRF rx mode")
        else:
            logger.error("Could not start HackRF rx mode: Device not open")

    def stop_rx_mode(self, msg):
        self.is_receiving = False
        if self.read_queue_thread.is_alive():
            self.read_queue_thread.join()
        if self.is_open:
            logger.info("Stopping rx mode")
            if hackrf.stop_rx_mode() == self.success:
                logger.info("stopped HackRF rx mode (" + str(msg) + ")")
            else:
                logger.error("could not stop HackRF rx mode")


    def switch_from_rx2tx(self):
        # https://github.com/mossmann/hackrf/pull/246/commits/4f9665fb3b43462e39a1592fc34f3dfb50de4a07
        self.reopen()

    def start_tx_mode(self, samples_to_send: np.ndarray, repeats=1):
        if self.is_open:
            self.init_send_parameters(samples_to_send, repeats)

            t = time.time()
            if hackrf.start_tx_mode(self.callback_send) == self.success:
                self.is_transmitting = True
                self.sendbuffer_thread.start()
                logger.info("successfully started HackRF tx mode")
            else:
                self.is_transmitting = False
                logger.error("could not start HackRF tx mode")
            print("other", 1000*(time.time()-t))
        else:
            logger.error("Could not start HackRF tx mode: Device not open")


    def stop_tx_mode(self, msg):
        self.is_transmitting = False
        if self.sendbuffer_thread.is_alive():
            logger.info("HackRF: closing send buffer thread")
            self.sendbuffer_thread.join()

        self.send_buffer_reader.close()
        self.send_buffer.close()

        if self.is_open:
            logger.info("stopping HackRF tx mode ({0})".format(msg))
            logger.info("closing because stop_tx_mode of HackRF is bugged and never returns")
            self.close()
            #if hackrf.stop_tx_mode() == self.success:
            # if hackrf.close
            #     logger.info("successfully stopped HackRF tx mode")
            # else:
            #     logger.error("could not stopped HackRF tx mode")

    def set_device_bandwidth(self, bw):
        if self.is_open:

            if hackrf.set_baseband_filter_bandwidth(bw) == self.success:
                logger.info("successfully set HackRF bandwidth to {0}".format(bw))
            else:
                logger.error("failed to set HackRF bandwidth to {0}".format(bw))

    def set_device_frequency(self, value):
        if self.is_open:
            if hackrf.set_freq(value) == self.success:
                logger.info("successfully set HackRF frequency to {0}".format(value))
            else:
                logger.error("failed to set HackRF frequency to {0}".format(value))

    def set_device_gain(self, gain):
        if self.is_open:
            hackrf.set_lna_gain(gain)
            hackrf.set_vga_gain(gain)
            hackrf.set_txvga_gain(gain)

    def set_device_sample_rate(self, sample_rate):
        if self.is_open:
            if hackrf.set_sample_rate(sample_rate) == self.success:
                logger.info("successfully set HackRF sample rate to {0}".format(sample_rate))
            else:
                logger.error("failed to set HackRF sample rate to {0}".format(sample_rate))

    def unpack_complex(self, buffer, nvalues: int):
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.int8), ('i', np.int8)])
        result.real = unpacked['r'] / 128.0
        result.imag = unpacked['i'] / 128.0
        return result


    def pack_complex(self, complex_samples: np.ndarray):
        assert complex_samples.dtype == np.complex64
        return (128 * complex_samples.view(np.float32)).astype(np.uint8).tobytes()