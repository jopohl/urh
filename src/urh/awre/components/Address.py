from collections import defaultdict

import numpy as np
from urh import constants

from urh.awre.components.Component import Component


class Address(Component):
    MIN_ADDRESS_LENGTH = 8  # Address should be at least one byte

    def __init__(self, participant_lut, xor_matrix, priority=2, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)
        self.xor_matrix = xor_matrix
        self.participant_lut = participant_lut

    def _py_find_field(self, bitvectors, column_ranges, rows):

        # Cluster participants
        equal_ranges_per_participant = defaultdict(dict)

        # Step 1: Find equal ranges for participants by evaluating the XOR matrix participant wise
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
                                d = equal_ranges_per_participant[participant].setdefault(equal_range, dict())
                                bits = "".join(map(str, bitvectors[row][equal_range[0]:equal_range[1]]))
                                s = d.setdefault(bits, set())
                                s.add(row)
                                s.add(other_row)
                            start = end + 1

        print(constants.color.BOLD + "Result after Step 1" +constants.color.END)
        self.__print_ranges(equal_ranges_per_participant, bitvectors)

        # Step 2: Now we want to find our address candidates.
        # Step 2.a: Cluster the ranges based on their byte length
        clustered_addresses = defaultdict(lambda: defaultdict(list))
        range_occurrences = defaultdict(int)
        for participant in equal_ranges_per_participant:
            for start, end in equal_ranges_per_participant[participant]:
                ranges = equal_ranges_per_participant[participant][(start,end)].values()
                range_occurrences[(start, end)] += len((set(row for row_indices in ranges for row in row_indices)))
                byte_len = (end - start) // 8
                bits = list(equal_ranges_per_participant[participant][(start,end)].keys())
                clustered_addresses[byte_len][(start, end)].extend(bits)

        #self.__print_clustered(clustered_addresses)

        # Now we search for ranges that are common in a cluster and contain different bit values. There are two possibilities:
        #   1) If the protocol contains ACKs, these different values are the addresses or at least good candidates for them
        #   2) If the protocol does not contain ACKs, these values contain both addresses and need to be splitted against each other
        # We assume, that the protocol contains ACKs and if we do not find any use the strategy from 2).

        # Step 2.b: Find common ranges with different values in the same cluster
        # TODO: This works only for two participants
        candidates = []
        for bl in sorted(clustered_addresses):
            nvals = sum(len(bits) for bits in clustered_addresses[bl].values())
            byte_str = ""
            if nvals > 2:
                byte_str = constants.color.BOLD
            print(byte_str + "Byte length " + str(bl) + constants.color.END)


            for (start, end), bits in sorted(clustered_addresses[bl].items()):
                print(start, end, bits, "(" + str(range_occurrences[(start, end)]) + ")")


        #print(clustered_addresses)
        # Step 2: Align sequences together (correct bit shifts, align to byte)


        raise NotImplementedError("Todo")

    def __print_clustered(self, clustered_addresses):
        for bl in sorted(clustered_addresses):
            print(constants.color.BOLD + "Byte length " + str(bl) + constants.color.END)
            for (start, end), bits in sorted(clustered_addresses[bl].items()):
                print(start, end, bits)

    def __print_ranges(self, equal_ranges_per_participant, bitvectors):

        for parti in sorted(equal_ranges_per_participant):
            print("\n" + constants.color.UNDERLINE + str(parti.name) + " (" + parti.shortname+ ")" + constants.color.END)
            for row, p in enumerate(self.participant_lut):
                if p == parti:
                    b = "".join(map(str, map(int, bitvectors[row])))[72:]
                    #  print(b)
                    hex_str = "".join([hex(int(b[i:i + 4], 2))[2:] for i in range(0, len(b), 4)])
                    #  print(hex_str)
                    #  print()

            address1 = "000110110110000000110011"
            address2 = "011110001110001010001001"

            assert len(address1) % 8 == 0
            assert len(address2) % 8 == 0

            print("address1", constants.color.BLUE, address1 + " (" +hex(int("".join(map(str, address1)), 2)) +")", constants.color.END)
            print("address2", constants.color.GREEN, address2 + " (" + hex(int("".join(map(str, address2)), 2)) + ")",
                  constants.color.END)

            print()

            for rng in sorted(set(equal_ranges_per_participant[parti])):
                start, end = rng
                for bits in sorted(equal_ranges_per_participant[parti][rng]):
                    bits_str = "".join(map(str, map(int, bits)))

                    padded_bits = bits
                    while len(padded_bits) % 4 != 0:
                        padded_bits = np.append(padded_bits, 0)
                    occurences = len(equal_ranges_per_participant[parti][rng][bits])
                    index = sorted(equal_ranges_per_participant[parti][rng][bits])[0]
                    if occurences >= 0:
                        # For Bob the adress 1b60330 is found to be 0x8db0198000 which is correct,
                        # as it starts with a leading 1 in all messages.
                        # This is the last Bit of e0003 (Broadcast) or 78e289  (Other address)
                        # Code to verify: hex(int("1000"+bin(int("1b6033",16))[2:]+"000",2))
                        # Therefore we need to check for partial bits inside the address candidates to be sure we find the correct ones
                        format_start = ""
                        if address1 in bits_str and address2 not in bits_str:
                            format_start = constants.color.BLUE
                        if address2 in bits_str and address1 not in bits_str:
                            format_start = constants.color.GREEN
                        if address1 in bits_str and address2 in bits_str:
                            format_start = constants.color.RED + constants.color.BOLD

                        print(start, end,
                              "({})\t".format(occurences),
                              format_start + hex(int("".join(map(str, padded_bits)), 2)) + "\033[0m", len(bitvectors[index]),
                              bits_str, "(" + ",".join(map(str, sorted(equal_ranges_per_participant[parti][rng][bits])))+ ")")
