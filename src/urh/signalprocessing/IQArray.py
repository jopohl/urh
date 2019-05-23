import numpy as np


class IQArray(object):
    def __init__(self, data: np.ndarray, dtype=None, n=None):
        if data is None:
            self.__data = np.zeros((n, 2), dtype, order="C")
        else:
            self.__data = self.convert_array_to_iq(data)

        assert self.__data.dtype not in (np.complex64, np.complex128)

    def __getitem__(self, item):
        return self.__data[item]

    def __setitem__(self, key, value: np.ndarray):
        if isinstance(value, int) or isinstance(value, float):
            self.__data[key] = value
            return

        if isinstance(value, IQArray):
            value = value.data
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

    def __eq__(self, other):
        return np.array_equal(self.data, other.data)

    @property
    def num_samples(self):
        return self.__data.shape[0]

    @property
    def minimum(self):
        return self.min_max_for_dtype(self.__data.dtype)[0]

    @property
    def maximum(self):
        return self.min_max_for_dtype(self.__data.dtype)[1]

    @property
    def data(self):
        return self.__data

    @property
    def real(self):
        return self.__data[:, 0]

    @real.setter
    def real(self, value):
        self.__data[:, 0] = value

    @property
    def imag(self):
        return self.__data[:, 1]

    @imag.setter
    def imag(self, value):
        self.__data[:, 1] = value

    @property
    def magnitudes_squared(self):
        return (self.real / self.maximum)**2 + (self.imag / self.maximum)**2

    @property
    def magnitudes(self):
        return np.sqrt(self.magnitudes_squared)

    def as_complex64(self):
        return self.__data.flatten(order="C").astype(np.float32).view(np.complex64)

    def to_bytes(self):
        return self.__data.tostring()

    def insert_subarray(self, pos, subarray: np.ndarray):
        if subarray.ndim == 1:
            n = len(subarray)
            if subarray.dtype == np.complex64:
                subarray = subarray.view(np.float32).reshape((n, 2), order="C")
            elif subarray.dtype == np.complex128:
                subarray = subarray.view(np.float64).reshape((n, 2), order="C")
            else:
                subarray = subarray.reshape((n//2, 2), order="C")

        self.__data = np.insert(self.__data, pos, subarray, axis=0)

    def apply_mask(self, mask: np.ndarray):
        self.__data = self.__data[mask]

    def tofile(self, filename: str):
        self.__data.tofile(filename)

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

    @staticmethod
    def min_max_for_dtype(dtype) -> tuple:
        if dtype == np.float32 or dtype == np.float64:
            return -1, 1
        else:
            return np.iinfo(dtype).min, np.iinfo(dtype).max

    @staticmethod
    def concatenate(*args):
        return IQArray(data=np.concatenate([arr.data if isinstance(arr, IQArray) else arr for arr in args[0]]))
