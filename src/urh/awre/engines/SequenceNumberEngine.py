import numpy as np

from urh.awre.CommonRange import CommonRange
from urh.awre.engines.Engine import Engine
from urh.cythonext import awre_util


class SequenceNumberEngine(Engine):
    def __init__(self, bitvectors, n_gram_length=8, minimum_score=0.75, already_labeled: list = None):
        """

        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors
        self.n_gram_length = n_gram_length
        self.minimum_score = minimum_score
        if already_labeled is None:
            self.already_labeled_cols = set()
        else:
            self.already_labeled_cols = {e // n_gram_length for rng in already_labeled for e in range(*rng)}

    def find(self):
        if len(self.bitvectors) < 3:
            # We need at least 3 bitvectors to properly find a sequence number
            return []

        diff_matrix = self.create_difference_matrix(self.bitvectors, self.n_gram_length)
        diff_frequencies_by_column = dict()

        for j in range(diff_matrix.shape[1]):
            unique, counts = np.unique(diff_matrix[:, j], return_counts=True)
            diff_frequencies_by_column[j] = dict(zip(unique, counts))

        self._debug("Diff_frequencies_by_column", diff_frequencies_by_column)
        scores_by_column = dict()
        for column, frequencies in diff_frequencies_by_column.items():
            if column not in self.already_labeled_cols:
                scores_by_column[column] = self.calc_score(frequencies)
            else:
                scores_by_column[column] = 0

        self._debug("Scores by column", scores_by_column)
        result = []
        for candidate_column in sorted(scores_by_column, key=scores_by_column.get, reverse=True):
            score = scores_by_column[candidate_column]
            if score < self.minimum_score:
                continue

            most_common_diff = self.get_most_frequent(diff_frequencies_by_column[candidate_column])
            message_indices = np.flatnonzero(
                # get all rows that have the most common difference or zero
                (diff_matrix[:, candidate_column] == most_common_diff) | (diff_matrix[:, candidate_column] == 0)
            )

            # For example, index 1 in diff matrix corresponds to index 1 and 2 of messages
            message_indices = set(message_indices) | set(message_indices + 1)
            values = set()
            for i in message_indices:
                values.add(self.bitvectors[i][
                           candidate_column * self.n_gram_length:candidate_column * self.n_gram_length + self.n_gram_length].tobytes())

            if len(result) > 0 \
                    and result[-1].start == (candidate_column - 1) * self.n_gram_length \
                    and result[-1].message_indices == message_indices:
                # Since the scoring neglects zeros, the score for leading sequence number parts will also be high
                # and match the same indices as the lower parts, therefore we implicitly consider big AND little endian
                # by starting with the lowest index and increase the length of the sequence number as long as
                # message indices match
                result[-1].length += self.n_gram_length
            else:
                result.append(CommonRange(start=candidate_column * self.n_gram_length,
                                          length=self.n_gram_length,
                                          score=score,
                                          field_type="sequence number",
                                          message_indices=message_indices
                                          )
                              )
            result[-1].values.extend(list(values))

        end_result = []

        # Now we expand the sequence number ranges when stuff left of it is constant
        for common_range in result:
            if len(set(common_range.values)) <= 2:
                # At least three different values needed to reliably identify a sequence number
                continue

            rows = np.array(list(common_range.message_indices)[1:]) - 1
            column = (common_range.start // self.n_gram_length) - 1

            while column >= 0 and column not in self.already_labeled_cols and not np.any(diff_matrix[rows, column]):
                # all elements are zero in diff matrix, so we have a constant
                common_range.start -= self.n_gram_length
                common_range.length += self.n_gram_length
                column = (common_range.start // self.n_gram_length) - 1

            end_result.append(common_range)

        return end_result

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
        num_zeros = sum(v for k, v in diff_frequencies.items() if k == 0)
        if num_zeros == total:
            return 0

        try:
            most_frequent = SequenceNumberEngine.get_most_frequent(diff_frequencies)
        except ValueError:
            return 0

        return diff_frequencies[most_frequent] / (total - num_zeros)

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
        return awre_util.create_seq_number_difference_matrix(bitvectors, n_gram_length)
