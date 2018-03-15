from collections import defaultdict

import numpy as np

from urh.awre.CommonRange import CommonRange


class Histogram(object):
    """
    Create a histogram based on the equalness of vectors
    """

    def __init__(self, vectors, indices=None, normalize=True):
        """

        :type vectors: list of np.ndarray
        :param indices: Indices of vectors for which the Histogram shall be created.
                        This is useful for clustering.
                        If None Histogram will be created over all bitvectors
        :type: list of int
        :param normalize:
        """
        self.__vectors = vectors  # type: list[np.ndarray]
        self.__active_indices = list(range(len(vectors))) if indices is None else indices

        self.__num_values = len(max((self.__vectors[i] for i in self.__active_indices), key=len))

        self.normalize = normalize
        self.data = self.__create_histogram()

    def __create_histogram(self):
        histogram = np.zeros(self.__num_values, dtype=np.float64 if self.normalize else np.uint)
        if self.normalize:
            # 1+2+3+...+len(self.__vectors)-1
            n = (len(self.__active_indices) * (len(self.__active_indices) - 1)) // 2
        else:
            n = 1

        for i in range(0, len(self.__active_indices) - 1):
            index_i = self.__active_indices[i]
            for j in range(i+1, len(self.__active_indices)):
                index_j = self.__active_indices[j]
                bitvector_i, bitvector_j = self.__vectors[index_i], self.__vectors[index_j]
                for k in range(0, min(len(bitvector_i), len(bitvector_j))):
                    if bitvector_i[k] == bitvector_j[k]:
                        histogram[k] += 1 / n
        return histogram

    def __repr__(self):
        return str(self.data.tolist())

    def find_common_ranges(self, alpha=0.95, range_type="bit"):
        """
        Find all common ranges where at least alpha percent of numbers are equal

        :param range_type: on of bit/hex/byte
        :param alpha:
        :return:
        """

        data_indices = np.argwhere(self.data > alpha).flatten()

        if len(data_indices) < 2:
            return []

        result = []
        start, length = None, 0
        for i in range(1, len(data_indices)):
            if start is None:
                start = data_indices[i - 1]
                length = 1

            if data_indices[i] - data_indices[i - 1] == 1:
                length += 1
            else:
                if length >= 2:
                    value, msg_indices = self.__get_value_for_common_range(start, length)
                    result.append(CommonRange(start, length, value, message_indices=msg_indices,
                                              range_type=range_type))

                start, length = None, 0

            if i == len(data_indices) - 1 and length >= 2:
                value, msg_indices = self.__get_value_for_common_range(start, length)
                result.append(CommonRange(start, length, value, message_indices=msg_indices,
                                          range_type=range_type))

        return result

    def __get_value_for_common_range(self, start: int, length: int):
        """
        Get the value for a range of common numbers. This is the value that appears most.

        :param start: Start of the common bit range
        :param length: Length of the common bit range
        :return:
        """
        values = defaultdict(list)
        for i in self.__active_indices:
            vector = self.__vectors[i]
            values[vector[start:start + length].tostring()].append(i)
        value = max(values, key=lambda x: len(x))
        indices = values[value]
        return self.__vectors[indices[0]][start:start + length], set(indices)

    def __vector_to_string(self, data_vector) -> str:
        lut = {i: "{0:x}".format(i) for i in range(16)}
        return "".join(lut[x] if x in lut else " {} ".format(x) for x in data_vector)

    def plot(self):
        import matplotlib.pyplot as plt
        self.subplot_on(plt)
        plt.show()

    def subplot_on(self, plt):
        plt.grid()
        plt.plot(self.data)
        plt.xticks(np.arange(4, len(self.data), 4))
        plt.xlabel("Bit position")
        if self.normalize:
            plt.ylabel("Number common bits (normalized)")
        else:
            plt.ylabel("Number common bits")
        plt.ylim(ymin=0)


if __name__ == "__main__":
    bv1 = np.array([1, 0, 1, 0, 1, 1, 1, 1], dtype=np.int8)
    bv2 = np.array([1, 0, 1, 0, 1, 0, 0, 0], dtype=np.int8)
    bv3 = np.array([1, 0, 1, 0, 1, 1, 1, 1], dtype=np.int8)
    bv4 = np.array([1, 0, 1, 0, 0, 0, 0, 0], dtype=np.int8)
    h = Histogram([bv1, bv2, bv3, bv4])
    h.plot()
