import math

import numpy as np

from urh.awre.CommonRange import CommonRange
from urh.awre.engines.Engine import Engine
from urh.util import util


class SequenceNumberEngine(Engine):
    """
    Current constraint: This class works only for messages of the same message type.
    Therefore, this engine should run AFTER message type inferring.

    """

    def __init__(self, bitvectors):
        """

        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors

    def find(self, n_gram_length=8, expand=True):
        diff_matrix = self.create_difference_matrix(self.bitvectors, n_gram_length)
        diff_frequencies_by_column = dict()

        for j in range(diff_matrix.shape[1]):
            unique, counts = np.unique(diff_matrix[:, j], return_counts=True)
            diff_frequencies_by_column[j] = dict(zip(unique, counts))

        scores_by_column = dict()
        for column, frequencies in diff_frequencies_by_column.items():
            scores_by_column[column] = self.calc_score(frequencies)

        candidate_column = max(scores_by_column, key=scores_by_column.get)
        result = [candidate_column]
        if expand:
            for i in range(candidate_column - 1, -1, -1):
                if set(diff_frequencies_by_column[i]) == {0, 1}:
                    # Only 0 and 1 as diff in neighboured column, so it likely belongs to sequence number
                    result.insert(0, i)
                else:
                    break

        return CommonRange(result[0] * n_gram_length, (result[-1] + 1 - result[0]) * n_gram_length,
                           score=scores_by_column[candidate_column], field_type="sequence number",
                           message_indices=list(range(len(self.bitvectors))))

    @staticmethod
    def get_most_frequent(diff_frequencies: dict):
        return max(filter(lambda x: x != 0, diff_frequencies), key=diff_frequencies.get)

    @staticmethod
    def calc_score(diff_frequencies: dict) -> float:
        """
        Calculate the score based on the distribution of differences
          1. high if one constant (!= zero) dominates
          2. Other constants (!= zero) should lower the score, zero means sequence number stays same for some messages

        :param diff_frequencies: Frequencies of decimal differences between columns of subsequent messages
                                 e.g. {-255: 3, 1: 1020} means -255 appeared 3 times and 1 appeared 1020 times
        :return: a score between 0 and 1
        """
        total = sum(diff_frequencies.values())

        try:
            most_frequent = SequenceNumberEngine.get_most_frequent(diff_frequencies)
        except ValueError:
            return 0

        return diff_frequencies[most_frequent] / total

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

        result = np.zeros((len(bitvectors) - 1, int(math.ceil(max_len / n_gram_length))), dtype=np.long)
        for i in range(1, len(bitvectors)):
            bv1, bv2 = bitvectors[i - 1], bitvectors[i]
            for j in range(0, max(len(bv1), len(bv2)), n_gram_length):
                diff = util.bits_to_number(bv2[j:j + n_gram_length]) - util.bits_to_number(bv1[j:j + n_gram_length])
                result[i - 1, j // n_gram_length] = diff % (2 ** n_gram_length)

        return result
