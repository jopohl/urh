import math
from collections import defaultdict

import numpy as np

from urh.awre.components.Component import Component
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Interval import Interval
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class Length(Component):
    """
    The length is defined as byte length and found by finding equal ranges in the length clustered blocks.
    A length field should be a common equal range in all clusters.
    """

    def __init__(self, fieldtypes, length_cluster, priority=2, predecessors=None,
                 enabled=True, backend=None, messagetypes=None):
        super().__init__(priority, predecessors, enabled, backend, messagetypes)

        self.length_field_type = next((ft for ft in fieldtypes if ft.function == ft.Function.LENGTH), None)
        self.length_field_name = self.length_field_type.caption if self.length_field_type else "Length"

        self.length_cluster = length_cluster
        """
        An example length cluster is

        2: [0.5, 1]
        4: [1, 0.75, 1, 1]

        Meaning there were two message lengths: 2 and 4 bit.
        (0.5, 1) means, the first bit was equal in 50% of cases (meaning maximum difference) and bit 2 was equal in all messages

        A simple XOR would not work as it would be very error prone.
        """

    def _py_find_field(self, messages):
        """

        :type messages: list of urh.signalprocessing.Message.Message
        :return:
        """
        messages_by_type = defaultdict(list)
        """:type : dict[urh.signalprocessing.MessageType.MessageType, list[urh.signalprocessing.Message.Message]] """

        for msg in messages:
            messages_by_type[msg.message_type].append(msg)

        # First we get the common ranges per message length
        common_ranges_by_length = defaultdict(lambda: defaultdict(list))
        """:type: dict[urh.signalprocessing.MessageType.MessageType, dict[int, List[(int,int)]]]"""

        for message_type in messages_by_type.keys():
            unlabeled_ranges = message_type.unlabeled_ranges
            for vec_len in set(4 * (len(msg.decoded_bits) // 4) for msg in messages_by_type[message_type]):
                try:
                    cluster = self.length_cluster[vec_len]
                except KeyError:
                    continue  # Skip message lengths that appear only once

                for rng_start, rng_end in unlabeled_ranges:
                    start = 0
                    for end in np.where(cluster[rng_start:rng_end] < self.EQUAL_BIT_TRESHOLD)[0]:
                        if start < end - 1:
                            common_ranges_by_length[message_type][vec_len].append(
                                (rng_start + start, rng_start + end - 1))
                        start = end + 1

        # Now we merge the ranges together to get our candidate ranges
        common_intervals_by_type = {message_type: [] for message_type in common_ranges_by_length.keys()}
        """:type: dict[urh.signalprocessing.MessageType.MessageType, list[Interval]]"""

        for message_type in common_intervals_by_type.keys():
            msg_lens = sorted(common_ranges_by_length[message_type].keys())
            for interval in common_ranges_by_length[message_type][msg_lens[0]]:
                candidate = Interval(interval[0], interval[1])
                for other_len in msg_lens[1:]:
                    matches = []
                    for other_interval in common_ranges_by_length[message_type][other_len]:
                        oi = Interval(other_interval[0], other_interval[1])
                        if oi.overlaps_with(candidate):
                            candidate = candidate.find_common_interval(oi)
                            matches.append(candidate)

                    if not matches:
                        candidate = None
                        break
                    else:
                        candidate = Interval.find_greatest(matches)

                if candidate:
                    common_intervals_by_type[message_type].append(candidate)

        # Now we have the common intervals and need to check which one is the length
        for message_type, intervals in common_intervals_by_type.items():
            assert isinstance(message_type, MessageType)
            # Exclude Synchronization (or preamble if not present) from length calculation
            sync_lbl = self.find_lbl_function_in(FieldType.Function.SYNC, message_type)
            if sync_lbl:
                sync_len = self.__nbits2bytes(sync_lbl.end)
            else:
                preamble_lbl = self.find_lbl_function_in(FieldType.Function.PREAMBLE, message_type)
                sync_len = self.__nbits2bytes(preamble_lbl.end) if preamble_lbl is not None else 0

            scores = defaultdict(int)
            weights = {-4: 1, -3: 2, -2: 3, -1: 4, 0: 5}

            for common_interval in intervals:
                for msg in messages_by_type[message_type]:
                    bits = msg.decoded_bits
                    byte_len = self.__nbits2bytes(len(bits)) - sync_len
                    start, end = common_interval.start, common_interval.end
                    for byte_start in range(start, end, 8):
                        byte_end = byte_start + 8 if byte_start + 8 <= end else end
                        try:
                            byte = int("".join(["1" if bit else "0" for bit in bits[byte_start:byte_end]]), 2)
                            diff = byte - byte_len
                            if diff in weights:
                                scores[(byte_start, byte_end)] += weights[diff]
                        except ValueError:
                            pass  # Byte_end or byte_start was out of bits --> too close on the end

            try:
                start, end = max(scores, key=scores.__getitem__)
                if not any((lbl.type.function == FieldType.Function.LENGTH or lbl.name == "Length") and lbl.auto_created
                           for lbl in message_type):
                    message_type.add_protocol_label(start=start, end=end - 1, name=self.length_field_name,
                                                    auto_created=True, type=self.length_field_type)
            except ValueError:
                continue

    def __nbits2bytes(self, nbits):
        return int(math.ceil(nbits / 8))

    @staticmethod
    def find_lbl_function_in(function: FieldType.Function, message_type: MessageType) -> ProtocolLabel:
        return next((lbl for lbl in message_type if lbl.type and lbl.type.function == function), None)
