from urh.dev.native.Device import Device


class LimeSDR(Device):
    BYTES_PER_SAMPLE = 8  # We use dataFmt_t.LMS_FMT_F32 so we have 32 bit floats for I and Q

    @staticmethod
    def lime_receive(data_conn, ctrl_conn, frequency: float, sample_rate: float, bandwidth: float, gain: float):
        pass

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

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, self.gain

    @property
    def send_process_arguments(self):
        return self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, self.gain, \
               self.send_buffer, self._current_sent_sample, self._current_sending_repeat, self.sending_repeats
