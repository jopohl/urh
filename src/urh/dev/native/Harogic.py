import numpy as np
from multiprocessing.connection import Connection
from collections import OrderedDict

from urh.dev.native.Device import Device
from urh.dev.native.lib import harogic
from urh.util.Logger import logger


class Harogic(Device):
    DEVICE_LIB = harogic
    ASYNCHRONOUS = False
    DATA_TYPE = np.float32
    DEVICE_METHODS = {
        Device.Command.SET_FREQUENCY.name: "set_frequency",
        Device.Command.SET_RF_GAIN.name: "set_ref_level",
        Device.Command.SET_ANTENNA_INDEX.name: "set_data_format",
        Device.Command.SET_IF_GAIN.name: "set_if_agc",
        Device.Command.SET_BB_GAIN.name: "set_preamp",
    }
    
    # These class-level variables will exist only in the backend process
    _sample_rate = 0
    _skip_factor = 1
    _receive_counter = 0
    # The sample rate above which we start dropping UI updates to prevent freezes
    UI_REFRESH_LIMIT_SPS = 10e6

    @property
    def has_multi_device_support(self):
        return True

    @classmethod
    def get_device_list(cls):
        return harogic.get_device_list()

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=0, baseband_gain=0,
                 resume_on_full_receive_buffer=False):
        if gain == -74: gain = -10
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)
        self.antenna_index = 1
        self.bandwidth_is_adjustable = False

    @property
    def device_parameters(self) -> OrderedDict:
        return OrderedDict([
            (self.Command.SET_ANTENNA_INDEX.name, self.antenna_index),
            (self.Command.SET_FREQUENCY.name, self.frequency),
            (self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
            (self.Command.SET_BANDWIDTH.name, self.bandwidth),
            (self.Command.SET_RF_GAIN.name, self.gain),
            (self.Command.SET_IF_GAIN.name, self.if_gain),
            (self.Command.SET_BB_GAIN.name, self.baseband_gain),
            ("identifier", self.device_serial),
        ])

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier: str):
        ret = harogic.open_device(device_identifier)
        ctrl_connection.send(f"OPEN:{ret}")
        return ret == 0

    @classmethod
    def shutdown_device(cls, ctrl_connection: Connection, is_tx: bool):
        logger.debug("Harogic: closing device")
        ret = harogic.stop_rx(); ctrl_connection.send(f"Stop RX:{ret}")
        ret = harogic.close_device(); ctrl_connection.send(f"CLOSE:{ret}")
        return True

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection, dev_parameters: OrderedDict):
        # This function runs once at the start of the backend process
        freq = dev_parameters[Device.Command.SET_FREQUENCY.name]
        srate = dev_parameters[Device.Command.SET_SAMPLE_RATE.name]
        gain = dev_parameters[Device.Command.SET_RF_GAIN.name]
        if_gain = dev_parameters[Device.Command.SET_IF_GAIN.name]
        bb_gain = dev_parameters[Device.Command.SET_BB_GAIN.name]
        format_index = dev_parameters.get(Device.Command.SET_ANTENNA_INDEX.name, 1)

        # Store sample rate and calculate skip factor to prevent UI overload
        cls._sample_rate = srate
        if cls._sample_rate > cls.UI_REFRESH_LIMIT_SPS:
            cls._skip_factor = int(cls._sample_rate / cls.UI_REFRESH_LIMIT_SPS)
        else:
            cls._skip_factor = 1
        
        ret = harogic.configure_and_start_rx(freq, srate, gain, format_index, if_gain, bb_gain)
        if ret != 0: ctrl_connection.send(f"Harogic backend failed to start with code {ret}")
        return ret

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        # This function runs in a tight loop in the backend
        num_samples, data_bytes = harogic.get_samples()
        
        # FINAL FREEZE FIX: Only send data to the UI periodically.
        # This keeps the pipe from blocking and freezing the app.
        cls._receive_counter += 1
        if num_samples > 0 and (cls._receive_counter % cls._skip_factor == 0):
            data_conn.send_bytes(data_bytes)

    @staticmethod
    def bytes_to_iq(buffer) -> np.ndarray:
        # The backend now sends perfectly formatted interleaved float32 data.
        return np.frombuffer(buffer, dtype=np.float32).reshape((-1, 2))
