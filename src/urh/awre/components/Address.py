from collections import defaultdict

import numpy as np

from urh.awre.components.Component import Component

class Address(Component):
    MIN_ADDRESS_LENGTH = 8 # Address should be at least one byte

    def __init__(self, participant_lut, xor_matrix, priority=2, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)
        self.xor_matrix = xor_matrix
        self.participant_lut = participant_lut

    def _py_find_field(self, bitvectors, column_ranges, rows):

        # Cluster participants
        equal_ranges_per_participant = defaultdict(dict)

        for i, row in enumerate(rows):
            participant = self.participant_lut[row]
            for j in range(i, len(rows)):
                if self.participant_lut[rows[j]] == participant:
                    xor_vec = self.xor_matrix[i, j][self.xor_matrix[i, j] != -1]
                    for rng_start, rng_end in column_ranges:
                        start = 0
                        for end in np.where(xor_vec[rng_start:rng_end] == 1)[0]:
                            if start < end - 1 and end - start >= self.MIN_ADDRESS_LENGTH:
                                equal_range = (rng_start + start, rng_start + end - 1)
                                s = equal_ranges_per_participant[participant].setdefault(equal_range, set())
                                s.add(i)
                                s.add(j)
                            start = end + 1


        for parti in sorted(equal_ranges_per_participant):
            print(parti)
            for rng in sorted(set(equal_ranges_per_participant[parti])):
                start, end = rng
                index = next(iter(equal_ranges_per_participant[parti][rng]))
                bits = bitvectors[index][start:end]
                while len(bits) % 4 != 0:
                    bits = np.append(bits, 0)
                #bits[0:0] = [0] * (4-len(bits)  % 4)
                print(start//4+1, end//4, "({})".format(index), hex(int("".join(map(str, bits)),2)))

        raise NotImplementedError("Todo")