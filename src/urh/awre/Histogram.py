from collections import defaultdict

import numpy as np

from urh.awre.CommonRange import CommonBitRange


class Histogram(object):
    """
    Create a histogram based on the equalness of bitvectors
    """

    def __init__(self, bitvectors, indices=None, normalize=True):
        """

        :type bitvectors: list of np.ndarray
        :param indices: Indices of bitvectors for which the Histogram shall be created.
                        This is useful for clustering.
                        If None Histogram will be created over all bitvectors
        :type: list of int
        :param normalize:
        """
        self.__bitvectors = bitvectors  # type: list[np.ndarray]
        self.__active_indices = list(range(len(bitvectors))) if indices is None else indices

        self.__num_bits = len(max((self.__bitvectors[i] for i in self.__active_indices), key=len))

        self.normalize = normalize
        self.data = self.__create_histogram()

    def __create_histogram(self):
        histogram = np.zeros(self.__num_bits, dtype=np.float64 if self.normalize else np.uint)
        if self.normalize:
            # 1+2+3+...+len(self.__bitvectors)-1
            n = (len(self.__active_indices) * (len(self.__active_indices) - 1)) // 2
        else:
            n = 1

        for i in range(0, len(self.__active_indices) - 1):
            index_i = self.__active_indices[i]
            for j in range(i+1, len(self.__active_indices)):
                index_j = self.__active_indices[j]
                bitvector_i, bitvector_j = self.__bitvectors[index_i], self.__bitvectors[index_j]
                for k in range(0, min(len(bitvector_i), len(bitvector_j))):
                    if bitvector_i[k] == bitvector_j[k]:
                        histogram[k] += 1 / n
        return histogram

    def __repr__(self):
        return str(self.data.tolist())

    def find_common_ranges(self, alpha=0.95):
        """
        Find all common ranges where at least alpha percent of bits are equal
        :param alpha:
        :return:
        """

        bit_indices = np.argwhere(self.data > alpha).flatten()

        if len(bit_indices) < 2:
            return []

        result = []
        start, length = None, 0
        for i in range(1, len(bit_indices)):
            if start is None:
                start = bit_indices[i - 1]
                length = 1

            if bit_indices[i] - bit_indices[i - 1] == 1:
                length += 1
            else:
                if length >= 2:
                    value, msg_indices = self.__get_value_for_common_range(start, length)
                    result.append(CommonBitRange(start, length, value, message_indices=msg_indices))

                start, length = None, 0

            if i == len(bit_indices) - 1 and length >= 2:
                value, msg_indices = self.__get_value_for_common_range(start, length)
                result.append(CommonBitRange(start, length, value, message_indices=msg_indices))

        return result

    def __get_value_for_common_range(self, start: int, length: int):
        """
        Get the value for a range of common bits. This is the value that appears most.

        :param start: Start of the common bit range
        :param length: Length of the common bit range
        :return:
        """
        values = defaultdict(set)
        for i in self.__active_indices:
            bitvector = self.__bitvectors[i]
            values["".join(map(str, bitvector[start:start + length]))].add(i)
        value = max(values, key=lambda x: len(x))
        return value, values[value]

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
