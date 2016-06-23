from collections import defaultdict

from urh import constants
from urh.signalprocessing.Interval import Interval
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
                            self.constant_indices[i].add(Interval(range_start, range_end))
                            self.constant_indices[j].add(Interval(range_start, range_end))

                        constant_length = 0
                        range_start = k

                if constant_length > constants.SHORTEST_CONSTANT_IN_BITS:
                    range_end = 4 * ((end) // 4)
                    self.constant_indices[i].add(Interval(range_start, range_end))
                    self.constant_indices[j].add(Interval(range_start, range_end))


        # Combine intervals
        combined_indices = dict()
        for block_index, intervals in self.constant_indices.items():
            combined_intervals = list()
            for interval in sorted(intervals):
                last_interval = None if len(combined_intervals) == 0 else combined_intervals[-1]
                if last_interval and last_interval.overlaps_with(interval):
                    combined_intervals.remove(last_interval)
                    combined_intervals.append(last_interval.find_common_interval(interval))
                else:
                    combined_intervals.append(interval)

                combined_indices[block_index] = combined_intervals

        for block_index in self.constant_indices:
            print(block_index, sorted(self.constant_indices[block_index]))
            print(block_index, combined_indices[block_index])

    def __get_hex_value_for_block(self, block, interval):
        start, end = block.convert_range(interval.start + self.preamble_end + 1,
                                   interval.end + self.preamble_end, from_view=0, to_view=1, decoded=True)
        return block.decoded_hex_str[start:end]

    def find_sync(self) -> ProtocolLabel:
        if self.preamble_end == 0:
            self.find_preamble()
        if len(self.constant_indices) == 0:
            self.find_constants()

        possible_sync_pos = defaultdict(int)
        for block_index, const_interval in self.constant_indices.items():
            for const_range in const_interval:
                if const_range.start == 0:
                    possible_sync_pos[const_range] += 1

        sync_interval = max(possible_sync_pos, key=possible_sync_pos.__getitem__)

        return ProtocolLabel(start=self.preamble_end + sync_interval.start + 1, end=self.preamble_end + sync_interval.end-1,
                             name="Sync", color_index=None, val_type_index=0)


