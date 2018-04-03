import itertools
import math
from collections import defaultdict

import array
from pprint import pprint

import numpy as np

from urh.cythonext import awre_util
from urh.signalprocessing.Message import Message


class Preprocessor(object):
    """
    This class preprocesses the messages in the following ways
    1) Identify preamble / length of preamble
    2) Identify sync word(s)
    3) Align all given messages on the identified preamble information
    """

    __DEBUG__ = True

    def __init__(self, messages: list):
        self.messages = messages  # type: list[Message]

    def preprocess(self) -> (np.ndarray, int):
        raw_preamble_positions = self.get_raw_preamble_positions()
        sync_words = self.find_possible_syncs(raw_preamble_positions)
        preamble_starts = raw_preamble_positions[:, 0]
        preamble_lengths = self.get_preamble_lengths_from_sync_words(sync_words, preamble_starts=preamble_starts)
        return preamble_starts, preamble_lengths, len(sync_words[0])

    def get_preamble_lengths_from_sync_words(self, sync_words: list, preamble_starts: np.ndarray):
        # If there should be varying sync word lengths we need to return an array of sync lengths per message
        assert all(len(sync_word) == len(sync_words[0]) for sync_word in sync_words)

        preamble_lengths = np.zeros(len(self.messages), dtype=int)

        for i, msg in enumerate(self.messages):
            bits = msg.decoded_bits_str
            preamble_lengths[i] = min((bits.index(sync_word) - preamble_starts[i]
                                       for sync_word in sync_words
                                       if sync_word in bits
                                       # There must be at least 2 bits preamble
                                       and bits.index(sync_word) > 2 + preamble_starts[i]),
                                      default=0)

        return preamble_lengths

    def align_messages(self, preamble_lengths: np.ndarray) -> int:
        """
        Align messages based on their sync words
        :type sync_words: list of str
        :param sync_words: List of sync words as strings of bits e.g. "1001"
        :return: end of sync position
        """
        average_preamble_length = self.get_next_lower_multiple_of_two(int(round(preamble_lengths.mean())))
        # TODO: This alignment will be lost after setting the decoding to another value --> Add an alignment layer?
        for i, msg in enumerate(self.messages):
            if preamble_lengths[i] > average_preamble_length:  # Crop it
                msg.decoded_bits[:] = msg.decoded_bits[preamble_lengths[i] - average_preamble_length:]
            elif preamble_lengths[i] < average_preamble_length:  # Insert bits
                start = msg.decoded_bits[0]
                num_bits = average_preamble_length - preamble_lengths[i]
                preamble_part = array.array("B",
                                            [not start if i % 2 == 0 else start for i in range(num_bits + 1, 1, -1)])
                msg.decoded_bits[:] = preamble_part + msg.decoded_bits[:]

        return average_preamble_length

    def find_possible_syncs(self, raw_preamble_positions=None):
        difference_matrix = self.get_difference_matrix()
        if raw_preamble_positions is None:
            raw_preamble_positions = self.get_raw_preamble_positions()
        return self.determine_sync_candidates(raw_preamble_positions, difference_matrix)

    def determine_sync_candidates(self, raw_preamble_positions: np.ndarray,
                                  difference_matrix: np.ndarray,
                                  n_gram_length=4) -> list:
        sync_lengths = defaultdict(int)
        possible_sync_words = defaultdict(int)

        for i in range(difference_matrix.shape[0]):
            for j in range(i + 1, difference_matrix.shape[1]):
                # position of first difference between message i and j
                sync_end = difference_matrix[i, j]

                if sync_end == 0:
                    continue

                for index, k in itertools.product([i, j], range(2)):
                    start = raw_preamble_positions[index, 0] + raw_preamble_positions[index, k+1]

                    # We take the next lower multiple of n for the sync len
                    # In doubt, it is better to under estimate the sync len to prevent it from
                    # taking needed values from other fields e.g. leading zeros for a length field
                    sync_len = self.lower_multiple_of_n(sync_end - start, n_gram_length)

                    sync_word = self.messages[index].decoded_bits_str[start:start + sync_len]

                    if sync_word not in ("", "10", "01"):
                        # Sync word must not be empty or just two bits long and "10" or "01" because
                        # that would be indistinguishable from the preamble
                        sync_lengths[sync_len] += 1
                        possible_sync_words[sync_word] += 1

        self.__debug("Sync word lengths", sync_lengths)
        self.__debug("Possible sync words", possible_sync_words)

        # We may have sync lengths that are too long here.
        # This happens, when there are constant fields behind sync such as length field for messages with same length.
        # Therefore, we take the minimum sync length which surpasses the 75 percentile of frequencies.
        # For example, for these values
        #   {32: 174, 36: 302, 40: 64, 80: 52, 132: 16, 136: 16}
        #   32 would get chosen over 36, because it's frequency surpasses the 75 percentile and is smaller than 36.
        # In doubt, it is better to underestimate the sync length
        # because overestimation will lead to serious errors when the other engines start operating.
        percentile = np.percentile(list(sync_lengths.values()), 75)
        estimated_sync_length = min(sync_len for sync_len, frequency in sync_lengths.items() if frequency > percentile)

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
        result = np.zeros((len(self.messages), 3), dtype=int)

        for i, msg in enumerate(self.messages):
            start, lower, upper = self.get_raw_preamble_position(msg)
            result[i, 0] = start
            result[i, 1] = lower - start
            result[i, 2] = upper - start

        return result

    def get_difference_matrix(self) -> np.ndarray:
        """
        Return a matrix of the first difference index between all messages
        :return:
        """
        result = np.zeros((len(self.messages), len(self.messages)), dtype=int)

        for i in range(len(self.messages)):
            for j in range(i + 1, len(self.messages)):
                result[i, j] = awre_util.find_first_difference(self.messages[i].decoded_bits,
                                                               self.messages[j].decoded_bits)

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
    def get_raw_preamble_position(message: Message) -> tuple:
        """
        Get the raw preamble length of a message by simply finding the first index of at least two equal bits
        The method ensures that the returned length is a multiple of 2.

        This method returns a tuple representing the upper and lower bound of the preamble because we cannot tell it
        for sure e.g. for sync words 1001 or 0110
        """
        bits = message.decoded_bits_str

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

            lower = upper = start + Preprocessor.lower_multiple_of_n(i+1-start, n+m)
            lower -= (n+m)

            k = (upper-start) / (n+m)

        if k > 2:
            return start, lower, upper
        else:
            # no preamble found
            return 0, 0, 0