import numpy as np

from urh.dev.native.Device import Device

try:
    from urh.dev.native.lib import rtlsdr
except ImportError:
    import urh.dev.native.lib.rtlsdr_fallback as rtlsdr
from urh.util.Logger import logger

class RTLSDR(Device):
    BYTES_PER_SAMPLE = 2  # RTLSDR device produces 8 bit unsigned IQ data

    @staticmethod
    def receive_sync(data_connection, ctrl_connection, device_number: int, center_freq: int, sample_rate: int,
                     gain: int):
        ret = rtlsdr.open(device_number)
        ctrl_connection.send("open:" + str(ret))

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
                result = RTLSDR.process_command(ctrl_connection.recv())
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

    @staticmethod
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

    def __init__(self, freq, gain, srate, device_number, is_ringbuffer=False):
        super().__init__(0, freq, gain, srate, is_ringbuffer)

        self.success = 0

        self.receive_process_function = RTLSDR.receive_sync

        self.bandwidth_is_adjustable = hasattr(rtlsdr,
                                               "set_tuner_bandwidth")  # e.g. not in Manjaro Linux / Ubuntu 14.04
        self._max_frequency = 6e9
        self._max_sample_rate = 3200000
        self._max_frequency = 6e9
        self._max_bandwidth = 3200000
        self._max_gain = 500  # Todo: Consider get_tuner_gains for allowed gains here

        self.device_number = device_number

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.device_number, self.frequency, self.sample_rate, self.gain

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
