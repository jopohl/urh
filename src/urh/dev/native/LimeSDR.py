import os
import time

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import limesdr


class LimeSDR(Device):
    FIFO_SIZE = 4000000000
    READ_SAMPLES = 32768
    LIME_TIMEOUT_MS = 10

    BYTES_PER_SAMPLE = 8  # We use dataFmt_t.LMS_FMT_F32 so we have 32 bit floats for I and Q
    DEVICE_LIB = limesdr
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_center_frequency",
        Device.Command.SET_BANDWIDTH.name: "set_lpf_bandwidth",
        Device.Command.SET_RF_GAIN.name: "set_normalized_gain"
    })

    @staticmethod
    def initialize_limesdr(freq, sample_rate, bandwidth, gain, ctrl_conn, is_tx):
        ret = limesdr.open()
        ctrl_conn.send("OPEN:" + str(ret))

        if ret != 0:
            return False

        ret = limesdr.init()
        ctrl_conn.send("INIT:" + str(ret))

        if ret != 0:
            return False

        # TODO Channel 0 currently hardcoded
        limesdr.CHANNEL = 0
        limesdr.IS_TX = is_tx
        limesdr.load_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), "limesdr.ini"))

        LimeSDR.process_command((LimeSDR.Command.SET_FREQUENCY.name, freq), ctrl_conn, is_tx)
        LimeSDR.process_command((LimeSDR.Command.SET_SAMPLE_RATE.name, sample_rate), ctrl_conn, is_tx)
        LimeSDR.process_command((LimeSDR.Command.SET_BANDWIDTH.name, bandwidth), ctrl_conn, is_tx)
        LimeSDR.process_command((LimeSDR.Command.SET_RF_GAIN.name, gain * 0.01), ctrl_conn, is_tx)

        return True

    @staticmethod
    def shutdown_lime_sdr(ctrl_conn):
        ret = limesdr.close()
        ctrl_conn.send("CLOSE:" + str(ret))
        return True

    @staticmethod
    def lime_receive(data_conn, ctrl_conn, frequency: float, sample_rate: float, bandwidth: float, gain: float):
        if not LimeSDR.initialize_limesdr(frequency, sample_rate, bandwidth, gain, ctrl_conn, is_tx=False):
            return False

        exit_requested = False

        limesdr.setup_stream(LimeSDR.FIFO_SIZE)
        limesdr.start_stream()

        while not exit_requested:
            limesdr.recv_stream(data_conn, LimeSDR.READ_SAMPLES, LimeSDR.LIME_TIMEOUT_MS)
            time.sleep(0.1)
            while ctrl_conn.poll():
                result = LimeSDR.process_command(ctrl_conn.recv(), ctrl_conn, is_tx=False)
                if result == LimeSDR.Command.STOP.name:
                    exit_requested = True
                    break

        limesdr.stop_stream()
        limesdr.destroy_stream()
        LimeSDR.shutdown_lime_sdr(ctrl_conn)
        data_conn.close()
        ctrl_conn.close()

    @staticmethod
    def lime_send(ctrl_conn, frequency: float, sample_rate: float, bandwidth: float, gain: float,
                  send_buffer, current_sent_index, current_sending_repeat, sending_repeats):
        pass

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1, is_ringbuffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain, is_ringbuffer=is_ringbuffer)
        self.success = 0

        self.receive_process_function = LimeSDR.lime_receive
        self.send_process_function = LimeSDR.lime_send

    def set_device_gain(self, gain):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_RF_GAIN.name, gain * 0.01))
        except BrokenPipeError:
            pass

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, self.gain

    @property
    def send_process_arguments(self):
        return self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, self.gain, \
               self.send_buffer, self._current_sent_sample, self._current_sending_repeat, self.sending_repeats

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
