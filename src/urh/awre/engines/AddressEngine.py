import itertools
from collections import defaultdict

import numpy as np

from urh.awre.CommonRange import CommonRange
from urh.awre.engines.Engine import Engine
from urh.cythonext import awre_util
from urh.util.Logger import logger


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
        self.message_indices_by_participant = defaultdict(list)
        for i, participant_index in enumerate(self.participant_indices):
            self.message_indices_by_participant[participant_index].append(i)

        self.known_addresses_by_participant = dict()  # type: dict[int, np.ndarray]

        self.range_type = range_type

    @staticmethod
    def cross_swap_check(rng1: CommonRange, rng2: CommonRange):
        return (rng1.start == rng2.start + rng1.length or rng1.start == rng2.start - rng1.length) \
               and rng1.value_str == rng2.value_str

    @staticmethod
    def ack_check(rng1: CommonRange, rng2: CommonRange):
        return (rng1.start == rng2.start and rng1.length == rng2.length) and rng1.value_str != rng2.value_str

    def find(self):
        addresses_by_participant = {p: [addr.tostring()] for p, addr in self.known_addresses_by_participant.items()}
        addresses_by_participant.update(self.find_addresses())
        self._debug("Addresses by participant", addresses_by_participant)

        # Find the address candidates by participant in messages
        ranges_by_participant = defaultdict(list)  # type: dict[int, list[CommonRange]]

        addresses = [np.array(np.frombuffer(a, dtype=np.uint8))
                     for address_list in addresses_by_participant.values()
                     for a in address_list]

        for i, msg_vector in enumerate(self.msg_vectors):
            participant = self.participant_indices[i]
            for address in addresses:
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
            addresses_by_participant[participant] = {a for a in addresses_by_participant[participant]
                                                     if len(a) == addr_len}

            for rng in filter(lambda r: r.length == addr_len, sorted_ranges):
                # Here we have ranges sorted by score. We assign destination address to first (highest scored) range
                # because it is more likely for a message to only have a destination address than only a source address
                rng.field_type = "address"
                rng.score = min(rng.score, 1.0)
                high_scored_ranges_by_participant[participant].append(rng)

        # Now we find the most probable address for all participants
        self.__assign_participant_addresses(addresses_by_participant, high_scored_ranges_by_participant)

        # Now we can separate SRC and DST
        for participant, ranges in high_scored_ranges_by_participant.items():
            address = addresses_by_participant[participant]
            for rng in ranges:
                rng.field_type = "source address" if rng.value.tostring() == address else "destination address"

        return high_scored_ranges_by_participant

    def __assign_participant_addresses(self, addresses_by_participant, high_scored_ranges_by_participant):
        scored_participants_addresses = dict()
        for participant, addresses in addresses_by_participant.items():
            scored_participants_addresses[participant] = defaultdict(int)
            for i in self.message_indices_by_participant[participant]:
                matching = [rng for rng in high_scored_ranges_by_participant[participant]
                            if i in rng.message_indices]

                if len(matching) == 1:
                    # only one address, so probably a destination and not a source
                    scored_participants_addresses[participant][matching[0].value.tostring()] -= 1
                elif len(matching) > 1:
                    # more than one address, so there must be a source address included
                    for address in {rng.value.tostring() for rng in matching}:
                        scored_participants_addresses[participant][address] += 1

        for participant, addresses in scored_participants_addresses.items():
            found_address = max(addresses, key=addresses.get)
            if len(addresses_by_participant[participant]) == 1:
                assigned = list(addresses_by_participant[participant])[0]
                addresses_by_participant[participant] = assigned
                if found_address != assigned:
                    logger.warning("Found a different address ({}) for participant {} than the assigned one {}".format(
                        found_address, participant, assigned))
            else:
                addresses_by_participant[participant] = found_address

    def find_addresses(self) -> dict:
        already_assigned = list(self.known_addresses_by_participant.keys())
        if len(already_assigned) == len(self.message_indices_by_participant):
            return dict()

        common_ranges_by_participant = dict()
        for participant, msg_indices in self.message_indices_by_participant.items():
            common_ranges_by_participant[participant] = self.find_common_ranges_exhaustive(self.msg_vectors,
                                                                                           msg_indices,
                                                                                           range_type="hex"
                                                                                           )

        self._debug("Common ranges by participant:", common_ranges_by_participant)

        result = defaultdict(set)
        participants = sorted(common_ranges_by_participant)  # type: list[int]

        if len(participants) < 2:
            return result

        # If we already know the address length we do not need to bother with other candidates
        if len(already_assigned) > 0:
            addr_len = len(self.known_addresses_by_participant[already_assigned[0]])
            if any(len(self.known_addresses_by_participant[i]) != addr_len for i in already_assigned):
                logger.warning("Addresses do not have a common length. Assuming length of {}".format(addr_len))
        else:
            addr_len = None

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
                    if addr_len is not None and len(val) != addr_len:
                        continue
                    if not p1_already_assigned and not p2_already_assigned:
                        result[p1].add(val.tostring())
                        result[p2].add(val.tostring())
                    elif p1_already_assigned and val.tostring() != self.known_addresses_by_participant[p1].tostring():
                        result[p2].add(val.tostring())
                    elif p2_already_assigned and val.tostring() != self.known_addresses_by_participant[p2].tostring():
                        result[p1].add(val.tostring())
        return result
