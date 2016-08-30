from urh import constants
from urh.awre.components.Component import Component

class Preamble(Component):
    def __init__(self, priority=0, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)

    def _py_find_field(self, bitvectors, column_ranges, rows):
        preamble_ranges = []

        for i in rows:
            pre_start, pre_end = self.__find_preamble_end(bitvectors[i], column_ranges[0][0], column_ranges[0][1])
            if pre_start and pre_end:
                preamble_ranges.append((pre_start, pre_end))

        if len(preamble_ranges) == 0:
            return 0, 0

        preamble_range = max(preamble_ranges, key=preamble_ranges.count)
        return 0, preamble_range[1]


    def __find_preamble_end(self, bitvector, rng_start, rng_end):
        try:
            start = 0
            while start < rng_end - 1:
                if bitvector[start] != bitvector[start+1]:
                    break
                start += 1

            if not bitvector[start]:
                start += 1

            for i in range(start+rng_start, rng_end, constants.SHORTEST_PREAMBLE_IN_BITS):
                for j in range(0, constants.SHORTEST_PREAMBLE_IN_BITS, 2):
                    if not (bitvector[i + j] and not bitvector[i + j + 1]):
                        return (start, i) if i >= 0 else (None, None)

            return (start, len(bitvector)) if len(bitvector) >= 0 else (None, None)

        except IndexError:
            return None