import numpy as np
from multiprocessing import Value, Array

from urh.signalprocessing.IQArray import IQArray


class RingBuffer(object):
    """
    A RingBuffer containing complex values.
    """

    def __init__(self, size: int, dtype=np.float32):
        self.dtype = dtype

        types = {
            np.uint8: "B",
            np.int8: "b",
            np.int16: "h",
            np.uint16: "H",
            np.float32: "f",
            np.float64: "d",
        }
        self.__data = Array(types[self.dtype], 2 * size)

        self.size = size
        self.__left_index = Value("L", 0)
        self.__right_index = Value("L", 0)
        self.__length = Value("L", 0)

    def __len__(self):
        return self.__length.value

    @property
    def left_index(self):
        return self.__left_index.value

    @left_index.setter
    def left_index(self, value):
        self.__left_index.value = value % self.size

    @property
    def right_index(self):
        return self.__right_index.value

    @right_index.setter
    def right_index(self, value):
        self.__right_index.value = value % self.size

    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    @property
    def space_left(self):
        return self.size - len(self)

    @property
    def data(self):
        return np.frombuffer(self.__data.get_obj(), dtype=self.dtype).reshape(
            len(self.__data) // 2, 2
        )

    @property
    def view_data(self):
        """
        Get a representation of the ring buffer for plotting. This is expensive, so it should only be used in frontend
        :return:
        """
        left, right = self.left_index, self.left_index + len(self)
        if left > right:
            left, right = right, left

        data = self.data.flatten()
        return np.concatenate((data[left:right], data[right:], data[:left]))

    def clear(self):
        self.left_index = 0
        self.right_index = 0

    def will_fit(self, number_values: int) -> bool:
        return number_values <= self.space_left

    def push(self, values: IQArray):
        """
        Push values to buffer. If buffer can't store all values a ValueError is raised
        """
        n = len(values)
        if len(self) + n > self.size:
            raise ValueError("Too much data to push to RingBuffer")

        slide_1 = np.s_[self.right_index : min(self.right_index + n, self.size)]
        slide_2 = np.s_[: max(self.right_index + n - self.size, 0)]
        with self.__data.get_lock():
            data = np.frombuffer(self.__data.get_obj(), dtype=self.dtype).reshape(
                len(self.__data) // 2, 2
            )
            data[slide_1] = values[: slide_1.stop - slide_1.start]
            data[slide_2] = values[slide_1.stop - slide_1.start :]
            self.right_index += n

        self.__length.value += n

    def pop(self, number: int, ensure_even_length=False) -> np.ndarray:
        """
        Pop number of elements. If there are not enough elements, all remaining elements are returned and the
        buffer is cleared afterwards. If buffer is empty, an empty numpy array is returned.

        If number is -1 (or any other value below zero) than complete buffer is returned
        """
        if ensure_even_length:
            number -= number % 2

        if len(self) == 0 or number == 0:
            return np.array([], dtype=self.dtype)

        if number < 0:
            # take everything
            number = len(self)
        else:
            number = min(number, len(self))

        with self.__data.get_lock():
            result = np.ones(2 * number, dtype=self.dtype).reshape(number, 2)
            data = np.frombuffer(self.__data.get_obj(), dtype=self.dtype).reshape(
                len(self.__data) // 2, 2
            )

            if self.left_index + number > len(data):
                end = len(data) - self.left_index
            else:
                end = number

            result[:end] = data[self.left_index : self.left_index + end]
            if end < number:
                result[end:] = data[: number - end]

        self.left_index += number
        self.__length.value -= number

        return result
