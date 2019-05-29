import itertools
import math
from array import array
from collections import defaultdict, Counter

import numpy as np

from urh.awre.CommonRange import CommonRange
from urh.awre.engines.Engine import Engine
from urh.cythonext import awre_util
from urh.util.Logger import logger


class AddressEngine(Engine):
    def __init__(self, msg_vectors, participant_indices, known_participant_addresses: dict = None,
                 already_labeled: list = None, src_field_present=False):
        """

        :param msg_vectors: Message data behind synchronization
        :type msg_vectors: list of np.ndarray
        :param participant_indices: list of participant indices
                                    where ith position holds participants index for ith messages
        :type participant_indices: list of int
        """
        assert len(msg_vectors) == len(participant_indices)

        self.minimum_score = 0.1

        self.msg_vectors = msg_vectors
        self.participant_indices = participant_indices
        self.already_labeled = []

        self.src_field_present = src_field_present

        if already_labeled is not None:
            for start, end in already_labeled:
                # convert it to hex
                self.already_labeled.append((int(math.ceil(start / 4)), int(math.ceil(end / 4))))

        self.message_indices_by_participant = defaultdict(list)
        for i, participant_index in enumerate(self.participant_indices):
            self.message_indices_by_participant[participant_index].append(i)

        if known_participant_addresses is None:
            self.known_addresses_by_participant = dict()  # type: dict[int, np.ndarray]
        else:
            self.known_addresses_by_participant = known_participant_addresses  # type: dict[int, np.ndarray]

    @staticmethod
    def cross_swap_check(rng1: CommonRange, rng2: CommonRange):
        return (rng1.start == rng2.start + rng1.length or rng1.start == rng2.start - rng1.length) \
               and rng1.value.tobytes() == rng2.value.tobytes()

    @staticmethod
    def ack_check(rng1: CommonRange, rng2: CommonRange):
        return rng1.start == rng2.start and rng1.length == rng2.length and rng1.value.tobytes() != rng2.value.tobytes()

    def find(self):
        addresses_by_participant = {p: [addr.tostring()] for p, addr in self.known_addresses_by_participant.items()}
        addresses_by_participant.update(self.find_addresses())
        self._debug("Addresses by participant", addresses_by_participant)

        # Find the address candidates by participant in messages
        ranges_by_participant = defaultdict(list)  # type: dict[int, list[CommonRange]]

        addresses = [np.array(np.frombuffer(a, dtype=np.uint8))
                     for address_list in addresses_by_participant.values()
                     for a in address_list]

        already_labeled_cols = array("L", [e for rng in self.already_labeled for e in range(*rng)])

        # Find occurrences of address candidates in messages and create common ranges over matching positions
        for i, msg_vector in enumerate(self.msg_vectors):
            participant = self.participant_indices[i]
            for address in addresses:
                for index in awre_util.find_occurrences(msg_vector, address, already_labeled_cols):
                    common_ranges = ranges_by_participant[participant]
                    rng = next((cr for cr in common_ranges if cr.matches(index, address)), None)  # type: CommonRange
                    if rng is not None:
                        rng.message_indices.add(i)
                    else:
                        common_ranges.append(CommonRange(index, len(address), address,
                                                         message_indices={i},
                                                         range_type="hex"))

        num_messages_by_participant = defaultdict(int)
        for participant in self.participant_indices:
            num_messages_by_participant[participant] += 1

        # Look for cross swapped values between participant clusters
        for p1, p2 in itertools.combinations(ranges_by_participant, 2):
            ranges1_set, ranges2_set = set(ranges_by_participant[p1]), set(ranges_by_participant[p2])

            for rng1, rng2 in itertools.product(ranges_by_participant[p1], ranges_by_participant[p2]):
                if rng1 in ranges2_set and rng2 in ranges1_set:
                    if self.cross_swap_check(rng1, rng2):
                        rng1.score += len(rng2.message_indices) / num_messages_by_participant[p2]
                        rng2.score += len(rng1.message_indices) / num_messages_by_participant[p1]
                    elif self.ack_check(rng1, rng2):
                        # Add previous score in divisor to add bonus to ranges that apply to all messages
                        rng1.score += len(rng2.message_indices) / (num_messages_by_participant[p2] + rng1.score)
                        rng2.score += len(rng1.message_indices) / (num_messages_by_participant[p1] + rng2.score)

        if len(ranges_by_participant) == 1 and not self.src_field_present:
            for p, ranges in ranges_by_participant.items():
                for rng in sorted(ranges):
                    try:
                        if np.array_equal(rng.value, self.known_addresses_by_participant[p]):
                            # Only one participant in this iteration and address already known -> Highscore
                            rng.score = 1
                            break  # Take only the first (leftmost) range
                    except KeyError:
                        pass

        high_scored_ranges_by_participant = defaultdict(list)

        address_length = self.__estimate_address_length(ranges_by_participant)

        # Get highscored ranges by participant
        for participant, common_ranges in ranges_by_participant.items():
            # Sort by negative score so ranges with highest score appear first
            # Secondary sort by tuple to ensure order when ranges have same score
            sorted_ranges = sorted(filter(lambda cr: cr.score > self.minimum_score, common_ranges),
                                   key=lambda cr: (-cr.score, cr))
            if len(sorted_ranges) == 0:
                addresses_by_participant[participant] = dict()
                continue

            addresses_by_participant[participant] = {a for a in addresses_by_participant.get(participant, [])
                                                     if len(a) == address_length}

            for rng in filter(lambda r: r.length == address_length, sorted_ranges):
                rng.score = min(rng.score, 1.0)
                high_scored_ranges_by_participant[participant].append(rng)

        # Now we find the most probable address for all participants
        self.__assign_participant_addresses(addresses_by_participant, high_scored_ranges_by_participant)

        # Eliminate participants for which we could not assign an address
        for participant, address in addresses_by_participant.copy().items():
            if address is None:
                del addresses_by_participant[participant]

        # Now we can separate SRC and DST
        for participant, ranges in high_scored_ranges_by_participant.items():
            try:
                address = addresses_by_participant[participant]
            except KeyError:
                high_scored_ranges_by_participant[participant] = []
                continue

            result = []

            for rng in sorted(ranges, key=lambda r: r.score, reverse=True):
                rng.field_type = "source address" if rng.value.tostring() == address else "destination address"
                if len(result) == 0:
                    result.append(rng)
                else:
                    subset = next((r for r in result if rng.message_indices.issubset(r.message_indices)), None)
                    if subset is not None:
                        if rng.field_type == subset.field_type:
                            # Avoid adding same address type twice
                            continue

                        if rng.length != subset.length or (rng.start != subset.end + 1 and rng.end + 1 != subset.start):
                            # Ensure addresses are next to each other
                            continue

                    result.append(rng)

            high_scored_ranges_by_participant[participant] = result

        self.__find_broadcast_fields(high_scored_ranges_by_participant, addresses_by_participant)

        result = [rng for ranges in high_scored_ranges_by_participant.values() for rng in ranges]
        # If we did not find a SRC address, lower the score a bit,
        # so DST fields do not win later e.g. again length fields in case of tie
        if not any(rng.field_type == "source address" for rng in result):
            for rng in result:
                rng.score *= 0.95

        return result

    def __estimate_address_length(self, ranges_by_participant: dict):
        """
        Estimate the address length which is assumed to be the same for all participants

        :param ranges_by_participant:
        :return:
        """
        address_lengths = []
        for participant, common_ranges in ranges_by_participant.items():
            sorted_ranges = sorted(filter(lambda cr: cr.score > self.minimum_score, common_ranges),
                                   key=lambda cr: (-cr.score, cr))

            max_scored = [r for r in sorted_ranges if r.score == sorted_ranges[0].score]

            # Prevent overestimation of address length by looking for substrings
            for rng in max_scored[:]:
                same_message_rng = [r for r in sorted_ranges
                                    if r not in max_scored and r.score > 0 and r.message_indices == rng.message_indices]

                if len(same_message_rng) > 1 and all(
                        r.value.tobytes() in rng.value.tobytes() for r in same_message_rng):
                    # remove the longer range and add the smaller ones
                    max_scored.remove(rng)
                    max_scored.extend(same_message_rng)

            possible_address_lengths = [r.length for r in max_scored]

            # Count possible address lengths.
            frequencies = Counter(possible_address_lengths)
            # Take the most common one. On tie, take the shorter one
            try:
                addr_len = max(frequencies, key=lambda x: (frequencies[x], -x))
                address_lengths.append(addr_len)
            except ValueError:  # max() arg is an empty sequence
                pass

        # Take most common address length of participants, to ensure they all have same address length
        counted = Counter(address_lengths)
        try:
            address_length = max(counted, key=lambda x: (counted[x], -x))
            return address_length
        except ValueError:  # max() arg is an empty sequence
            return 0

    def __assign_participant_addresses(self, addresses_by_participant, high_scored_ranges_by_participant):
        scored_participants_addresses = dict()
        for participant in addresses_by_participant:
            scored_participants_addresses[participant] = defaultdict(int)

        for participant, addresses in addresses_by_participant.items():
            if participant in self.known_addresses_by_participant:
                address = self.known_addresses_by_participant[participant].tostring()
                scored_participants_addresses[participant][address] = 9999999999
                continue

            for i in self.message_indices_by_participant[participant]:
                matching = [rng for rng in high_scored_ranges_by_participant[participant]
                            if i in rng.message_indices and rng.value.tostring() in addresses]

                if len(matching) == 1:
                    address = matching[0].value.tostring()
                    # only one address, so probably a destination and not a source
                    scored_participants_addresses[participant][address] *= 0.9

                    # Since this is probably an ACK, the address is probably SRC of participant of previous message
                    if i > 0 and self.participant_indices[i - 1] != participant:
                        prev_participant = self.participant_indices[i - 1]
                        prev_matching = [rng for rng in high_scored_ranges_by_participant[prev_participant]
                                         if i - 1 in rng.message_indices and rng.value.tostring() in addresses]
                        if len(prev_matching) > 1:
                            for prev_rng in filter(lambda r: r.value.tostring() == address, prev_matching):
                                scored_participants_addresses[prev_participant][address] += prev_rng.score

                elif len(matching) > 1:
                    # more than one address, so there must be a source address included
                    for rng in matching:
                        scored_participants_addresses[participant][rng.value.tostring()] += rng.score

        minimum_score = 0.5
        taken_addresses = set()
        self._debug("Scored addresses", scored_participants_addresses)

        # If all participants have exactly one possible address and they all differ, we can assign them right away
        if all(len(addresses) == 1 for addresses in scored_participants_addresses.values()):
            all_addresses = [list(addresses)[0] for addresses in scored_participants_addresses.values()]
            if len(all_addresses) == len(set(all_addresses)):  # ensure all addresses are different
                for p, addresses in scored_participants_addresses.items():
                    addresses_by_participant[p] = list(addresses)[0]
                return

        for participant, addresses in sorted(scored_participants_addresses.items()):
            try:
                # sort filtered results to prevent randomness for equal scores
                found_address = max(sorted(
                    filter(lambda a: a not in taken_addresses and addresses[a] >= minimum_score, addresses),
                    reverse=True
                ), key=addresses.get)
            except ValueError:
                # Could not assign address for this participant
                addresses_by_participant[participant] = None
                continue

            addresses_by_participant[participant] = found_address
            taken_addresses.add(found_address)

    def __find_broadcast_fields(self, high_scored_ranges_by_participant, addresses_by_participant: dict):
        """
        Last we check for messages that were sent to broadcast
          1. we search for messages that have a SRC address but no DST address
          2. we look at other messages that have this SRC field and find the corresponding DST position
          3. we evaluate the value of message without DST from 1 and compare these values with each other.
             if they match, we found the broadcast address
        :param high_scored_ranges_by_participant:
        :return:
        """
        if -1 in addresses_by_participant:
            # broadcast address is already known
            return

        broadcast_bag = defaultdict(list)  # type: dict[CommonRange, list[int]]
        for common_ranges in high_scored_ranges_by_participant.values():
            src_address_fields = sorted(filter(lambda r: r.field_type == "source address", common_ranges))
            dst_address_fields = sorted(filter(lambda r: r.field_type == "destination address", common_ranges))
            msg_with_dst = {i for dst_address_field in dst_address_fields for i in dst_address_field.message_indices}

            for src_address_field in src_address_fields:  # type: CommonRange
                msg_without_dst = {i for i in src_address_field.message_indices if i not in msg_with_dst}
                if len(msg_without_dst) == 0:
                    continue
                try:
                    matching_dst = next(dst for dst in dst_address_fields
                                        if all(i in dst.message_indices
                                               for i in src_address_field.message_indices - msg_without_dst))
                except StopIteration:
                    continue
                for msg in msg_without_dst:
                    broadcast_bag[matching_dst].append(msg)

        if len(broadcast_bag) == 0:
            return

        broadcast_address = None
        for dst, messages in broadcast_bag.items():
            for msg_index in messages:
                value = self.msg_vectors[msg_index][dst.start:dst.end + 1]
                if broadcast_address is None:
                    broadcast_address = value
                elif value.tobytes() != broadcast_address.tobytes():
                    # Address is not common across messages so it can't be a broadcast address
                    return

        addresses_by_participant[-1] = broadcast_address.tobytes()
        for dst, messages in broadcast_bag.items():
            dst.values.append(broadcast_address)
            dst.message_indices.update(messages)

    def find_addresses(self) -> dict:
        already_assigned = list(self.known_addresses_by_participant.keys())
        if len(already_assigned) == len(self.message_indices_by_participant):
            self._debug("Skipping find addresses as already known.")
            return dict()

        common_ranges_by_participant = dict()
        for participant, message_indices in self.message_indices_by_participant.items():
            # Cluster by length
            length_clusters = defaultdict(list)
            for i in message_indices:
                length_clusters[len(self.msg_vectors[i])].append(i)

            common_ranges_by_length = self.find_common_ranges_by_cluster(self.msg_vectors, length_clusters, range_type="hex")
            common_ranges_by_participant[participant] = []
            for ranges in common_ranges_by_length.values():
                common_ranges_by_participant[participant].extend(self.ignore_already_labeled(ranges,
                                                                                             self.already_labeled))

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
