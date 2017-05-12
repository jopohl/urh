import numpy as np
import time

from urh.dev.native.Device import Device
from urh.dev.native.lib import airspy
from urh.util.Logger import logger
from multiprocessing.connection import Connection


class AirSpy(Device):
    BYTES_PER_SAMPLE = 8
    DEVICE_LIB = airspy
    ASYNCHRONOUS = True
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_center_frequency",
    })
    del DEVICE_METHODS[Device.Command.SET_BANDWIDTH.name]

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = airspy.open()
        ctrl_connection.send("OPEN:" + str(ret))
        return ret == 0

    @classmethod
    def shutdown_device(cls, ctrl_connection):
        logger.debug("AirSpy: closing device")
        ret = airspy.stop_rx()
        ctrl_connection.send("Stop RX:" + str(ret))

        ret = airspy.close()
        ctrl_connection.send("EXIT:" + str(ret))

        return True

    @classmethod
    def enter_async_receive_mode(cls, data_connection: Connection):
        airspy.start_rx(data_connection.send_bytes)

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.success = 0

        self.bandwidth_is_adjustable = False

    @staticmethod
    def unpack_complex(buffer, nvalues: int):
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.float32), ('i', np.float32)])
        result.real = unpacked["r"]
        result.imag = unpacked["i"]
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        assert complex_samples.dtype == np.complex64
        # tostring() is a compatibility (numpy<1.9) alias for tobytes(). Despite its name it returns bytes not strings.
        return complex_samples.view(np.float32).tostring()
