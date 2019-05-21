import numpy as np


class IQArray(object):
    def __init__(self, n: int, dtype: np.dtype, minimum: int, maximum: int):
        self.__data = np.zeros(2 * n, dtype)
        self.minimum = minimum
        self.maximum = maximum
        self.__current_index = 0

    @property
    def data(self):
        return self.__data[0:self.__current_index]

    @property
    def real(self):
        return self.__data[0::2]

    @property
    def imag(self):
        return self.__data[1::2]

    @property
    def magnitudes_squared(self):
        return (self.real / self.maximum)**2 + (self.imag / self.maximum)**2

    def reset(self):
        self.__current_index = 0

    def write(self, new_data: np.ndarray):
        if self.__current_index + len(new_data) > len(self.__data):
            raise ValueError("Array is full")

        self.__data[self.__current_index:self.__current_index + len(new_data)] = new_data
        self.__current_index += len(new_data)
