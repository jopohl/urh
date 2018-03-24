import itertools
from collections import defaultdict

import numpy as np

from urh.awre.CommonRange import CommonRange
from urh.awre.engines.Engine import Engine
from urh.cythonext import awre_util


class AddressEngine(Engine):
    def __init__(self, msg_vectors, participant_indices, range_type="hex"):
        """

        :param msg_vectors: Message data behind synchronization
        :type msg_vectors: list of np.ndarray
        :param participant_indices: list of participant indices
                                    where ith position holds participants index for ith messages
        :type participant_indices: list of int
        """
        assert len(msg_vectors) == len(participant_indices)

        self.msg_vectors = msg_vectors
        self.participant_indices = participant_indices

        self.addresses_by_participant = dict()  # type: dict[int, np.ndarray]

        self.range_type = range_type

    @staticmethod
    def cross_swap_check(rng1: CommonRange, rng2: CommonRange):
        return (rng1.start == rng2.start + rng1.length or rng1.start == rng2.start - rng1.length) \
               and rng1.value_str == rng2.value_str

    @staticmethod
    def ack_check(rng1: CommonRange, rng2: CommonRange):
        return (rng1.start == rng2.start and rng1.length == rng2.length) and rng1.value_str != rng2.value_str

    def find(self):
        self.addresses_by_participant.update(self.find_addresses())
        self._debug("Addresses by participant", self.addresses_by_participant)

        # Find the address candidates by participant in messages
        ranges_by_participant = defaultdict(list)  # type: dict[int, list[CommonRange]]
        for i, msg_vector in enumerate(self.msg_vectors):
            participant = self.participant_indices[i]
            for address in self.addresses_by_participant.get(participant, []):
                for index in awre_util.find_occurrences(msg_vector, address):
                    common_ranges = ranges_by_participant[participant]
                    rng = next((cr for cr in common_ranges if cr.matches(index, address)), None)  # type: CommonRange
                    if rng is not None:
                        rng.message_indices.add(i)
                    else:
                        common_ranges.append(CommonRange(index, len(address), address,
                                                         message_indices={i},
                                                         range_type=self.range_type))

        num_messages_by_participant = defaultdict(int)
        for participant in self.participant_indices:
            num_messages_by_participant[participant] += 1

        # Look for cross swapped values between participant clusters
        for p1, p2 in itertools.combinations(ranges_by_participant, 2):
            for rng1, rng2 in itertools.product(ranges_by_participant[p1], ranges_by_participant[p2]):
                if rng1 in ranges_by_participant[p2] and rng2 in ranges_by_participant[p1]:
                    if self.cross_swap_check(rng1, rng2):
                        rng1.score += len(rng1.message_indices) / num_messages_by_participant[p1]
                        rng2.score += len(rng2.message_indices) / num_messages_by_participant[p2]
                    elif self.ack_check(rng1, rng2):
                        rng1.score += len(rng1.message_indices) / num_messages_by_participant[p1]
                        rng2.score += len(rng2.message_indices) / num_messages_by_participant[p2]

        high_scored_ranges_by_participant = defaultdict(list)
        for participant, common_ranges in ranges_by_participant.items():
            # Sort by negative score so ranges with highest score appear first
            # Secondary sort by tuple to ensure order when ranges have same score
            sorted_ranges = sorted(filter(lambda cr: cr.score > 0.1, common_ranges), key=lambda cr: (-cr.score, cr))

            addr_len = sorted_ranges[0].length if len(sorted_ranges) > 0 else 0

            i = -1
            for rng in sorted_ranges:
                if rng.length != addr_len:
                    continue
                i += 1
                # Here we have ranges sorted by score. We assign destination address to first (highest scored) range
                # because it is more likely for a message to only have a destination address than only a source address
                rng.field_type = "destination address" if i % 2 == 0 else "source address"
                rng.score = min(rng.score, 1.0)
                high_scored_ranges_by_participant[participant].append(rng)

        print(high_scored_ranges_by_participant)

        return high_scored_ranges_by_participant

    def find_addresses(self) -> dict:
        message_indices_by_participant = defaultdict(list)
        for i, participant_index in enumerate(self.participant_indices):
            message_indices_by_participant[participant_index].append(i)

        already_assigned = self.addresses_by_participant.keys()
        if len(already_assigned) == len(message_indices_by_participant):
            return dict()

        common_ranges_by_participant = dict()
        for participant, msg_indices in message_indices_by_participant.items():
            common_ranges_by_participant[participant] = self.find_common_ranges_exhaustive(self.msg_vectors,
                                                                                           msg_indices,
                                                                                           range_type="hex"
                                                                                           )

        self._debug("Common ranges by participant:", common_ranges_by_participant)

        result = defaultdict(list)
        participants = sorted(common_ranges_by_participant)  # type: list[int]

        if len(participants) < 2:
            return result

        for p1, p2 in itertools.combinations(participants, 2):
            p1_already_assigned = p1 in already_assigned
            p2_already_assigned = p2 in already_assigned

            if p1_already_assigned and p2_already_assigned:
                continue

            # common ranges are not merged yet, so there is only one element in values
            values1 = [cr.value for cr in common_ranges_by_participant[p1]]
            values2 = [cr.value for cr in common_ranges_by_participant[p2]]
            for seq1, seq2 in itertools.product(values1, values2):
                lcs = self.find_longest_common_sub_sequences(seq1, seq2)
                vals = lcs if len(lcs) > 0 else [seq1, seq2]
                # Address candidate must be at least 2 values long
                for val in filter(lambda v: len(v) >= 2, vals):
                    if not p1_already_assigned:
                        result[p1].append(val)
                    if not p2_already_assigned:
                        result[p2].append(val)

        return result
