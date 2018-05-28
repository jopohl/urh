import math

import numpy as np

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

    def find(self, n_gram_length=8, minimum_score=0.1):
        diff_matrix = self.create_difference_matrix(self.bitvectors, n_gram_length)
        diff_frequencies_by_column = dict()

        for j in range(diff_matrix.shape[1]):
            print(diff_matrix[:, j])
            unique, counts = np.unique(diff_matrix[:, j], return_counts=True)
            diff_frequencies_by_column[j] = dict(zip(unique, counts))

        stage_1_scores_by_column = dict()
        for column, frequencies in diff_frequencies_by_column.items():
            stage_1_scores_by_column[column] = self.calc_stage_1_score(frequencies)

        print(diff_frequencies_by_column)
        print(stage_1_scores_by_column)

        candidates = dict(filter(lambda d: d[1] > 0.9, stage_1_scores_by_column.items()))
        self.calc_combined_score(candidates, diff_frequencies_by_column)

        print(candidates)

        # Find column with highest frequency of constant != zero
        # If there are also negative values in this column, check for matching frequencies in neighbour columns
        # {0: {0: 1020, 1: 3}, 1: {-255: 3, 1: 1020}, 2: {0: 1023}, 3: {0: 1023}}

    @staticmethod
    def calc_combined_score(candidates: dict, diff_frequencies_by_column: dict):
        """
        if negative number and frequency of this number equals frequency of constants of neighbour column

        :param candidates:
        :param diff_frequencies_by_column:
        :return:
        """
        result = dict()
        for column in candidates:
            diff_freq = diff_frequencies_by_column[column]
            negatives = dict(filter(lambda d: d[0] < 0, diff_freq.items()))
            positives = dict(filter(lambda d: d[0] > 0, diff_freq.items()))

            # Now we look to left and right and see if there is a correlation


            print(negatives)
            print(positives)

        return result

    @staticmethod
    def calc_stage_1_score(diff_frequencies: dict) -> float:
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
            most_frequent = max(filter(lambda x: x != 0, diff_frequencies), key=diff_frequencies.get)
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

        result = np.zeros((len(bitvectors)-1, int(math.ceil(max_len / n_gram_length))), dtype=np.long)
        for i in range(1, len(bitvectors)):
            bv1, bv2 = bitvectors[i-1], bitvectors[i]
            for j in range(0, max(len(bv1), len(bv2)), n_gram_length):
                result[i-1, j//n_gram_length] = util.bits_to_number(bv2[j:j+n_gram_length]) - util.bits_to_number(bv1[j:j+n_gram_length])

        return result
