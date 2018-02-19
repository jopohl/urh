from multiprocessing import Value

import numpy as np

from urh.util.RingBuffer import RingBuffer


class SendConfig(object):
    def __init__(self, send_buffer, current_sent_index: Value, current_sending_repeat: Value,
                 total_samples: int, sending_repeats: int, continuous: bool = False,
                 pack_complex_method: callable = None, continuous_send_ring_buffer: RingBuffer = None):
        self.send_buffer = send_buffer
        self.current_sent_index = current_sent_index
        self.current_sending_repeat = current_sending_repeat
        self.total_samples = total_samples
        self.sending_repeats = sending_repeats
        self.continuous = continuous
        self.pack_complex_method = pack_complex_method
        self.continuous_send_ring_buffer = continuous_send_ring_buffer

    def get_data_to_send(self, buffer_length: int):
        try:
            if self.sending_is_finished():
                return np.zeros(1, dtype=self.send_buffer._type_._type_)

            if self.continuous:
                result = self.pack_complex_method(self.continuous_send_ring_buffer.pop(buffer_length // 2))
                if len(result) == 0:
                    # avoid empty arrays which will not work with cython API
                    return np.zeros(1, dtype=self.send_buffer._type_._type_)
            else:
                index = self.current_sent_index.value
                np_view = np.frombuffer(self.send_buffer, dtype=self.send_buffer._type_._type_)
                result = np_view[index:index + buffer_length]

            self.progress_send_status(len(result))
            return result
        except (BrokenPipeError, EOFError):
            return np.zeros(1, dtype=self.send_buffer._type_._type_)

    def sending_is_finished(self):
        if self.sending_repeats == 0:  # 0 = infinity
            return False

        return self.current_sending_repeat.value >= self.sending_repeats \
               and self.current_sent_index.value >= self.total_samples

    def progress_send_status(self, buffer_length: int):
        self.current_sent_index.value += buffer_length
        if self.current_sent_index.value >= self.total_samples - 1:
            self.current_sending_repeat.value += 1
            if self.current_sending_repeat.value < self.sending_repeats or self.sending_repeats == 0:  # 0 = infinity
                self.current_sent_index.value = 0
            else:
                self.current_sent_index.value = self.total_samples
