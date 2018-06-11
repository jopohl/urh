import copy
import math
from collections import defaultdict, Counter

import numpy as np

from urh.awre.CommonRange import CommonRange, EmptyCommonRange, CommonRangeContainer
from urh.awre.Preprocessor import Preprocessor
from urh.awre.engines.AddressEngine import AddressEngine
from urh.awre.engines.LengthEngine import LengthEngine
from urh.awre.engines.SequenceNumberEngine import SequenceNumberEngine
from urh.cythonext import awre_util


class FormatFinder(object):
    MIN_MESSAGES_PER_CLUSTER = 2

    def __init__(self, protocol, participants=None, shortest_field_length=None):
        """

        :type protocol: urh.signalprocessing.ProtocolAnalyzer.ProtocolAnalyzer
        :param participants:
        """
        if participants is not None:
            protocol.auto_assign_participants(participants)
        self.preamble_starts, self.preamble_lengths, sync_len = Preprocessor(protocol.messages).preprocess()
        self.sync_ends = self.preamble_starts + self.preamble_lengths + sync_len

        if shortest_field_length is None:
            self.shortest_field_length = 8 if sync_len >= 8 else 4 if sync_len >= 4 else 1

        n = self.shortest_field_length
        for i, value in enumerate(self.sync_ends):
            # In doubt it is better to under estimate the sync end
            self.sync_ends[i] = n * max(int(math.floor((value - self.preamble_starts[i]) / n)), 1) + self.preamble_starts[i]

            if self.sync_ends[i] - self.preamble_starts[i] < self.preamble_lengths[i]:
                self.preamble_lengths[i] = self.sync_ends[i] - self.preamble_starts[i]

        self.messages = protocol.messages
        self.bitvectors = self.get_bitvectors_from_messages(protocol.messages, self.sync_ends)
        self.hexvectors = self.get_hexvectors(self.bitvectors)
        self.xor_matrix = self.build_xor_matrix()
        participants = list(sorted(set(msg.participant for msg in protocol.messages)))
        self.participant_indices = [participants.index(msg.participant) for msg in protocol.messages]

        self.engines = [
            LengthEngine(self.bitvectors),
            AddressEngine(self.hexvectors, self.participant_indices),
            SequenceNumberEngine(self.bitvectors)
        ]

        self.label_set = set()
        self.message_types = [[]]

    def update_message_types(self, common_ranges: list):
        if not common_ranges:
            return

        # We need at least as many message types as there are field types.
        # E.g. if we have three length fields with different ranges we need at least three message types
        num_message_types = max(Counter(rng.field_type for rng in common_ranges).values())
        while len(self.message_types) < num_message_types:
            self.message_types.append([])

        # Now we update the message types or add new ones if necessary
        for merged_rng in common_ranges:
            # Find a message type that not has already a field in this range
            try:
                mt = next(
                    mt for mt in self.message_types
                    if not any(merged_rng.overlaps_with(rng) for rng in mt)
                    and not any(rng.field_type == merged_rng.field_type for rng in mt)
                )
            except StopIteration:
                self.message_types.append([])
                mt = self.message_types[-1]
            mt.append(merged_rng)

    def perform_iteration(self):
        for engine in self.engines:
            high_scored_ranges = []  # type: list[CommonRange]
            high_scored_ranges.extend(engine.find())
            merged_ranges = self.merge_common_ranges(high_scored_ranges)
            self.label_set.update(merged_ranges)
        self.message_types = self.create_message_types(self.label_set)
        self.message_types = self.retransform_message_types(self.message_types, self.preamble_starts,
                                                            self.preamble_lengths, self.sync_ends)

    def build_xor_matrix(self):
        return awre_util.build_xor_matrix(self.bitvectors)

    @staticmethod
    def merge_common_ranges(common_ranges):
        """
        Merge common ranges if possible

        :type common_ranges: list of CommonRange
        :rtype: list of CommonRange
        """
        merged_ranges = []
        for common_range in common_ranges:
            assert isinstance(common_range, CommonRange)
            try:
                same_range = next(rng for rng in merged_ranges
                                  if rng.bit_start == common_range.bit_start
                                  and rng.bit_end == common_range.bit_end
                                  and rng.field_type == common_range.field_type)
                same_range.values.extend(common_range.values)
                same_range.message_indices.update(common_range.message_indices)
            except StopIteration:
                merged_ranges.append(common_range)

        return merged_ranges

    @staticmethod
    def get_hexvectors(bitvectors: list):
        result = []

        for bitvector in bitvectors:
            hexvector = np.empty(int(math.ceil(len(bitvector) / 4)), dtype=np.uint8)
            for i in range(0, len(hexvector)):
                bits = bitvector[4*i:4*(i+1)]
                hexvector[i] = int("".join(map(str, bits)), 2)
            result.append(hexvector)

        return result

    @staticmethod
    def get_bitvectors_from_messages(messages: list, sync_ends: np.ndarray = None):
        if sync_ends is None:
            sync_ends = defaultdict(lambda: None)

        return [np.array(msg.decoded_bits[sync_ends[i]:], dtype=np.int8) for i, msg in enumerate(messages)]

    @staticmethod
    def get_bitvectors_by_participant(protocol) -> dict:
        result = defaultdict(list)
        for msg in protocol.messages:
            result[msg.participant].append(np.array(msg.decoded_bits, dtype=np.int8))
        return result

    @staticmethod
    def create_message_types(label_set: set, num_messages: int=None):
        """

        :param label_set:
        :param num_messages:
        :return:
        :rtype: list of CommonRangeContainer
        """
        if num_messages is None:
            message_indices = sorted(set(i for rng in label_set for i in rng.message_indices))
        else:
            message_indices = range(num_messages)

        result = []
        for i in message_indices:
            labels = sorted(set(rng for rng in label_set if i in rng.message_indices
                         and not isinstance(rng, EmptyCommonRange)))

            container = next((container for container in result if container.has_same_ranges(labels)), None)
            if container is None:
                result.append(CommonRangeContainer(labels, message_indices={i}))
            else:
                container.message_indices.add(i)

        result = FormatFinder.handle_overlapping_conflict(result)

        return result

    @staticmethod
    def handle_overlapping_conflict(containers):
        """
        Handle overlapping conflicts for a list of CommonRangeContainers

        :type containers: list of CommonRangeContainer
        :return:
        """
        result = []
        for container in containers:
            if not container.ranges_overlap:
                result.append(container)
                continue

            result.append(FormatFinder.__handle_container_overlapping_conflict(container))

        return result

    @staticmethod
    def __handle_container_overlapping_conflict(container: CommonRangeContainer):
        """
        Handle overlapping conflict for a CommRangeContainer.
        We can assert that all labels in the container share the same message indices
        because we partitioned them in a step before.
        If two or more labels overlap we have three ways to resolve the conflict:

        1. Choose the range with the highest score
        2. If multiple ranges overlap choose the ranges that maximize the overall (cumulated) score
        3. If the overlapping is very small i.e. only 1 or 2 bits we can adjust the start/end of the conflicting ranges

        The ranges inside the container _must_ be sorted i.e. the range with lowest start must be at front

        :param container:
        :return:
        """
        partitions = []  # type: list[list[CommonRange]]
        # partition the container into overlapping partitions
        # results in something like [[A], [B,C], [D], [E,F,G]]] where B and C and E, F, G are overlapping
        for cur_rng in container:
            if len(partitions) == 0:
                partitions.append([cur_rng])
                continue

            last_rng = partitions[-1][-1]  # type: CommonRange
            if cur_rng.overlaps_with(last_rng):
                partitions[-1].append(cur_rng)
            else:
                partitions.append([cur_rng])

        # Todo: Adjust start/end of conflicting ranges if overlapping is very small (i.e. 1 or 2 bits)

        result = []
        # Go through these partitions and handle overlapping conflicts
        for partition in partitions:
            possible_solutions = []
            for i, rng in enumerate(partition):
                # Append every range to this solution that does not overlap with current rng
                solution = [rng] + [r for r in partition[i+1:] if not rng.overlaps_with(r)]
                possible_solutions.append(solution)

            best_solution = max(possible_solutions, key=lambda sol: sum(r.score for r in sol))
            result.extend(best_solution)

        return CommonRangeContainer(result, message_indices=copy.copy(container.message_indices))

    @staticmethod
    def retransform_message_types(message_types, preamble_starts, preamble_lengths, sync_ends):
        """
        Retransform the message types into original message space.
        That is, consider preamble and sync information.

        1. We need to add sync end of a message to the corresponding ranges
        2. Furthermore, we need to create a new message type if messages of label have different sync ends
        3. While we are on it, we create Preamble and Sync ranges in this method

        :type message_types: list of CommonRangeContainer
        :type preamble_starts: np.ndarray
        :type preamble_lengths: np.ndarray
        :type sync_ends: np.ndarray
        :return:
        """
        assert len(preamble_starts) == len(preamble_lengths) == len(sync_ends)

        result = []
        for i, sync_end in enumerate(sync_ends):
            preamble = CommonRange(preamble_starts[i], preamble_lengths[i], field_type="preamble")
            preamble_end = preamble_starts[i] + preamble_lengths[i]
            sync = CommonRange(preamble_end, sync_end - preamble_end, field_type="synchronization")

            mt = next((copy.deepcopy(mt) for mt in message_types if i in mt.message_indices),
                      CommonRangeContainer([], set()))

            mt.message_indices = {i}
            for rng in mt:
                rng.sync_end = sync_end

            mt.add_ranges([preamble, sync])

            existing = next((m for m in result if mt.has_same_ranges(list(m))), None)  # type: CommonRange
            if existing is None:
                result.append(mt)
            else:
                existing.message_indices.add(i)

        return result