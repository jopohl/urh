import numpy as np
import time

from urh.dev.native.Device import Device
from urh.dev.native.lib import airspy
from urh.util.Logger import logger


class AirSpy(Device):
    BYTES_PER_SAMPLE = 8
    DEVICE_LIB = airspy
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_center_frequency",
    })
    del DEVICE_METHODS[Device.Command.SET_BANDWIDTH.name]

    @staticmethod
    def initialize_airspy(freq, sample_rate, gain, if_gain, baseband_gain, ctrl_conn, is_tx):
        ret = airspy.open()
        ctrl_conn.send("OPEN:" + str(ret))

        if ret != 0:
            return False

        AirSpy.process_command((AirSpy.Command.SET_FREQUENCY.name, freq), ctrl_conn, is_tx)
        AirSpy.process_command((AirSpy.Command.SET_SAMPLE_RATE.name, sample_rate), ctrl_conn, is_tx)
        AirSpy.process_command((AirSpy.Command.SET_RF_GAIN.name, gain), ctrl_conn, is_tx)
        AirSpy.process_command((AirSpy.Command.SET_IF_GAIN.name, if_gain), ctrl_conn, is_tx)
        AirSpy.process_command((AirSpy.Command.SET_BB_GAIN.name, baseband_gain), ctrl_conn, is_tx)

        return True

    @staticmethod
    def shutdown_airspy(ctrl_conn):
        logger.debug("AirSpy: closing device")
        ret = airspy.stop_rx()
        ctrl_conn.send("Stop RX:" + str(ret))

        ret = airspy.close()
        ctrl_conn.send("EXIT:" + str(ret))

        return True

    @staticmethod
    def airspy_receive(data_connection, ctrl_connection, freq, sample_rate, gain, if_gain, baseband_gain):
        if not AirSpy.initialize_airspy(freq, sample_rate, gain, if_gain, baseband_gain, ctrl_connection, is_tx=False):
            return False

        airspy.start_rx(data_connection.send_bytes)

        exit_requested = False

        while not exit_requested:
            time.sleep(0.5)
            while ctrl_connection.poll():
                result = AirSpy.process_command(ctrl_connection.recv(), ctrl_connection, is_tx=False)
                if result == AirSpy.Command.STOP.name:
                    exit_requested = True
                    break

        AirSpy.shutdown_airspy(ctrl_connection)
        data_connection.close()
        ctrl_connection.close()

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1, is_ringbuffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain, is_ringbuffer=is_ringbuffer)
        self.success = 0

        self.bandwidth_is_adjustable = False

        self.receive_process_function = AirSpy.airspy_receive

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.frequency, self.sample_rate, self.gain, self.if_gain, self.baseband_gain

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

