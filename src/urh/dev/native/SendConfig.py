from multiprocessing import Value
from multiprocessing.connection import Connection

class SendConfig(object):
    def __init__(self,  send_buffer, current_sent_index: Value, current_sending_repeat: Value,
                 total_samples: int, sending_repeats: int, continuous: bool = False, data_connection: Connection = None,
                 pack_complex_method: callable = None):
        self.send_buffer = send_buffer
        self.current_sent_index = current_sent_index
        self.current_sending_repeat = current_sending_repeat
        self.total_samples = total_samples
        self.sending_repeats = sending_repeats
        self.continuous = continuous
        self.data_connection = data_connection
        self.pack_complex_method = pack_complex_method

        if self.continuous:
            assert self.data_connection is not None

    def get_data_to_send(self, buffer_length: int):
        try:
            if self.sending_is_finished():
                return b""

            if self.continuous:
                result = self.pack_complex_method(self.data_connection.recv())
            else:
                result = self.send_buffer[
                         self.current_sent_index.value:self.current_sent_index.value + buffer_length]
            self.progress_send_status(len(result))
            return result
        except (BrokenPipeError, EOFError):
            return b""

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
