from collections import defaultdict

from urh import constants
from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class LabelAssigner(object):
    def __init__(self, blocks):
        """

        :type blocks: list of ProtocolBlock
        """
        self.blocks = blocks
        self.preamble_end = 0
        self.constant_indices = defaultdict(set)

    def find_preamble(self) -> ProtocolLabel:
        preamble_ends = list()

        for block in self.blocks:
            # searching preamble
            preamble_end = block.find_preamble_end()
            if preamble_end is None or preamble_end < 1:
                continue
            preamble_ends.append(preamble_end)

        if len(preamble_ends) == 0:
            return None

        self.preamble_end = max(preamble_ends, key=preamble_ends.count)
        return ProtocolLabel(name="Preamble", start=0, end=self.preamble_end-1, val_type_index=0, color_index=None)

    def find_constants(self):
        self.constant_indices.clear()
        for i in range(0, len(self.blocks)):
            for j in range(i + 1, len(self.blocks)):
                range_start = 0
                constant_length = 0
                bits_i = self.blocks[i].decoded_bits[self.preamble_end:]
                bits_j = self.blocks[j].decoded_bits[self.preamble_end:]
                end = min(len(bits_i), len(bits_j)) - 1

                for k, (bit_i, bit_j) in enumerate(zip(bits_i, bits_j)):
                    if bit_i == bit_j:
                        constant_length += 1
                    else:
                        if constant_length > constants.SHORTEST_CONSTANT_IN_BITS:
                            range_end = 4 * ((k - 1) // 4)
                            self.constant_indices[i].add((range_start, range_end))
                            self.constant_indices[j].add((range_start, range_end))

                        constant_length = 0
                        range_start = k

                if constant_length > constants.SHORTEST_CONSTANT_IN_BITS:
                    range_end = 4 * ((end) // 4)
                    self.constant_indices[i].add((range_start, range_end))
                    self.constant_indices[j].add((range_start, range_end))

    def find_sync(self) -> ProtocolLabel:
        if self.preamble_end == 0:
            self.find_preamble()
        if len(self.constant_indices) == 0:
            self.find_constants()

        possible_sync_pos = defaultdict(int)
        for block_index, const_ranges in self.constant_indices.items():
            for const_range in const_ranges:
                if const_range[0] == 0:
                    possible_sync_pos[const_range] += 1

        sync_range = max(possible_sync_pos, key=possible_sync_pos.__getitem__)

        return ProtocolLabel(start=self.preamble_end + sync_range[0] + 1, end=self.preamble_end + sync_range[1]-1,
                             name="Sync", color_index=None, val_type_index=0)