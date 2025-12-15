import itertools
import math
import os
import time
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

    _DEBUG_ = False

    def __init__(self, bitvectors: list, existing_message_types: dict = None):
        self.bitvectors = bitvectors  # type: list[np.ndarray]
        self.existing_message_types = (
            existing_message_types if existing_message_types is not None else dict()
        )

    def preprocess(self) -> (np.ndarray, int):
        raw_preamble_positions = self.get_raw_preamble_positions()
        existing_sync_words = self.__get_existing_sync_words()
        if len(existing_sync_words) == 0:
            sync_words = self.find_possible_syncs(raw_preamble_positions)
        else:
            # NOTE: This does not cover the case if protocol has multiple sync words and not all of them were labeled
            sync_words = existing_sync_words

        preamble_starts = raw_preamble_positions[:, 0]
        preamble_lengths = self.get_preamble_lengths_from_sync_words(
            sync_words, preamble_starts=preamble_starts
        )
        sync_len = len(sync_words[0]) if len(sync_words) > 0 else 0
        return preamble_starts, preamble_lengths, sync_len

    def get_preamble_lengths_from_sync_words(
        self, sync_words: list, preamble_starts: np.ndarray
    ):
        """
        Get the preamble lengths based on the found sync words for all messages.
        If there should be more than one sync word in a message, use the first one.

        :param sync_words:
        :param preamble_starts:
        :return:
        """
        # If there should be varying sync word lengths we need to return an array of sync lengths per message
        assert all(len(sync_word) == len(sync_words[0]) for sync_word in sync_words)

        byte_sync_words = [bytes(map(int, sync_word)) for sync_word in sync_words]

        result = np.zeros(len(self.bitvectors), dtype=np.uint32)

        for i, bitvector in enumerate(self.bitvectors):
            preamble_lengths = []
            bits = bitvector.tobytes()

            for sync_word in byte_sync_words:
                sync_start = bits.find(sync_word)
                if sync_start != -1:
                    if sync_start - preamble_starts[i] >= 2:
                        preamble_lengths.append(sync_start - preamble_starts[i])

                    # Consider case where sync word starts with preamble pattern
                    sync_start = bits.find(
                        sync_word, sync_start + 1, sync_start + 2 * len(sync_word)
                    )

                    if sync_start != -1:
                        if sync_start - preamble_starts[i] >= 2:
                            preamble_lengths.append(sync_start - preamble_starts[i])

            preamble_lengths.sort()

            if len(preamble_lengths) == 0:
                result[i] = 0
            elif len(preamble_lengths) == 1:
                result[i] = preamble_lengths[0]
            else:
                # consider all indices not more than one byte before first one
                preamble_lengths = list(
                    filter(lambda x: x < preamble_lengths[0] + 7, preamble_lengths)
                )

                # take the smallest preamble_length, but prefer a greater one if it is divisible by 8 (or 4)
                preamble_length = next(
                    (pl for pl in preamble_lengths if pl % 8 == 0), None
                )
                if preamble_length is None:
                    preamble_length = next(
                        (pl for pl in preamble_lengths if pl % 4 == 0), None
                    )
                if preamble_length is None:
                    preamble_length = preamble_lengths[0]
                result[i] = preamble_length

        return result

    def find_possible_syncs(self, raw_preamble_positions=None):
        difference_matrix = self.get_difference_matrix()
        if raw_preamble_positions is None:
            raw_preamble_positions = self.get_raw_preamble_positions()
        return self.determine_sync_candidates(
            raw_preamble_positions, difference_matrix, n_gram_length=4
        )

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
                result[common_prefix] += (
                    possible_sync_words[sync1] + possible_sync_words[sync2]
                )
            else:
                result[sync1] += possible_sync_words[sync1]
                result[sync2] += possible_sync_words[sync2]
        return result

    def determine_sync_candidates(
        self,
        raw_preamble_positions: np.ndarray,
        difference_matrix: np.ndarray,
        n_gram_length=4,
    ) -> list:
        possible_sync_words = awre_util.find_possible_sync_words(
            difference_matrix, raw_preamble_positions, self.bitvectors, n_gram_length
        )

        self.__debug("Possible sync words", possible_sync_words)
        if len(possible_sync_words) == 0:
            return []

        possible_sync_words = self.merge_possible_sync_words(
            possible_sync_words, n_gram_length
        )
        self.__debug("Merged sync words", possible_sync_words)

        scores = self.__score_sync_lengths(possible_sync_words)

        sorted_scores = sorted(scores, reverse=True, key=scores.get)
        estimated_sync_length = sorted_scores[0]
        if estimated_sync_length % 8 != 0:
            for other in filter(
                lambda x: 0 < estimated_sync_length - x < 7, sorted_scores
            ):
                if other % 8 == 0:
                    estimated_sync_length = other
                    break

        # Now we look at all possible sync words with this length
        sync_words = {
            word: frequency
            for word, frequency in possible_sync_words.items()
            if len(word) == estimated_sync_length
        }
        self.__debug("Sync words", sync_words)

        additional_syncs = self.__find_additional_sync_words(
            estimated_sync_length, sync_words, possible_sync_words
        )

        if additional_syncs:
            self.__debug("Found additional sync words", additional_syncs)
            sync_words.update(additional_syncs)

        result = []
        for sync_word in sorted(sync_words, key=sync_words.get, reverse=True):
            # Convert bytes back to string
            result.append("".join(str(c) for c in sync_word))

        return result

    def __find_additional_sync_words(
        self, sync_length: int, present_sync_words, possible_sync_words
    ) -> dict:
        """
        Look for additional sync words, in case we had varying preamble lengths and multiple sync words
        (see test_with_three_syncs_different_preamble_lengths for an example)

        :param sync_length:
        :type present_sync_words: dict
        :type possible_sync_words: dict
        :return:
        """
        np_syn = [
            np.fromiter(map(int, sync_word), dtype=np.uint8, count=len(sync_word))
            for sync_word in present_sync_words
        ]

        messages_without_sync = [
            i
            for i, bv in enumerate(self.bitvectors)
            if not any(
                awre_util.find_occurrences(bv, s, return_after_first=True)
                for s in np_syn
            )
        ]

        result = dict()
        if len(messages_without_sync) == 0:
            return result

        # Is there another sync word that applies to all messages without sync?
        additional_candidates = {
            word: score
            for word, score in possible_sync_words.items()
            if len(word) > sync_length
            and not any(s in word for s in present_sync_words)
        }

        for sync in sorted(
            additional_candidates, key=additional_candidates.get, reverse=True
        ):
            if len(messages_without_sync) == 0:
                break

            score = additional_candidates[sync]
            s = sync[:sync_length]
            np_s = np.fromiter(s, dtype=np.uint8, count=len(s))
            matching = [
                i
                for i in messages_without_sync
                if awre_util.find_occurrences(
                    self.bitvectors[i], np_s, return_after_first=True
                )
            ]
            if matching:
                result[s] = score
                for m in matching:
                    messages_without_sync.remove(m)

        return result

    def get_raw_preamble_positions(self) -> np.ndarray:
        """
        Return a 2D numpy array where first column is the start of preamble
        second and third columns are lower and upper bound for preamble length by message, respectively
        """
        result = np.zeros((len(self.bitvectors), 3), dtype=np.uint32)

        for i, bitvector in enumerate(self.bitvectors):
            if i in self.existing_message_types:
                preamble_label = self.existing_message_types[
                    i
                ].get_first_label_with_type(FieldType.Function.PREAMBLE)
            else:
                preamble_label = None

            if preamble_label is None:
                start, lower, upper = awre_util.get_raw_preamble_position(bitvector)
            else:
                # If this message is already labeled with a preamble we just use it's values
                start, lower, upper = (
                    preamble_label.start,
                    preamble_label.end,
                    preamble_label.end,
                )

            result[i, 0] = start
            result[i, 1] = lower - start
            result[i, 2] = upper - start

        return result

    def get_difference_matrix(self) -> np.ndarray:
        """
        Return a matrix of the first difference index between all messages
        :return:
        """
        return awre_util.get_difference_matrix(self.bitvectors)

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
                sync_label = self.existing_message_types[i].get_first_label_with_type(
                    FieldType.Function.SYNC
                )
            else:
                sync_label = None

            if sync_label is not None:
                result.append(
                    "".join(map(str, bitvector[sync_label.start : sync_label.end]))
                )
        return result

    def __debug(self, *args):
        if self._DEBUG_:
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
