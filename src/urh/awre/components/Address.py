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
                other_row = rows[j]
                if self.participant_lut[other_row] == participant:
                    xor_vec = self.xor_matrix[row, other_row][self.xor_matrix[row, other_row] != -1]
                    for rng_start, rng_end in column_ranges:
                        start = 0
                        # The last 1 marks end of seqzence, and prevents swalloing long zero sequences at the end
                        cmp_vector = np.append(xor_vec[rng_start:rng_end], 1)
                        for end in np.where(cmp_vector == 1)[0]:
                            if end - start >= self.MIN_ADDRESS_LENGTH:
                                equal_range = (rng_start + start, rng_start + end)
                                s = equal_ranges_per_participant[participant].setdefault(equal_range, set())
                                s.add(row)
                                s.add(other_row)
                            start = end + 1

        for parti in sorted(equal_ranges_per_participant):
            print(parti)
            for row, p in enumerate(self.participant_lut):
                if p == parti:
                    b = "".join(map(str,map(int,bitvectors[row])))[72:]
                  #  print(b)
                    hex_str = "".join([hex(int(b[i:i+4],2))[2:]for i in range(0,len(b),4)])
                  #  print(hex_str)
                  #  print()


            for rng in sorted(set(equal_ranges_per_participant[parti])):
                start, end = rng
                index = next(iter(equal_ranges_per_participant[parti][rng]))
                bits = bitvectors[index][start:end]
                bits_str = "".join(map(str, map(int, bitvectors[index][start:end])))
                while len(bits) % 4 != 0:
                    bits = np.append(bits, 0)
                occurences = len(equal_ranges_per_participant[parti][rng])
                if occurences >= 0:
                   # For Bob the adress 1b60330 is found to be 0x8db0198000 which is correct,
                   # as it starts with a leading 1 in all messages.
                   # This is the last Bit of e0003 (Broadcast) or 78e289  (Other address)
                   # Code to verify: hex(int("1000"+bin(int("1b6033",16))[2:]+"000",2))
                   print(start // 4 + 1, end // 4, "({})".format(occurences),
                         hex(int("".join(map(str, bits)), 2)), len(bitvectors[index]), bits_str)



        raise NotImplementedError("Todo")