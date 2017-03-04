from multiprocessing import Process
from multiprocessing import Value

import numpy as np
from multiprocessing import Pipe

from urh.dev.native.Device import Device
try:
    from urh.dev.native.lib import rtlsdr
except ImportError:
    import urh.dev.native.lib.rtlsdr_fallback as rtlsdr
from urh.util.Logger import logger


def receive_sync(data_connection, ctrl_connection, device_number: int, center_freq: int, sample_rate: int, gain: int):
    ret = rtlsdr.open(device_number)
    ctrl_connection.send("open:"+str(ret))

    ret = rtlsdr.set_center_freq(center_freq)
    ctrl_connection.send("set_center_freq:" + str(ret))

    ret = rtlsdr.set_sample_rate(sample_rate)
    ctrl_connection.send("set_sample_rate:" + str(ret))

    ret = rtlsdr.set_tuner_gain(gain)
    ctrl_connection.send("set_tuner_gain:" + str(ret))

    ret = rtlsdr.reset_buffer()
    ctrl_connection.send("reset_buffer:" + str(ret))

    exit_requested = False

    while not exit_requested:
        while ctrl_connection.poll():
            result = process_command(ctrl_connection.recv())
            if result == "stop":
                exit_requested = True
                break

        if not exit_requested:
            data_connection.send_bytes(rtlsdr.read_sync())

    logger.debug("RTLSDR: closing device")
    ret = rtlsdr.close()
    ctrl_connection.send("close:" + str(ret))

    data_connection.close()
    ctrl_connection.close()

def process_command(command):
    logger.debug("RTLSDR: {}".format(command))
    if command == "stop":
        return "stop"

    tag, value = command.split(":")
    if tag == "center_freq":
        logger.info("RTLSDR: Set center freq to {0}".format(int(value)))
        return rtlsdr.set_center_freq(int(value))

    elif tag == "tuner_gain":
        logger.info("RTLSDR: Set tuner gain to {0}".format(int(value)))
        return rtlsdr.set_tuner_gain(int(value))

    elif tag == "sample_rate":
        logger.info("RTLSDR: Set sample_rate to {0}".format(int(value)))
        return rtlsdr.set_sample_rate(int(value))

    elif tag == "tuner_bandwidth":
        logger.info("RTLSDR: Set bandwidth to {0}".format(int(value)))
        return rtlsdr.set_tuner_bandwidth(int(value))


class RTLSDR(Device):
    BYTES_PER_SAMPLE = 2  # RTLSDR device produces 8 bit unsigned IQ data

    def __init__(self, freq, gain, srate, device_number, is_ringbuffer=False):
        super().__init__(0, freq, gain, srate, is_ringbuffer)

        self.success = 0

        self.is_receiving_p = Value('i', 0)
        """
        Shared Value to communicate with the receiving process.

        """

        self.bandwidth_is_adjustable = hasattr(rtlsdr, "set_tuner_bandwidth")   # e.g. not in Manjaro Linux / Ubuntu 14.04
        self._max_frequency = 6e9
        self._max_sample_rate = 3200000
        self._max_frequency = 6e9
        self._max_bandwidth = 3200000
        self._max_gain = 500  # Todo: Consider get_tuner_gains for allowed gains here

        self.device_number = device_number

    def open(self):
        pass  # happens in start rx mode

    def close(self):
        pass  # happens in stop tx mode

    def start_rx_mode(self):
        self.init_recv_buffer()

        self.is_open = True
        self.is_receiving = True
        self.receive_process = Process(target=receive_sync, args=(self.child_data_conn, self.child_ctrl_conn,
                                                                  self.device_number, self.frequency,
                                                                  self.sample_rate, self.gain
                                                                  ))
        self.receive_process.daemon = True
        self._start_read_rcv_buffer_thread()
        self.receive_process.start()

    def stop_rx_mode(self, msg):
        self.is_receiving = False
        self.parent_ctrl_conn.send("stop")

        logger.info("RTLSDR: Stopping RX Mode: " + msg)

        if hasattr(self, "receive_process"):
            self.receive_process.join(0.3)
            if self.receive_process.is_alive():
                logger.warning("RTLSDR: Receive process is still alive, terminating it")
                self.receive_process.terminate()
                self.receive_process.join()
                self.parent_data_conn, self.child_data_conn = Pipe()
                self.parent_ctrl_conn, self.child_ctrl_conn = Pipe()

        if hasattr(self, "read_queue_thread") and self.read_recv_buffer_thread.is_alive():
            try:
                self.read_recv_buffer_thread.join(0.001)
                logger.info("RTLSDR: Joined read_queue_thread")
            except RuntimeError:
                logger.error("RTLSDR: Could not join read_queue_thread")


    def set_device_frequency(self, frequency):
        self.parent_ctrl_conn.send("center_freq:{}".format(int(frequency)))

    def set_device_sample_rate(self, sample_rate):
        self.parent_ctrl_conn.send("sample_rate:{}".format(int(sample_rate)))

    def set_freq_correction(self, ppm):
        ret = rtlsdr.set_freq_correction(int(ppm))
        self.log_retcode(ret, "Set frequency correction")

    def set_offset_tuning(self, on: bool):
        ret = rtlsdr.set_offset_tuning(on)
        self.log_retcode(ret, "Set offset tuning")

    def set_gain_mode(self, manual: bool):
        ret = rtlsdr.set_tuner_gain_mode(manual)
        self.log_retcode(ret, "Set gain mode manual")

    def set_if_gain(self, gain):
        ret = rtlsdr.set_tuner_if_gain(1, int(gain))
        self.log_retcode(ret, "Set IF gain")

    def set_gain(self, gain):
        self.parent_ctrl_conn.send("tuner_gain:{}".format(int(gain)))

    def set_device_gain(self, gain):
        self.set_gain(gain)

    def set_device_bandwidth(self, bandwidth):
        if hasattr(rtlsdr, "set_tuner_bandwidth"):
            self.parent_ctrl_conn.send("tuner_bandwidth:{}".format(int(bandwidth)))
        else:
            logger.warning("Setting the bandwidth is not supported by your RTL-SDR driver version.")

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
