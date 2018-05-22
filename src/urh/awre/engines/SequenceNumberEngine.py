import math

import numpy as np

from urh.awre.engines.Engine import Engine
from urh.util import util


class SequenceNumberEngine(Engine):
    def __init__(self, bitvectors):
        """

        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors

    def find(self, n_gram_length=8, minimum_score=0.1):
        diff_matrix = self.create_difference_matrix(self.bitvectors, n_gram_length)
        vec = diff_matrix[:, 1]
        print(np.min(vec), np.max(vec), np.std(vec))


    @staticmethod
    def create_difference_matrix(bitvectors, n_gram_length: int):
        """
        Create the difference matrix e.g.
        10 20 0
        1  2  3
        4  5  6

        means first eight bits of messages 1 and 2 (row 1) differ by 10 if they are considered as decimal number

        :type bitvectors: list of np.ndarray
        :type n_gram_length: int
        :rtype: np.ndarray
        """
        max_len = len(max(bitvectors, key=len))

        result = np.zeros((len(bitvectors)-1, int(math.ceil(max_len / n_gram_length))), dtype=np.long)
        for i in range(1, len(bitvectors)):
            bv1, bv2 = bitvectors[i-1], bitvectors[i]
            for j in range(0, max(len(bv1), len(bv2)), n_gram_length):
                result[i-1, j//n_gram_length] = util.bits_to_number(bv2[j:j+n_gram_length]) - util.bits_to_number(bv1[j:j+n_gram_length])

        return result
