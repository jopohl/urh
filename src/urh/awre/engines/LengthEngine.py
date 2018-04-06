import math
from collections import defaultdict
from pprint import pprint

import numpy as np

from urh.awre.CommonRange import CommonRange, EmptyCommonRange
from urh.awre.engines.Engine import Engine
from urh.util import util


class LengthEngine(Engine):
    def __init__(self, bitvectors):
        """

        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors

    def find(self, n_gram_length=8, minimum_score=0.1):
        # Consider the n_gram_length
        bitvectors_by_n_gram_length = defaultdict(list)
        for i, bitvector in enumerate(self.bitvectors):
            bin_num = int(math.ceil(len(bitvector) / n_gram_length))
            bitvectors_by_n_gram_length[bin_num].append(i)

        # TODO: From here we should start a loop for subclustering
        common_ranges_by_length = self.find_common_ranges_by_cluster(self.bitvectors, bitvectors_by_n_gram_length)

        # Ranges must be common along length clusters
        # but their values must differ, so now we rule out all ranges that are
        #   1. common across clusters AND
        #   2. have same value
        ranges = [r for rng in common_ranges_by_length.values() for r in rng]
        for rng in ranges:
            count = len([r for r in ranges if rng.start == r.start
                         and rng.length == r.length
                         and rng.value_str == r.value_str])
            if count < 2:
                continue

            for length in common_ranges_by_length:
                try:
                    common_ranges_by_length[length].remove(rng)
                except ValueError:
                    pass

        self._debug("Common Ranges:", common_ranges_by_length)

        # TODO: Try different endianess
        # The window length must be smaller than common range's length
        # and is something like 8 in case of on 8 bit integer.
        # We make this generic so e.g. 4 bit integers are supported as well
        if n_gram_length == 8:
            window_lengths = [8, 16, 32, 64]
        else:
            window_lengths = [n_gram_length * i for i in range(1, 5)]

        scored_ranges = dict()
        for length in common_ranges_by_length:
            scored_ranges[length] = dict()
            for window_length in window_lengths:
                scored_ranges[length][window_length] = []

        for window_length in window_lengths:
            for length, common_ranges in common_ranges_by_length.items():
                for common_range in filter(lambda cr: cr.length >= window_length, common_ranges):
                    bits = common_range.value_str
                    max_score = max_start = -1
                    for start in range(0, len(bits) + 1 - window_length):
                        score = self.score_bits(bits[start:start + window_length], length, position=start)
                        if score > max_score:
                            max_score = score
                            max_start = start

                    rng = CommonRange(common_range.start + max_start, window_length,
                                      common_range.value[max_start:max_start + window_length],
                                      score=max_score, field_type="length",
                                      message_indices=common_range.message_indices,
                                      range_type=common_range.range_type)
                    scored_ranges[length][window_length].append(rng)

        self._debug("scored ranges", scored_ranges)

        # Take the ranges with highest score per cluster if it's score surpasses the minimum score
        high_scores_by_length = dict()

        for length, ranges_by_window_length in scored_ranges.items():
            for window_length, ranges in ranges_by_window_length.items():
                high_score_range = max(ranges, key=lambda x: x.score, default=None)  # type: CommonRange

                if high_score_range is None or high_score_range.score < minimum_score:
                    high_score_range = EmptyCommonRange(field_type="length")

                if length not in high_scores_by_length or high_scores_by_length[length].score < high_score_range.score:
                    high_scores_by_length[length] = high_score_range

        found_ranges = list(filter(lambda x: not isinstance(x, EmptyCommonRange), high_scores_by_length.values()))

        # If there are length clusters with only one message see if we can assign a range from other clusters
        for length, msg_indices in bitvectors_by_n_gram_length.items():
            if len(msg_indices) != 1:
                continue

            msg_index = msg_indices[0]
            bitvector = self.bitvectors[msg_index]
            max_score, best_match = 0, None

            for rng in found_ranges:
                bits = util.convert_numbers_to_hex_string(bitvector[rng.start:rng.end + 1])
                score = self.score_bits(bits, length, rng.start)
                if score > max_score:
                    best_match, max_score = rng, score

            if best_match is not None:
                high_scores_by_length[length] = CommonRange(best_match.start, best_match.length,
                                                            value=bitvector[best_match.start:best_match.end + 1],
                                                            score=max_score, field_type="length",
                                                            message_indices={msg_index}, range_type="bit")

        self._debug("Highscore ranges", high_scores_by_length)
        return high_scores_by_length

    @staticmethod
    def score_bits(bits: str, target_length: int, position: int):
        value = int(bits, 2)

        # Length field should be at front, so we give lower scores for large starts
        f = (1 / (1 + 0.25 * position))

        return f * LengthEngine.gauss(value, target_length)

    @staticmethod
    def gauss(x, mu, sigma=2):
        return np.exp(-0.5 * np.power((x - mu) / sigma, 2))
