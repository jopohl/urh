from collections import defaultdict
from urh.awre.components.Component import Component
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message


class Preamble(Component):
    """
    Assign Preamble and SoF.

    """
    def __init__(self, fieldtypes, priority=0, predecessors=None, enabled=True, backend=None, messagetypes=None):
        """

        :type fieldtypes: list of FieldType
        :param priority:
        :param predecessors:
        :param enabled:
        :param backend:
        :param messagetypes:
        """
        super().__init__(priority, predecessors, enabled, backend, messagetypes)

        self.preamble_field_type = next((ft for ft in fieldtypes if ft.function == ft.Function.PREAMBLE), None)
        self.sync_field_type = next((ft for ft in fieldtypes if ft.function == ft.Function.SYNC), None)

        self.preamble_name = self.preamble_field_type.caption if self.preamble_field_type else "Preamble"
        self.sync_name = self.sync_field_type.caption if self.sync_field_type else "Synchronization"

    def _py_find_field(self, messages):
        """

        :type messages: list of Message
        :return:
        """
        preamble_ranges = defaultdict(list)
        """:type: dict[MessageType, list] """

        for msg in messages:
            rng = self.__find_preamble_range(msg)
            if rng:
                preamble_ranges[msg.message_type].append(rng)

        preamble_ends = defaultdict(int)
        for message_type, ranges in preamble_ranges.items():
            start, end = max(ranges, key=ranges.count)
            message_type.add_protocol_label(start=start, end=end, name=self.preamble_name,
                                            auto_created=True, type=self.preamble_field_type)

            preamble_ends[message_type] = end + 1

        for message_type in preamble_ranges.keys():
            messages = [msg for msg in messages if msg.message_type == message_type]
            first_field = next((field for field in message_type if field.start > preamble_ends[message_type]), None)
            search_end = first_field.start if first_field is not None else None
            sync_range = self.__find_sync_range(messages, preamble_ends[message_type], search_end)

            if sync_range:
                message_type.add_protocol_label(start=sync_range[0], end=sync_range[1]-1, name=self.sync_name,
                                                auto_created=True, type=self.sync_field_type)


    def __find_preamble_range(self, message: Message):
        search_start = 0

        if len(message.message_type) == 0:
            search_end = len(message.decoded_bits)
        else:
            search_end = message.message_type[0].start

        bits = message.decoded_bits

        # Skip sequences of equal bits
        try:
            first_difference = next((i for i in range(search_start, search_end-1) if bits[i] != bits[i+1]), None)
        except IndexError:
            # see: https://github.com/jopohl/urh/issues/290
            first_difference = None

        if first_difference is None:
            return None

        try:
            preamble_end = next((i-1 for i in range(first_difference, search_end, 4)
                if bits[i] == bits[i+1] or bits[i] != bits[i+2] or bits[i] == bits[i+3]), search_end)
        except IndexError:
            return None

        if preamble_end - first_difference > 4:
            return first_difference, preamble_end
        else:
            return None


    def __find_sync_range(self, messages, preamble_end: int, search_end: int):
        """
        Finding the synchronization works by finding the first difference between two messages.
        This is performed for all messages and the most frequent first difference is chosen

        :type messages: list of Message
        :param preamble_end: End of preamble = start of search
        :param search_end: End of search = start of first other label
        """

        possible_sync_pos = defaultdict(int)


        for i, msg in enumerate(messages):
            bits_i = msg.decoded_bits[preamble_end:search_end]
            for j in range(i, len(messages)):
                bits_j = messages[j].decoded_bits[preamble_end:search_end]
                first_diff = next((k for k, (bit_i, bit_j) in enumerate(zip(bits_i, bits_j)) if bit_i != bit_j), None)
                if first_diff is not None:
                    first_diff = preamble_end + 4 * (first_diff // 4)
                    if (first_diff - preamble_end) >= 4:
                        possible_sync_pos[(preamble_end, first_diff)] += 1
        try:
            sync_interval = max(possible_sync_pos, key=possible_sync_pos.__getitem__)
            return sync_interval
        except ValueError:
            return None
