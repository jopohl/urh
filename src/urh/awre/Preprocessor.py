import itertools
import math
import os
from collections import defaultdict

import numpy as np

from urh.cythonext import awre_util
from urh.signalprocessing.FieldType import FieldType


class Preprocessor(object):
    """
    This class preprocesses the messages in the following ways
    1) Identify preamble / length of preamble
    2) Identify sync word(s)
    3) Align all given messages on the identified preamble information
    """

    __DEBUG__ = True

    def __init__(self, bitvectors: list, existing_message_types: dict = None):
        self.bitvectors = bitvectors  # type: list[np.ndarray]
        self.existing_message_types = existing_message_types if existing_message_types is not None else dict()

    def preprocess(self) -> (np.ndarray, int):
        raw_preamble_positions = self.get_raw_preamble_positions()
        existing_sync_words = self.__get_existing_sync_words()
        if len(existing_sync_words) == 0:
            sync_words = self.find_possible_syncs(raw_preamble_positions)
        else:
            # NOTE: This does not cover the case if protocol has multiple sync words and not all of them were labeled
            sync_words = existing_sync_words

        preamble_starts = raw_preamble_positions[:, 0]
        preamble_lengths = self.get_preamble_lengths_from_sync_words(sync_words, preamble_starts=preamble_starts)
        sync_len = len(sync_words[0]) if len(sync_words) > 0 else 0
        return preamble_starts, preamble_lengths, sync_len

    def get_preamble_lengths_from_sync_words(self, sync_words: list, preamble_starts: np.ndarray):
        """
        Get the preamble lengths based on the found sync words for all messages.
        If there should be more than one sync word in a message, use the first one.

        :param sync_words:
        :param preamble_starts:
        :return:
        """
        # If there should be varying sync word lengths we need to return an array of sync lengths per message
        assert all(len(sync_word) == len(sync_words[0]) for sync_word in sync_words)

        preamble_lengths = np.zeros(len(self.bitvectors), dtype=int)

        for i, bitvector in enumerate(self.bitvectors):
            bits = "".join(map(str, bitvector))
            indices = sorted(
                bits.find(sync_word) - preamble_starts[i]
                # There must be at least 2 bits preamble
                for sync_word in sync_words if bits.find(sync_word) > 2 + preamble_starts[i]
            )

            if len(indices) == 0:
                preamble_lengths[i] = 0
            elif len(indices) == 1:
                preamble_lengths[i] = indices[0]
            else:
                # consider all indices not more than one byte before first one
                indices = list(filter(lambda x: x < indices[0] + 7, indices))

                # take the smallest index, but prefer a greater one if it is divisible by 8 (or 4)
                index = next((index for index in indices if index % 8 == 0), None)
                if index is None:
                    index = next((index for index in indices if index % 4 == 0), None)
                if index is None:
                    index = indices[0]
                preamble_lengths[i] = index

        return preamble_lengths

    def find_possible_syncs(self, raw_preamble_positions=None):
        difference_matrix = self.get_difference_matrix()
        if raw_preamble_positions is None:
            raw_preamble_positions = self.get_raw_preamble_positions()
        return self.determine_sync_candidates(raw_preamble_positions, difference_matrix, n_gram_length=4)

    @staticmethod
    def merge_possible_sync_words(possible_sync_words: dict, n_gram_length: int):
        """
        Merge possible sync words by looking for common prefixes

        :param possible_sync_words: dict of possible sync words and their frequencies
        :return:
        """
        result = defaultdict(int)
        if len(possible_sync_words) < 2:
            return possible_sync_words.copy()

        for sync1, sync2 in itertools.combinations(possible_sync_words, 2):
            common_prefix = os.path.commonprefix([sync1, sync2])
            if len(common_prefix) > n_gram_length:
                result[common_prefix] += possible_sync_words[sync1] + possible_sync_words[sync2]
            else:
                result[sync1] += possible_sync_words[sync1]
                result[sync2] += possible_sync_words[sync2]
        return result

    def determine_sync_candidates(self,
                                  raw_preamble_positions: np.ndarray,
                                  difference_matrix: np.ndarray,
                                  n_gram_length=4) -> list:
        possible_sync_words = defaultdict(int)

        for i in range(difference_matrix.shape[0]):
            for j in range(i + 1, difference_matrix.shape[1]):
                # position of first difference between message i and j
                sync_end = difference_matrix[i, j]

                if sync_end == 0:
                    continue

                for index, k in itertools.product([i, j], range(2)):
                    start = raw_preamble_positions[index, 0] + raw_preamble_positions[index, k + 1]

                    # We take the next lower multiple of n for the sync len
                    # In doubt, it is better to under estimate the sync len to prevent it from
                    # taking needed values from other fields e.g. leading zeros for a length field
                    sync_len = max(0, self.lower_multiple_of_n(sync_end - start, n_gram_length))

                    sync_word = "".join(map(str, self.bitvectors[index][start:start + sync_len]))

                    if sync_word not in ("", "10", "01"):
                        # Sync word must not be empty or just two bits long and "10" or "01" because
                        # that would be indistinguishable from the preamble

                        if (start + sync_len) % n_gram_length == 0:
                            # if sync end aligns nicely at n gram length give it a larger score
                            possible_sync_words[sync_word] += 1
                        else:
                            possible_sync_words[sync_word] += 0.5

        self.__debug("Possible sync words", possible_sync_words)
        if len(possible_sync_words) == 0:
            return []

        possible_sync_words = self.merge_possible_sync_words(possible_sync_words, n_gram_length)
        self.__debug("Merged sync words", possible_sync_words)

        scores = self.__score_sync_lengths(possible_sync_words)
        estimated_sync_length = max(scores, key=scores.get)

        # Now we look at all possible sync words with this length
        sync_words = {word: frequency for word, frequency in possible_sync_words.items()
                      if len(word) == estimated_sync_length}
        self.__debug("Sync words", sync_words)

        return sorted(sync_words, key=sync_words.get, reverse=True)

    def get_raw_preamble_positions(self) -> np.ndarray:
        """
        Return a 2D numpy array where first column is the start of preamble
        second and third columns are lower and upper bound for preamble length by message, respectively
        """
        result = np.zeros((len(self.bitvectors), 3), dtype=int)

        for i, bitvector in enumerate(self.bitvectors):
            if i in self.existing_message_types:
                preamble_label = self.existing_message_types[i].get_first_label_with_type(FieldType.Function.PREAMBLE)
            else:
                preamble_label = None

            if preamble_label is None:
                start, lower, upper = self.get_raw_preamble_position(bitvector)
            else:
                # If this message is already labeled with a preamble we just use it's values
                start, lower, upper = preamble_label.start, preamble_label.end, preamble_label.end

            result[i, 0] = start
            result[i, 1] = lower - start
            result[i, 2] = upper - start

        return result

    def get_difference_matrix(self) -> np.ndarray:
        """
        Return a matrix of the first difference index between all messages
        :return:
        """
        result = np.zeros((len(self.bitvectors), len(self.bitvectors)), dtype=int)

        for i in range(len(self.bitvectors)):
            for j in range(i + 1, len(self.bitvectors)):
                result[i, j] = awre_util.find_first_difference(self.bitvectors[i], self.bitvectors[j])

        return result

    def __score_sync_lengths(self, possible_sync_words: dict):
        sync_lengths = defaultdict(int)
        for sync_word, score in possible_sync_words.items():
            sync_lengths[len(sync_word)] += score

        self.__debug("Sync lengths", sync_lengths)

        return sync_lengths

    def __get_existing_sync_words(self) -> list:
        result = []
        for i, bitvector in enumerate(self.bitvectors):
            if i in self.existing_message_types:
                sync_label = self.existing_message_types[i].get_first_label_with_type(FieldType.Function.SYNC)
            else:
                sync_label = None

            if sync_label is not None:
                result.append("".join(map(str, bitvector[sync_label.start:sync_label.end])))
        return result

    def __debug(self, *args):
        if self.__DEBUG__:
            print("[PREPROCESSOR]", *args)

    @staticmethod
    def get_next_multiple_of_n(number: int, n: int):
        return n * int(math.ceil(number / n))

    @staticmethod
    def lower_multiple_of_n(number: int, n: int):
        return n * int(math.floor(number / n))

    @staticmethod
    def get_next_lower_multiple_of_two(number: int):
        return number if number % 2 == 0 else number - 1

    @staticmethod
    def get_raw_preamble_position(bitvector: np.ndarray) -> tuple:
        """
        Get the raw preamble length of a message by simply finding the first index of at least two equal bits
        The method ensures that the returned length is a multiple of 2.

        This method returns a tuple representing the upper and lower bound of the preamble because we cannot tell it
        for sure e.g. for sync words 1001 or 0110
        """
        bits = "".join(map(str, bitvector))

        lower = upper = 0

        if len(bits) == 0:
            return lower, upper

        start = -1
        k = 0
        while k < 2 and start < len(bits):
            start += 1

            a = bits[start]
            b = "1" if a == "0" else "0"

            # now we search for the pattern a^n b^m
            try:
                n = bits.index(b, start) - start
                m = bits.index(a, start + n) - n - start
            except ValueError:
                return 0, 0, 0

            preamble_pattern = a * n + b * m
            i = start
            for i in range(start, len(bits), len(preamble_pattern)):
                try:
                    bits.index(preamble_pattern, i, i + len(preamble_pattern))
                except ValueError:
                    break

            lower = upper = start + Preprocessor.lower_multiple_of_n(i + 1 - start, n + m)
            lower -= (n + m)

            k = (upper - start) / (n + m)

        if k > 2:
            return start, lower, upper
        else:
            # no preamble found
            return 0, 0, 0
