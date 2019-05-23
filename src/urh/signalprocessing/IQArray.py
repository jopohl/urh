import numpy as np


class IQArray(object):
    def __init__(self, data: np.ndarray, dtype=None, n=None):
        if data is None:
            self.__data = np.zeros((n, 2), dtype, order="C")
        else:
            self.__data = self.convert_array_to_iq(data)

    def __getitem__(self, item):
        return self.__data[item]

    def __setitem__(self, key, value: np.ndarray):
        if value.dtype == np.complex64 or value.dtype == np.complex128:
            self.real[key] = value.real
            self.imag[key] = value.imag
        else:
            if value.ndim == 2:
                self.__data[key] = value
            else:
                self.__data[key] = value.reshape(len(value)//2, 2)

    def __len__(self):
        return len(self.__data)

    @property
    def num_samples(self):
        return self.__data.shape[0]

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
        return self.__data[:, 0]

    @property
    def imag(self):
        return self.__data[:, 1]

    @property
    def magnitudes_squared(self):
        return (self.real / self.maximum)**2 + (self.imag / self.maximum)**2

    @property
    def magnitudes(self):
        return np.sqrt(self.magnitudes_squared)

    def as_complex64(self):
        return self.__data.flatten(order="C").astype(np.float32).view(np.complex64)

    def insert_subarray(self, pos, subarray: np.ndarray):
        self.__data = np.insert(self.__data, pos, subarray)

    @staticmethod
    def from_file(filename: str):
        if filename.endswith(".complex16u"):
            # two 8 bit unsigned integers
            data = np.fromfile(filename, dtype=np.uint8)
            return IQArray(data=data)
        elif filename.endswith(".complex16s") or filename.endswith(".cs8"):
            # two 8 bit signed integers
            data = np.fromfile(filename, dtype=np.int8)
            return IQArray(data=data)
        else:
            # Uncompressed
            data = np.fromfile(filename, dtype=np.float32)
            return IQArray(data=data)

    @staticmethod
    def convert_array_to_iq(arr: np.ndarray):
        if arr.ndim == 1:
            if arr.dtype == np.complex64:
                arr = arr.view(np.float32)
            elif arr.dtype == np.complex128:
                arr = arr.view(np.float64)
            return arr.reshape((len(arr) // 2, 2), order="C")
        elif arr.ndim == 2:
            return arr
        else:
            raise ValueError("Too many dimensions")
