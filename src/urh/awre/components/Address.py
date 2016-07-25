from collections import defaultdict

import numpy as np

from urh.awre.components.Component import Component

class Address(Component):
    def __init__(self, participant_lut, xor_matrix, priority=2, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)
        self.xor_matrix = xor_matrix
        self.participant_lut = participant_lut

    def _py_find_field(self, bitvectors, column_ranges, rows):

        # Cluster participants
        participant_xor = defaultdict(list)
        for i, row in enumerate(rows):
            participant = self.participant_lut[row]
            for j in range(i, len(rows)):
                if self.participant_lut[rows[j]] == participant:
                    participant_xor[participant].append(self.xor_matrix[i, j][self.xor_matrix[i, j] != -1])

        equal_ranges_per_participant = defaultdict(list)
        for participant in participant_xor:
            for xor_vec in participant_xor[participant]:
                for rng_start, rng_end in column_ranges:
                    start = 0
                    for end in np.where(xor_vec[rng_start:rng_end] == 1)[0]:
                        if start < end - 1:
                            equal_ranges_per_participant[participant].append((rng_start + start, rng_start + end - 1))
                        start = end + 1

        for part in equal_ranges_per_participant:
            print(part, sorted(set(equal_ranges_per_participant[part])))

        raise NotImplementedError("Todo")