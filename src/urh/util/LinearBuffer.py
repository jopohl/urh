import numpy as np


class LinearBuffer(object):
    def __init__(self, size):
        self.data = np.zeros(size, dtype=np.complex64)
        self.write_current = 0
        self.read_current = 0

    def data_available(self, number):
        return self.write_current >= ((self.read_current + number) % len(self.data))

    def push(self, data):
        np.put(self.data, range(self.write_current, self.write_current+len(data)), data, mode="wrap")
        self.write_current = (self.write_current + len(data)) % len(self.data)

    def pop(self, number):
        result = self.data[self.read_current:self.read_current+number]
        self.read_current = (self.read_current + number) % len(self.data)
        return result
