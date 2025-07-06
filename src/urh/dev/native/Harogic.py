import numpy as np
from multiprocessing.connection import Connection
from collections import OrderedDict
from urh.dev import config
from urh.dev.native.Device import Device
from urh.dev.native.lib import harogic
from urh.util.Logger import logger

class Harogic(Device):
    """
    Native backend for Harogic devices
    """
    DEVICE_LIB = harogic
    ASYNCHRONOUS = False  # We will use the synchronous receive loop

    # Define how commands from URH map to our Cython functions
    DEVICE_METHODS = {
        Device.Command.SET_FREQUENCY.name: "set_frequency",
        # We also map the gain command so it can be changed live too
        Device.Command.SET_RF_GAIN.name: "set_ref_level", 
    }
    
    # We will handle all configuration in configure_and_start_rx()

    @classmethod
    def get_device_list(cls):
        return harogic.get_device_list()

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=0, baseband_gain=0, resume_on_full_receive_buffer=False):
        if gain == -74:
            gain = -10  # Our desired default for Harogic
        super().__init__(center_freq=center_freq,
                         sample_rate=sample_rate,
                         bandwidth=bandwidth,
                         gain=gain,
                         if_gain=if_gain,
                         baseband_gain=baseband_gain,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)

        # Harogic doesn't have adjustable bandwidth in IQS mode, it's tied to sample rate.
        self.bandwidth_is_adjustable = False

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        # device_identifier in URH is the serial number
        # Our Cython wrapper uses the device index, not serial.
        # For simplicity, we'll always use the first device (index 0).
        ret = harogic.open_device(0)
        ctrl_connection.send(f"OPEN:{ret}")
        return ret == 0

    @classmethod
    def shutdown_device(cls, ctrl_connection: Connection, is_tx: bool):
        logger.debug("Harogic: closing device")
        ret = harogic.stop_rx()
        ctrl_connection.send(f"Stop RX:{ret}")
        ret = harogic.close_device()
        ctrl_connection.send(f"CLOSE:{ret}")
        return True

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection, dev_parameters: OrderedDict): # <-- NEW DEFINITION
        # This method is called before the receive loop starts.
        # We now correctly receive the parameters dictionary.
        freq = dev_parameters[Device.Command.SET_FREQUENCY.name]
        srate = dev_parameters[Device.Command.SET_SAMPLE_RATE.name]
        gain = dev_parameters[Device.Command.SET_RF_GAIN.name]
        
        ret = harogic.configure_and_start_rx(freq, srate, gain)
        return ret

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        num_samples, data_bytes = harogic.get_samples()
        if num_samples > 0:
            data_conn.send_bytes(data_bytes)

    @staticmethod
    def bytes_to_iq(buffer) -> np.ndarray:
        # Determine the data type from our Cython helper
        dtype = np.int8 if harogic.get_data_type() == 'int8' else np.int16
        
        # Create a numpy array from the buffer and reshape it to (N, 2) for I and Q
        data = np.frombuffer(buffer, dtype=dtype)
        
        # Normalize the data to be between -1.0 and 1.0
        if dtype == np.int8:
            normalized_data = data.astype(np.float32) / 127.0
        else: # int16
            normalized_data = data.astype(np.float32) / 32767.0
            
        return normalized_data.reshape((-1, 2))