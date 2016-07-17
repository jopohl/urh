import math
from collections import defaultdict

from urh.awre.components.Component import Component

class Length(Component):
    """
    The length is defined as byte length and found via a scoring algorithm.
    """


    def __init__(self, priority=2, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend )
        self.sync_end = 0
        """
        Says where the sync ends (in bit). This will not get counted to calculate the byte length of the blocks.
        This value is set in the FormatFinder.

        :type: int
        """

    def _py_find_field(self, bitvectors, column_ranges, rows):
        sync_len = self.__nbits2bytes(self.sync_end)
        scores = defaultdict(int)
        weights = {-5: 1, -4: 2, -3: 3, -2: 4, -1: 5, 0: 6}
        for row in rows:
            bv = bitvectors[row]
            byte_len = self.__nbits2bytes(len(bv)) - sync_len
            for start, end in column_ranges[row]:
                for byte_start in range(start, end, 8):
                    byte_end = byte_start + 8 if byte_start + 8 <= end else end
                    byte = int("".join(["1" if bit else "0" for bit in bv[byte_start:byte_end]]), 2)
                    diff = byte - byte_len
                    if diff in weights:
                        scores[(byte_start, byte_end)] += weights[diff]
        try:
            return max(scores, key=scores.__getitem__)
        except ValueError:
            return 0,0


    def __nbits2bytes(self, nbits):
        return int(math.ceil(nbits / 8))
