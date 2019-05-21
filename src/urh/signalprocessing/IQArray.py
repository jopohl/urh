import numpy as np


class IQArray(object):
    def __init__(self, n: int, dtype, minimum: int, maximum: int, data: np.ndarray = None):
        if data is None:
            self.__data = np.zeros(2 * n, dtype)
        else:
            self.__data = data

        self.minimum = minimum
        self.maximum = maximum
        self.num_samples = len(self.__data) // 2

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.__data[2*item:2*(item+1)]
        elif isinstance(item, slice):
            start = 2 * item.start if item.start is not None else None
            stop = 2 * item.stop if item.stop is not None else None
            step = 2 * item.step if item.step is not None else None
            return self.__data[start:stop:step]

    @property
    def data(self):
        return self.__data

    @property
    def real(self):
        return self.__data[0::2]

    @property
    def imag(self):
        return self.__data[1::2]

    @property
    def magnitudes_squared(self):
        return (self.real / self.maximum)**2 + (self.imag / self.maximum)**2

    @property
    def magnitudes(self):
        return np.sqrt(self.magnitudes_squared)

    @staticmethod
    def from_file(filename: str):
        if filename.endswith(".complex16u"):
            # two 8 bit unsigned integers
            data = np.fromfile(filename, dtype=np.uint8)
            return IQArray(-1, np.uint8, minimum=0, maximum=255, data=data)
        elif filename.endswith(".complex16s") or filename.endswith(".cs8"):
            # two 8 bit signed integers
            data = np.fromfile(filename, dtype=np.int8)
            return IQArray(-1, np.int8, minimum=-128, maximum=127, data=data)
        else:
            # Uncompressed
            data = np.fromfile(filename, dtype=np.float32)
            return IQArray(-1, np.float32, minimum=-1, maximum=1, data=data)

    @staticmethod
    def from_array(arr: np.ndarray, minimum=-1, maximum=1):
        return IQArray(-1, arr.dtype, minimum=minimum, maximum=maximum, data=arr)
