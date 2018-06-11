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

    def __init__(self, bitvectors, n_gram_length=8, minimum_score=0.9, expand=True):
        """

        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors
        self.n_gram_length = n_gram_length
        self.expand = expand
        self.minimum_score = minimum_score


    def find(self):
        diff_matrix = self.create_difference_matrix(self.bitvectors, self.n_gram_length)
        diff_frequencies_by_column = dict()

        for j in range(diff_matrix.shape[1]):
            unique, counts = np.unique(diff_matrix[:, j], return_counts=True)
            diff_frequencies_by_column[j] = dict(zip(unique, counts))

        scores_by_column = dict()
        for column, frequencies in diff_frequencies_by_column.items():
            scores_by_column[column] = self.calc_score(frequencies)

        result = []
        for candidate_column in sorted(scores_by_column, key=scores_by_column.get, reverse=True):
            score = scores_by_column[candidate_column]
            if score < self.minimum_score:
                continue

            start = end = candidate_column
            if self.expand:
                # TODO: Consider big endian (go in other direction)
                for i in range(candidate_column - 1, -1, -1):
                    if set(diff_frequencies_by_column[i]) == {0, 1}:
                        # Only 0 and 1 as diff in neighboured column, so it likely belongs to sequence number
                        start = i
                    else:
                        break

            most_common_diff = self.get_most_frequent(diff_frequencies_by_column[candidate_column])
            message_indices = np.flatnonzero(
                # get all rows that have the most common difference or zero
                (diff_matrix[:, candidate_column]) == most_common_diff | (diff_matrix[:, candidate_column] == 0)
            )

            result.append(CommonRange(start=start * self.n_gram_length,
                                      length=(end + 1 - start) * self.n_gram_length,
                                      score=score,
                                      field_type="sequence number",
                                      # e.g. index 1 in diff matrix corresponds to index 1 and 2 of messages
                                      message_indices=set(message_indices) | set(message_indices+1)
                                      )
                          )

        return result

    @staticmethod
    def get_most_frequent(diff_frequencies: dict):
        return max(filter(lambda x: x not in (0, -1), diff_frequencies), key=diff_frequencies.get)

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

        result = np.full((len(bitvectors) - 1, int(math.ceil(max_len / n_gram_length))), -1, dtype=np.long)
        for i in range(1, len(bitvectors)):
            bv1, bv2 = bitvectors[i - 1], bitvectors[i]
            for j in range(0, min(len(bv1), len(bv2)), n_gram_length):
                diff = util.bits_to_number(bv2[j:j + n_gram_length]) - util.bits_to_number(bv1[j:j + n_gram_length])
                result[i - 1, j // n_gram_length] = diff % (2 ** n_gram_length)

        return result
