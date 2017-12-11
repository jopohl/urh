import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import sdrplay


class SDRPlay(Device):
    DEVICE_LIB = sdrplay
    ASYNCHRONOUS = True
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.success = 0
        self.error_codes = {
            0: "SUCCESS",
            1: "FAIL",
            2: "INVALID PARAMETER",
            3: "OUT OF RANGE",
            4: "GAIN UPDATE ERROR",
            5: "RF UPDATE ERROR",
            6: "FS UPDATE ERROR",
            7: "HARDWARE ERROR",
            8: "ALIASING ERROR",
            9: "ALREADY INITIALIZED",
            10: "NOT INITIALIZED",
            11: "NOT ENABLED",
            12: "HARDWARE VERSION ERROR",
            13: "OUT OF MEMORY ERROR"
        }

    @staticmethod
    def unpack_complex(buffer):
        """
        Conversion from short to float happens in c callback
        :param buffer:
        :param nvalues:
        :return:
        """
        return np.frombuffer(buffer, dtype=np.complex64)
