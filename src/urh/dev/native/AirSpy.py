import numpy as np
import time

from urh.dev.native.Device import Device
from urh.dev.native.lib import airspy
from urh.util.Logger import logger
from multiprocessing.connection import Connection


class AirSpy(Device):
    DEVICE_LIB = airspy
    ASYNCHRONOUS = True
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_center_frequency",
    })
    del DEVICE_METHODS[Device.Command.SET_BANDWIDTH.name]

    DATA_TYPE = np.float32

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ret = airspy.open()
        ctrl_connection.send("OPEN:" + str(ret))
        return ret == 0

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx=False):
        logger.debug("AirSpy: closing device")
        ret = airspy.stop_rx()
        ctrl_connection.send("Stop RX:" + str(ret))

        ret = airspy.close()
        ctrl_connection.send("EXIT:" + str(ret))

        return True

    @classmethod
    def enter_async_receive_mode(cls, data_connection: Connection, ctrl_connection: Connection):
        ret = airspy.start_rx(data_connection.send_bytes)
        ctrl_connection.send("Start RX MODE:" + str(ret))
        return ret

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1,
                 resume_on_full_receive_buffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.success = 0

        self.bandwidth_is_adjustable = False

    @staticmethod
    def bytes_to_iq(buffer) -> np.ndarray:
        return np.frombuffer(buffer, dtype=np.float32).reshape((-1, 2), order="C")
