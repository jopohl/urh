import threading
import numpy as np

class Device(object):
    def __init__(self, initial_bufsize=8e9, is_ringbuffer=False):
        self.lock = threading.Lock()
        self.byte_buffer = b''

        buf_size = initial_bufsize
        self.is_ringbuffer = is_ringbuffer  # Ringbuffer for Live Sniffing
        self.current_index = 0
        while True:
            try:
                self.data = np.zeros(buf_size, dtype=np.complex64)
                break
            except (MemoryError, ValueError):
                buf_size //= 2

    def callback_recv(self, buffer):
        with self.lock:
            self.byte_buffer += buffer

            r = np.empty(len(self.byte_buffer) // 4, dtype=np.float16)
            i = np.empty(len(self.byte_buffer) // 4, dtype=np.float16)
            c = np.empty(len(self.byte_buffer) // 4, dtype=np.complex64)
            if self.current_index + len(c) >= len(self.data):
                if self.is_ringbuffer:
                    self.current_index = 0
                    if len(c) >= len(self.data):
                        self.stop("Receiving buffer too small.")
                else:
                    self.stop("Receiving Buffer is full.")
                    return

            for j in range(0, len(self.byte_buffer), 4):
                r[j // 4] = np.frombuffer(self.byte_buffer[j:j + 2], dtype=np.float16) / 32767.5
                i[j // 4] = np.frombuffer(self.byte_buffer[j + 2:j + 4], dtype=np.float16) / 32767.5
            # r2 = np.fromstring(buffer[], dtype=np.float16) / 32767.5
            c.real = r
            c.imag = i
            self.data[self.current_index:self.current_index + len(c)] = c
            self.current_index += len(c)
            l = 4*(len(self.byte_buffer)//4)
            self.byte_buffer = self.byte_buffer[l:l+len(self.byte_buffer)%4]

        return 0