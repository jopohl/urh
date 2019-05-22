import numpy as np


class IQArray(object):
    def __init__(self, n: int, dtype, data: np.ndarray = None):
        if data is None:
            self.__data = np.zeros(2 * n, dtype)
        else:
            self.__data = data

        self.num_samples = len(self.__data) // 2

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.__data[2*item:2*(item+1)]
        elif isinstance(item, slice):
            start = 2 * item.start if item.start is not None else None
            stop = 2 * item.stop if item.stop is not None else None
            step = 2 * item.step if item.step is not None else None
            return self.__data[start:stop:step]

    def __setitem__(self, key, value: np.ndarray):
        if isinstance(key, int):
            if value.dtype == np.complex64:
                self.__data[2*key] = value[0].real
                self.__data[2*key+1] = value[0].imag
            else:
                self.__data[2*key] = value[0]
                self.__data[2*key+1] = value[1]
        elif isinstance(key, slice):
            start = 2 * key.start if key.start is not None else None
            stop = 2 * key.stop if key.stop is not None else None
            if key.step is not None:
                raise NotImplementedError("Step not implemented")

            if value.dtype == np.complex64:
                self.__data[start:stop:2] = value.real
                self.__data[start+1:stop:2] = value.imag
            else:
                self.__data[start:stop] = value

    def __len__(self):
        return len(self.__data) // 2

    @property
    def minimum(self):
        dtype = self.__data.dtype
        if dtype == np.int8:
            return -128
        elif dtype == np.uint8:
            return 0
        elif dtype == np.int16:
            return -32768
        elif dtype == np.uint16:
            return 0
        elif dtype == np.float32 or dtype == np.float64:
            return -1
        else:
            raise ValueError("Unsupported dtype")

    @property
    def maximum(self):
        dtype = self.__data.dtype
        if dtype == np.int8:
            return 127
        elif dtype == np.uint8:
            return 255
        elif dtype == np.int16:
            return 32767
        elif dtype == np.uint16:
            return 65535
        elif dtype == np.float32 or dtype == np.float64:
            return 1
        else:
            raise ValueError("Unsupported dtype")

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

    def as_complex64(self):
        return self.__data.astype(np.float32).view(np.complex64)

    def insert_subarray(self, pos, subarray: np.ndarray):
        self.__data = np.insert(self.__data, pos, subarray)

    @staticmethod
    def from_file(filename: str):
        if filename.endswith(".complex16u"):
            # two 8 bit unsigned integers
            data = np.fromfile(filename, dtype=np.uint8)
            return IQArray(-1, np.uint8, data=data)
        elif filename.endswith(".complex16s") or filename.endswith(".cs8"):
            # two 8 bit signed integers
            data = np.fromfile(filename, dtype=np.int8)
            return IQArray(-1, np.int8, data=data)
        else:
            # Uncompressed
            data = np.fromfile(filename, dtype=np.float32)
            return IQArray(-1, np.float32, data=data)

    @staticmethod
    def from_array(arr: np.ndarray):
        return IQArray(-1, arr.dtype, data=arr)
