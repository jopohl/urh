import numpy as np


class LinearBuffer(object):
    def __init__(self, size):
        self.data = np.zeros(size, dtype=np.complex64)
        self.write_current = 0
        self.read_current = 0
        self.__data_available = 0

    def data_available(self, number):
        return number <= self.__data_available

    def push(self, data):
        np.put(self.data, range(self.write_current, self.write_current+len(data)), data, mode="wrap")
        self.write_current = (self.write_current + len(data)) % len(self.data)
        self.__data_available += len(data)

    def pop(self, number):
        result = self.data[self.read_current:self.read_current+number]
        self.read_current = (self.read_current + number) % len(self.data)
        self.__data_available -= number
        self.__data_available = max(0, self.__data_available)
        return result
