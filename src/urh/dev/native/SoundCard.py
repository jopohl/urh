from collections import OrderedDict
from multiprocessing import Array
from multiprocessing.connection import Connection

import numpy as np
import pyaudio

from urh.dev.native.Device import Device
from urh.util.Logger import logger


class SoundCard(Device):
    DEVICE_LIB = pyaudio
    ASYNCHRONOUS = False
    DEVICE_METHODS = dict()

    CHUNK_SIZE = 1024
    SYNC_TX_CHUNK_SIZE = 2 * CHUNK_SIZE
    CONTINUOUS_TX_CHUNK_SIZE = SYNC_TX_CHUNK_SIZE

    SAMPLE_RATE = 48000

    pyaudio_handle = None
    pyaudio_stream = None

    @classmethod
    def init_device(cls, ctrl_connection: Connection, is_tx: bool, parameters: OrderedDict) -> bool:
        try:
            cls.SAMPLE_RATE = int(parameters[cls.Command.SET_SAMPLE_RATE.name])
        except (KeyError, ValueError):
            pass
        return super().init_device(ctrl_connection, is_tx, parameters)

    @classmethod
    def setup_device(cls, ctrl_connection: Connection, device_identifier):
        ctrl_connection.send("Initializing pyaudio...")
        try:
            cls.pyaudio_handle = pyaudio.PyAudio()
            ctrl_connection.send("Initialized pyaudio")
            return True
        except Exception as e:
            logger.exception(e)
            ctrl_connection.send("Failed to initialize pyaudio")

    @classmethod
    def prepare_sync_receive(cls, ctrl_connection: Connection):
        try:
            cls.pyaudio_stream = cls.pyaudio_handle.open(format=pyaudio.paFloat32,
                                                         channels=2,
                                                         rate=cls.SAMPLE_RATE,
                                                         input=True,
                                                         frames_per_buffer=cls.CHUNK_SIZE)
            ctrl_connection.send("Successfully started pyaudio stream")
            return 0
        except Exception as e:
            logger.exception(e)
            ctrl_connection.send("Failed to start pyaudio stream")

    @classmethod
    def prepare_sync_send(cls, ctrl_connection: Connection):
        try:
            cls.pyaudio_stream = cls.pyaudio_handle.open(format=pyaudio.paFloat32,
                                                         channels=2,
                                                         rate=cls.SAMPLE_RATE,
                                                         frames_per_buffer=cls.CHUNK_SIZE,
                                                         output=True)
            ctrl_connection.send("Successfully started pyaudio stream")
            return 0
        except Exception as e:
            logger.exception(e)
            ctrl_connection.send("Failed to start pyaudio stream")

    @classmethod
    def receive_sync(cls, data_conn: Connection):
        if cls.pyaudio_stream:
            data_conn.send_bytes(cls.pyaudio_stream.read(cls.CHUNK_SIZE))

    @classmethod
    def send_sync(cls, data):
        if cls.pyaudio_stream:
            data_bytes = data.tostring() if isinstance(data, np.ndarray) else bytes(data)
            # pad with zeros if smaller than chunk size
            cls.pyaudio_stream.write(data_bytes.ljust(cls.CHUNK_SIZE*8, b'\0'))

    @classmethod
    def shutdown_device(cls, ctrl_connection, is_tx: bool):
        logger.debug("shutting down pyaudio...")
        try:
            if cls.pyaudio_stream:
                cls.pyaudio_stream.stop_stream()
                cls.pyaudio_stream.close()
            if cls.pyaudio_handle:
                cls.pyaudio_handle.terminate()
            ctrl_connection.send("CLOSE:0")
        except Exception as e:
            logger.exception(e)
            ctrl_connection.send("Failed to shut down pyaudio")

    def __init__(self, sample_rate, resume_on_full_receive_buffer=False):
        super().__init__(center_freq=0, sample_rate=sample_rate, bandwidth=0,
                         gain=1, if_gain=1, baseband_gain=1,
                         resume_on_full_receive_buffer=resume_on_full_receive_buffer)

        self.success = 0
        self.bandwidth_is_adjustable = False

    @property
    def device_parameters(self) -> OrderedDict:
        return OrderedDict([(self.Command.SET_SAMPLE_RATE.name, self.sample_rate),
                            ("identifier", None)])

    @staticmethod
    def unpack_complex(buffer):
        return np.frombuffer(buffer, dtype=np.complex64)

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        arr = Array("f", 2*len(complex_samples), lock=False)
        numpy_view = np.frombuffer(arr, dtype=np.float32)
        numpy_view[:] = complex_samples.view(np.float32)
        return arr
