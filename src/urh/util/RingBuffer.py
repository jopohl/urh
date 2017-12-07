import numpy as np
from multiprocessing import Value, Array


class RingBuffer(object):
    """
    A RingBuffer containing complex values.
    """
    def __init__(self, size: int):
        self.__data = Array("f", 2*size)
        self.size = size
        self.__current_index = Value("L", 0)

    @property
    def current_index(self):
        return self.__current_index.value

    @current_index.setter
    def current_index(self, value):
        self.__current_index.value = value

    @property
    def is_empty(self) -> bool:
        return self.current_index == 0

    @property
    def space_left(self):
        return self.size - self.current_index

    @property
    def data(self):
        return np.frombuffer(self.__data.get_obj(), dtype=np.complex64)

    def __getitem__(self, index):
        return self.data[index]

    def __repr__(self):
        return "RingBuffer " + str(self.data)

    def __increase_current_index_by(self, n: int):
        self.current_index += n
        if self.current_index > self.size:
            self.current_index = self.size

    def clear(self):
        self.current_index = 0

    def will_fit(self, number_values: int) -> bool:
        return number_values <= self.space_left

    def push(self, values: np.ndarray):
        """
        Push values to buffer. If buffer can't store all values a ValueError is raised
        :param values: 
        :return: 
        """
        n = len(values)

        with self.__data.get_lock():
            data = np.frombuffer(self.__data.get_obj(), dtype=np.complex64)
            data[self.current_index:self.current_index+n] = values

        self.__increase_current_index_by(n)

    def pop(self, number: int, ensure_even_length=False, pad_zeros=False) -> np.ndarray:
        """
        Pop number of elements. If there are not enough elements, all remaining elements are returned and the
        buffer is cleared afterwards. If buffer is empty, an empty numpy array is returned.
        """
        if ensure_even_length:
            number -= number % 2

        too_much = number - self.current_index

        if too_much > 0:
            number = self.current_index

        with self.__data.get_lock():
            self.current_index -= number

            if pad_zeros and too_much > 0:
                result = np.zeros(too_much+number, dtype=np.complex64)
                result[0:number] = np.copy(self.data[0:number])
            else:
                result = np.copy(self.data[0:number])

            data = np.frombuffer(self.__data.get_obj(), dtype=np.complex64)
            data[:] = np.roll(data, -number)

        return result
