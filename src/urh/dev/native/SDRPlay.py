from collections import OrderedDict
from multiprocessing.connection import Connection

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import sdrplay
from urh.util.Logger import logger


class SDRPlay(Device):
    DEVICE_LIB = sdrplay
    ASYNCHRONOUS = True
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS[Device.Command.SET_RF_GAIN.name] = "set_gain"
    DEVICE_METHODS[Device.Command.SET_IF_GAIN.name]["rx"] = "set_if_gain"
    DEVICE_METHODS[Device.Command.SET_ANTENNA_INDEX.name] = "set_antenna"

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
    def device_dict_to_string(d):
        hw_ver = d["hw_version"]
        serial = d["serial"]
        return "RSP {} ({})".format(hw_ver, serial)

    @property
    def device_parameters(self):
        return OrderedDict([(self.Command.SET_ANTENNA_INDEX.name, self.antenna_index),
                            (self.Command.SET_FREQUENCY.name, self.frequency),
                            (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                            (self.Command.SET_BANDWIDTH.name, self.bandwidth),
                            (self.Command.SET_RF_GAIN.name, self.gain),
                            (self.Command.SET_IF_GAIN.name, self.if_gain),
                            ("identifier", self.device_number)])

    @property
    def has_multi_device_support(self):
        return True

    @classmethod
    def get_device_list(cls):
        return [cls.device_dict_to_string(d) for d in sdrplay.get_devices()]

    @classmethod
    def enter_async_receive_mode(cls, data_connection: Connection, ctrl_connection: Connection):
        ret = sdrplay.init_stream(cls.sdrplay_initial_gain, cls.sdrplay_initial_sample_rate, cls.sdrplay_initial_freq,
                                  cls.sdrplay_initial_bandwidth, cls.sdrplay_initial_if_gain, data_connection)

        ctrl_connection.send(
            "Start RX MODE with \n  FREQUENCY={}\n  SAMPLE_RATE={}\n  BANDWIDTH={}\n  GAIN={}\n  IF_GAIN={}:{}".format(
                cls.sdrplay_initial_freq, cls.sdrplay_initial_sample_rate, cls.sdrplay_initial_bandwidth, cls.sdrplay_initial_gain, cls.sdrplay_initial_if_gain, ret))

        return ret

    @classmethod
    def init_device(cls, ctrl_connection: Connection, is_tx: bool, parameters: OrderedDict) -> bool:
        identifier = parameters["identifier"]

        try:
            device_list = sdrplay.get_devices()
            device_number = int(identifier)
            ctrl_connection.send("CONNECTED DEVICES: {}".format(", ".join(map(cls.device_dict_to_string, device_list))))
            ret = sdrplay.set_device_index(device_number)
            ctrl_connection.send("SET DEVICE NUMBER to {}:{}".format(device_number, ret))
        except (TypeError, ValueError) as e:
            logger.exception(e)
            return False

        device_model = device_list[device_number]["hw_version"]
        sdrplay.set_gr_mode_for_dev_model(device_model)
        if device_model == 2:
            antenna = parameters[cls.Command.SET_ANTENNA_INDEX.name]
            cls.process_command((cls.Command.SET_ANTENNA_INDEX.name, antenna), ctrl_connection, is_tx=False)
        else:
            ctrl_connection.send("Skipping antenna selection for RSP1 device")

        cls.sdrplay_initial_freq = parameters[cls.Command.SET_FREQUENCY.name]
        cls.sdrplay_initial_sample_rate = parameters[cls.Command.SET_SAMPLE_RATE.name]
        cls.sdrplay_initial_bandwidth = parameters[cls.Command.SET_BANDWIDTH.name]
        cls.sdrplay_initial_gain = parameters[cls.Command.SET_RF_GAIN.name]
        cls.sdrplay_initial_if_gain = parameters[cls.Command.SET_IF_GAIN.name]
        cls.sdrplay_device_index = identifier
        return True

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx: bool):
        logger.debug("SDRPLAY: closing device")
        ret = sdrplay.close_stream()
        ctrl_connection.send("CLOSE STREAM:" + str(ret))

        if cls.sdrplay_device_index is not None:
            ret = sdrplay.release_device_index()
            ctrl_connection.send("RELEASE DEVICE:" + str(ret))

    @staticmethod
    def unpack_complex(buffer):
        """
        Conversion from short to float happens in c callback
        :param buffer:
        :param nvalues:
        :return:
        """
        return np.frombuffer(buffer, dtype=np.complex64)
