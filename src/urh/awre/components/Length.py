import math
from collections import defaultdict

import numpy as np

from urh.awre.components.Component import Component
from urh.signalprocessing.Interval import Interval


class Length(Component):
    """
    The length is defined as byte length and found by finding equal ranges in the length clustered blocks.
    A length field should be a common equal range in all clusters.
    """


    def __init__(self, length_cluster, priority=2, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend )
        self.sync_end = 0
        """
        Says where the sync ends (in bit). This will not get counted to calculate the byte length of the blocks.
        This value is set in the FormatFinder.

        :type: int
        """

        self.length_cluster = length_cluster

    def _py_find_field(self, bitvectors, column_ranges, rows):
        equal_ranges = defaultdict(list)
        for vec_len in set(len(bitvectors[row]) for row in rows):
            try:
                cluster = self.length_cluster[vec_len]
                for rng_start, rng_end in column_ranges:
                    start = 0
                    for end in np.where(cluster[rng_start:rng_end] < self.EQUAL_BIT_TRESHOLD)[0]:
                        if start < end-1:
                            equal_ranges[vec_len].append((rng_start+start, rng_start+end-1))
                        start = end+1
            except KeyError:
                continue

        common_intervals = []
        keys = sorted(equal_ranges)
        for interval in equal_ranges[keys[0]]:
            candidate = Interval(interval[0], interval[1])
            for other_key in keys[1:]:
                matches = []
                for other_interval in equal_ranges[other_key]:
                    oi = Interval(other_interval[0], other_interval[1])
                    if oi.overlaps_with(candidate):
                        candidate = candidate.find_common_interval(oi)
                        matches.append(candidate)

                if not matches:
                    candidate = None
                    break
                else:
                    candidate = Interval.find_greatest(matches)

            if candidate:
                common_intervals.append(candidate)

        # Now we have the common intervals and need to check which one is the length
        sync_len = self.__nbits2bytes(self.sync_end)
        scores = defaultdict(int)
        weights = {-5: 1, -4: 2, -3: 3, -2: 4, -1: 5, 0: 6}
        for ci in common_intervals:
            for row in rows:
                bv = bitvectors[row]
                byte_len = self.__nbits2bytes(len(bv)) - sync_len
                start, end = ci.start, ci.end
                for byte_start in range(start, end, 8):
                    byte_end = byte_start + 8 if byte_start + 8 <= end else end
                    try:
                        byte = int("".join(["1" if bit else "0" for bit in bv[byte_start:byte_end]]), 2)
                        diff = byte - byte_len
                        if diff in weights:
                            scores[(byte_start, byte_end)] += weights[diff]
                    except ValueError:
                        pass # Byte_end or byte_start was out of bv --> too close on the end

        try:
            return max(scores, key=scores.__getitem__)
        except ValueError:
            return 0, 0

    def __nbits2bytes(self, nbits):
        return int(math.ceil(nbits / 8))
