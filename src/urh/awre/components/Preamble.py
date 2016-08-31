from collections import defaultdict
from urh.awre.components.Component import Component
from urh.signalprocessing.Message import Message


class Preamble(Component):
    """
    Assign Preamble and SoF.

    """
    def __init__(self, priority=0, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)

    def _py_find_field(self, messages):
        preamble_ranges = defaultdict(list)

        for msg in messages:
            rng = self.__find_preamble_range(msg)
            if rng:
                preamble_ranges[msg.message_type].append(rng)

        sof_ranges = defaultdict(list)
        for message_type, ranges in preamble_ranges.items():
            start, end = max(ranges, key=ranges.count)
            message_type.add_protocol_label(start=start, end=end, type_index=0, name="Preamble")

    def __find_preamble_range(self, message: Message):
        search_start = 0

        if len(message.message_type) == 0:
            search_end = len(message.decoded_bits)
        else:
            search_end = message.message_type[0]

        bits = message.decoded_bits

        # Skip sequences of equal bits
        first_difference = next((i for i in range(search_start, search_end-1) if bits[i] != bits[i+1]), None)
        if first_difference is None:
            return None

        preamble_end = next((i-1 for i in range(first_difference, search_end, 4)
            if bits[i] == bits[i+1] or bits[i] != bits[i+2] or bits[i] == bits[i+3]), search_end)

        if preamble_end - first_difference > 4:
            return first_difference, preamble_end
        else:
            return None


    def __find_sync_range(self):
        """
        Finding the synchronization works by finding the first difference between two messages.
        This is performed for all messages and the most frequent first difference is chosen
        """

        # 1. If preamble there: Start behind it
        # 1a. Do not search behind other labels
        # 2. Search for first difference
        #


        possible_sync_pos = defaultdict(int)
        print(column_ranges)

        for i in range(0, len(rows)):
            bitvector_i = bitvectors[rows[i]]
            for j in range(i, len(rows)):
                bitvector_j = bitvectors[rows[j]]
                for start, end in column_ranges:
                    bits_i = bitvector_i[start:end]
                    bits_j = bitvector_j[start:end]
                    try:
                        first_diff = next(k for k, (bit_i, bit_j) in enumerate(zip(bits_i, bits_j)) if bit_i != bit_j)
                    except StopIteration:
                        continue
                    start = 4 * (start // 4)
                    first_diff = start + 4 * (first_diff // 4)
                    if start != first_diff:
                        possible_sync_pos[(start, first_diff)] += 1