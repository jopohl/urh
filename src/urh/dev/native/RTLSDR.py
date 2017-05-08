import numpy as np

from urh.dev.native.Device import Device

try:
    from urh.dev.native.lib import rtlsdr
except ImportError:
    import urh.dev.native.lib.rtlsdr_fallback as rtlsdr
from urh.util.Logger import logger


class RTLSDR(Device):
    BYTES_PER_SAMPLE = 2  # RTLSDR device produces 8 bit unsigned IQ data
    DEVICE_LIB = rtlsdr
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_RF_GAIN.name: "set_tuner_gain",
        Device.Command.SET_BANDWIDTH.name: "set_tuner_bandwidth",
        Device.Command.SET_FREQUENCY_CORRECTION.name: "set_freq_correction",
        Device.Command.SET_DIRECT_SAMPLING_MODE.name: "set_direct_sampling"
    })

    @staticmethod
    def receive_sync(data_connection, ctrl_connection, device_number: int, center_freq: int, sample_rate: int,
                     bandwidth: int, gain: int, freq_correction: int, direct_sampling_mode: int):
        ret = rtlsdr.open(device_number)
        ctrl_connection.send("OPEN:" + str(ret))

        RTLSDR.process_command((RTLSDR.Command.SET_FREQUENCY.name, center_freq), ctrl_connection, False)
        RTLSDR.process_command((RTLSDR.Command.SET_SAMPLE_RATE.name, sample_rate), ctrl_connection, False)
        if RTLSDR.get_bandwidth_is_adjustable():
            RTLSDR.process_command((RTLSDR.Command.SET_BANDWIDTH.name, bandwidth), ctrl_connection, False)
        RTLSDR.process_command((RTLSDR.Command.SET_FREQUENCY_CORRECTION.name, freq_correction), ctrl_connection, False)
        RTLSDR.process_command((RTLSDR.Command.SET_DIRECT_SAMPLING_MODE.name, direct_sampling_mode), ctrl_connection,
                               False)
        # Gain has to be set last, otherwise it does not get considered by RTL-SDR
        RTLSDR.process_command((RTLSDR.Command.SET_RF_GAIN.name, 10 * gain), ctrl_connection, False)

        ret = rtlsdr.reset_buffer()
        ctrl_connection.send("RESET_BUFFER:" + str(ret))

        exit_requested = False

        while not exit_requested:
            while ctrl_connection.poll():
                result = RTLSDR.process_command(ctrl_connection.recv(), ctrl_connection, False)
                if result == RTLSDR.Command.STOP.name:
                    exit_requested = True
                    break

            if not exit_requested:
                data_connection.send_bytes(rtlsdr.read_sync())

        logger.debug("RTLSDR: closing device")
        ret = rtlsdr.close()
        ctrl_connection.send("CLOSE:" + str(ret))

        data_connection.close()
        ctrl_connection.close()

    def __init__(self, freq, gain, srate, device_number, is_ringbuffer=False):
        super().__init__(center_freq=freq, sample_rate=srate, bandwidth=0,
                         gain=gain, if_gain=1, baseband_gain=1, is_ringbuffer=is_ringbuffer)

        self.success = 0

        self.receive_process_function = RTLSDR.receive_sync

        self.bandwidth_is_adjustable = self.get_bandwidth_is_adjustable() # e.g. not in Manjaro Linux / Ubuntu 14.04

        self.device_number = device_number

    @staticmethod
    def get_bandwidth_is_adjustable():
        return hasattr(rtlsdr, "set_tuner_bandwidth")

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.device_number, self.frequency, self.sample_rate, \
               self.bandwidth, self.gain, self.freq_correction, self.direct_sampling_mode

    def set_device_bandwidth(self, bandwidth):
        if self.bandwidth_is_adjustable:
            super().set_device_bandwidth(bandwidth)
        else:
            logger.warning("Setting the bandwidth is not supported by your RTL-SDR driver version.")

    def set_device_gain(self, gain):
        super().set_device_gain(10 * gain)

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
