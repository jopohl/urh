import numpy as np


class RingBuffer(object):
    def __init__(self, size: int, dtype=np.complex64):
        self.__data = np.zeros(size, dtype=dtype)
        self.size = size
        self.current_index = 0

    @property
    def is_empty(self) -> bool:
        return self.current_index == 0

    @property
    def is_full(self) -> bool:
        return self.current_index == self.size

    @property
    def space_left(self):
        return self.size - self.current_index

    def __getitem__(self, index):
        return self.__data[index]

    def __repr__(self):
        return "RingBuffer " + str(self.__data)

    def __increase_current_index_by(self, n: int):
        if not self.is_full:
            self.current_index += n
            if self.current_index > self.size:
                self.current_index = self.size

    def will_fit(self, number_values: int) -> bool:
        return number_values <= self.space_left

    def push(self, values: np.ndarray):
        """
        Push values to buffer. If buffer can't store all values a ValueError is raised
        :param values: 
        :return: 
        """
        n = len(values)
        self.__data = np.roll(self.__data, n)
        self.__data[0:n] = values

        self.__increase_current_index_by(n)

    def pop(self, number: int) -> np.ndarray:
        """
        Pop number of elements. If there are not enough elements, all remaining elements are returned and the
        buffer is cleared afterwards. If buffer is empty, an empty numpy array is returned.
        """
        if number > self.current_index:
            number = self.current_index

        result = self.__data[self.current_index-number:self.current_index]
        self.current_index -= number
        return result
