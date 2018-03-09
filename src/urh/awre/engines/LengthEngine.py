import math
import numpy as np
from collections import defaultdict

from urh.awre.CommonRange import CommonBitRange, EmptyCommonBitRange
from urh.awre.Histogram import Histogram
from urh.awre.engines.Engine import Engine


class LengthEngine(Engine):
    def __init__(self, bitvectors):
        """

        :type bitvectors: list of np.ndarray
        :param bitvectors: bitvectors behind the synchronization
        """
        self.bitvectors = bitvectors

    def find(self, n_gram_length=8, minimum_score=0.8):
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
                         and rng.values[0] == r.values[0]])
            if count < 2:
                continue

            for length in common_ranges_by_length:
                try:
                    common_ranges_by_length[length].remove(rng)
                except ValueError:
                    pass

        self._debug("Common Ranges:", common_ranges_by_length)

        # TODO: Try different score modes (endianess, window length...)
        # The window length must be smaller than common range's length
        # and is something like 8 in case of on 8 bit integer.
        # We make this generic so e.g. 4 bit integers are supported as well
        for length, common_ranges in common_ranges_by_length.items():
            for common_range in common_ranges:
                common_range.score = self.score_range(common_range, length)
                common_range.field_type = "Length"

        # Take the ranges with highest score per cluster
        # if it's score surpasses the minimum score
        high_scores_by_length = dict()
        for length, ranges in common_ranges_by_length.items():
            high_score_range = max(ranges, key=lambda x: x.score, default=None)  # type: CommonBitRange
            if high_score_range is None or high_score_range.score < minimum_score:
                high_score_range = EmptyCommonBitRange(field_type="Length")
            high_scores_by_length[length] = high_score_range

        self._debug("Highscore ranges", high_scores_by_length)

        return high_scores_by_length

    @staticmethod
    def score_range(common_range: CommonBitRange, target_length: int):
        """
        Score a common bit range based on the target length.
        :param common_range:
        :param target_length:
        :return:
        """
        # TODO: Consider different endianess, window functions etc.
        # See if there is a correlation of the values in that range and the message length
        #   - use 8 / 16 / 32 ... bit windows
        #   - try both endianness
        #   - hardcore mode: try any n bit window
        # See if there are common equal ranges between the clusters -> try these first
        assert len(common_range.values) == 1
        value = int(common_range.values[0], 2)

        if value < target_length or value == 0:
            return 0

        return max(0.0, 1 - (value - target_length) / 10)
