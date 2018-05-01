from multiprocessing import Connection

import pyaudio

from urh.dev.native.Device import Device
from urh.util.Logger import logger


class SoundCard(Device):
    DEVICE_LIB = pyaudio
    ASYNCHRONOUS = False
    DEVICE_METHODS = dict()

    CHUNK_SIZE = 1024
    SAMPLE_RATE = 48000

    pyaudio_handle = None
    pyaudio_stream = None

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
    def receive_sync(cls, data_conn: Connection):
        if cls.pyaudio_stream:
            data_conn.send_bytes(cls.pyaudio_stream.read(cls.CHUNK_SIZE))

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
