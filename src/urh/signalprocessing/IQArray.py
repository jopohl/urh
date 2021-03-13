import os
import tarfile
import tempfile
import wave

import numpy as np


class IQArray(object):
    def __init__(self, data: np.ndarray, dtype=None, n=None, skip_conversion=False):
        if data is None:
            self.__data = np.zeros((n, 2), dtype, order="C")
        else:
            if skip_conversion:
                self.__data = data
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
                self.__data[key] = value.reshape((-1, 2), order="C")

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
        return self.real**2.0 + self.imag**2.0

    @property
    def magnitudes(self):
        return np.sqrt(self.magnitudes_squared)

    @property
    def magnitudes_normalized(self):
        return self.magnitudes / np.sqrt(self.maximum**2.0 + self.minimum**2.0)

    @property
    def dtype(self):
        return self.__data.dtype

    def as_complex64(self):
        return self.convert_to(np.float32).flatten(order="C").view(np.complex64)

    def to_bytes(self):
        return self.__data.tostring()

    def subarray(self, start=None, stop=None, step=None):
        return IQArray(self[start:stop:step])

    def insert_subarray(self, pos, subarray: np.ndarray):
        if subarray.ndim == 1:
            if subarray.dtype == np.complex64:
                subarray = subarray.view(np.float32).reshape((-1, 2), order="C")
            elif subarray.dtype == np.complex128:
                subarray = subarray.view(np.float64).reshape((-1, 2), order="C")
            else:
                subarray = subarray.reshape((-1, 2), order="C")

        self.__data = np.insert(self.__data, pos, subarray, axis=0)

    def apply_mask(self, mask: np.ndarray):
        self.__data = self.__data[mask]

    def tofile(self, filename: str):
        if filename.endswith(".complex16u") or filename.endswith(".cu8"):
            self.convert_to(np.uint8).tofile(filename)
        elif filename.endswith(".complex16s") or filename.endswith(".cs8"):
            self.convert_to(np.int8).tofile(filename)
        elif filename.endswith(".complex32u") or filename.endswith(".cu16"):
            self.convert_to(np.uint16).tofile(filename)
        elif filename.endswith(".complex32s") or filename.endswith(".cs16"):
            self.convert_to(np.int16).tofile(filename)
        else:
            self.convert_to(np.float32).tofile(filename)

    def convert_to(self, target_dtype) -> np.ndarray:
        if target_dtype == self.__data.dtype:
            return self.__data

        if self.__data.dtype == np.uint8:
            if target_dtype == np.int8:
                return np.add(self.__data, -128, dtype=np.int8, casting="unsafe")
            elif target_dtype == np.int16:
                return np.add(self.__data, -128, dtype=np.int16, casting="unsafe") << 8
            elif target_dtype == np.uint16:
                return self.__data.astype(np.uint16) << 8
            elif target_dtype == np.float32:
                return np.add(np.multiply(self.__data, 1/128, dtype=np.float32), -1.0, dtype=np.float32)

        if self.__data.dtype == np.int8:
            if target_dtype == np.uint8:
                return np.add(self.__data, 128, dtype=np.uint8, casting="unsafe")
            elif target_dtype == np.int16:
                return self.__data.astype(np.int16) << 8
            elif target_dtype == np.uint16:
                return np.add(self.__data, 128, dtype=np.uint16, casting="unsafe") << 8
            elif target_dtype == np.float32:
                return np.multiply(self.__data, 1/128, dtype=np.float32)

        if self.__data.dtype == np.uint16:
            if target_dtype == np.int8:
                return (np.add(self.__data, -32768, dtype=np.int16, casting="unsafe") >> 8).astype(np.int8)
            elif target_dtype == np.uint8:
                return (self.__data >> 8).astype(np.uint8)
            elif target_dtype == np.int16:
                return np.add(self.__data, -32768, dtype=np.int16, casting="unsafe")
            elif target_dtype == np.float32:
                return np.add(np.multiply(self.__data, 1/32768, dtype=np.float32), -1.0, dtype=np.float32)

        if self.__data.dtype == np.int16:
            if target_dtype == np.int8:
                return (self.__data >> 8).astype(np.int8)
            elif target_dtype == np.uint8:
                return (np.add(self.__data, 32768, dtype=np.uint16, casting="unsafe") >> 8).astype(np.uint8)
            elif target_dtype == np.uint16:
                return np.add(self.__data, 32768, dtype=np.uint16, casting="unsafe")
            elif target_dtype == np.float32:
                return np.multiply(self.__data, 1/32768, dtype=np.float32)

        if self.__data.dtype == np.float32:
            if target_dtype == np.int8:
                return np.multiply(self.__data, 127, dtype=np.float32).astype(np.int8)
            elif target_dtype == np.uint8:
                return np.multiply(np.add(self.__data, 1.0, dtype=np.float32), 127, dtype=np.float32).astype(np.uint8)
            elif target_dtype == np.int16:
                return np.multiply(self.__data, 32767, dtype=np.float32).astype(np.int16)
            elif target_dtype == np.uint16:
                return np.multiply(np.add(self.__data, 1.0, dtype=np.float32), 32767, dtype=np.float32).astype(np.uint16)

        if target_dtype not in (np.uint8, np.int8, np.uint16, np.int16, np.float32):
            raise ValueError("Data type {} not supported".format(target_dtype))

        raise NotImplementedError("Conversion from {} to {} not supported", self.__data.dtype, target_dtype)

    @staticmethod
    def from_file(filename: str):
        if filename.endswith(".complex16u") or filename.endswith(".cu8"):
            # two 8 bit unsigned integers
            return IQArray(IQArray(data=np.fromfile(filename, dtype=np.uint8)).convert_to(np.int8))
        elif filename.endswith(".complex16s") or filename.endswith(".cs8"):
            # two 8 bit signed integers
            return IQArray(data=np.fromfile(filename, dtype=np.int8))
        elif filename.endswith(".complex32u") or filename.endswith(".cu16"):
            # two 16 bit unsigned integers
            return IQArray(IQArray(data=np.fromfile(filename, dtype=np.uint16)).convert_to(np.int16))
        elif filename.endswith(".complex32s") or filename.endswith(".cs16"):
            # two 16 bit signed integers
            return IQArray(data=np.fromfile(filename, dtype=np.int16))
        else:
            return IQArray(data=np.fromfile(filename, dtype=np.float32))

    @staticmethod
    def convert_array_to_iq(arr: np.ndarray) -> np.ndarray:
        if arr.ndim == 1:
            if arr.dtype == np.complex64:
                arr = arr.view(np.float32)
            elif arr.dtype == np.complex128:
                arr = arr.view(np.float64)
            if len(arr) % 2 == 0:
                return arr.reshape((-1, 2), order="C")
            else: # ignore the last half sample to avoid a conversion error
                return arr[:-1].reshape((-1, 2), order="C")
        elif arr.ndim == 2:
            return arr
        else:
            raise ValueError("Too many dimensions")

    @staticmethod
    def min_max_for_dtype(dtype) -> tuple:
        if dtype in (np.float32, np.float64, np.complex64, np.complex128):
            return -1, 1
        else:
            return np.iinfo(dtype).min, np.iinfo(dtype).max

    @staticmethod
    def concatenate(*args):
        return IQArray(data=np.concatenate([arr.data if isinstance(arr, IQArray) else arr for arr in args[0]]))

    def save_compressed(self, filename):
        with tarfile.open(filename, 'w:bz2') as tar_write:
            tmp_name = tempfile.mkstemp()[1]
            self.tofile(tmp_name)
            tar_write.add(tmp_name)
            os.remove(tmp_name)

    def export_to_wav(self, filename, num_channels, sample_rate):
        f = wave.open(filename, "w")
        f.setnchannels(num_channels)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(self.convert_to(np.int16))
        f.close()
