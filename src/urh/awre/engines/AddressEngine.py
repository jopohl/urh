from collections import defaultdict
from pprint import pprint

import numpy as np

from urh.awre.CommonRange import CommonRange
from urh.awre.engines.Engine import Engine
from urh.cythonext import awre_util
import itertools


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

    def find(self):
        self.addresses_by_participant.update(self.find_addresses())
        self._debug(self.addresses_by_participant)

        ranges_by_participant = defaultdict(list)  # type: dict[int, list[CommonRange]]
        for i, msg_vector in enumerate(self.msg_vectors):
            participant = self.participant_indices[i]
            for address in self.addresses_by_participant[participant]:
                for index in awre_util.find_occurrences(msg_vector, address):
                    common_ranges = ranges_by_participant[participant]
                    rng = next((cr for cr in common_ranges if cr.matches(index, address)), None)  # type: CommonRange
                    if rng is not None:
                        rng.message_indices.add(i)
                    else:
                        common_ranges.append(CommonRange(index, len(address), address, message_indices={i},
                                                         range_type=self.range_type))


        pprint(ranges_by_participant)



        # TODO
        return dict()

    def find_addresses(self) -> dict:
        message_indices_by_participant = defaultdict(list)
        for i, participant_index in enumerate(self.participant_indices):
            message_indices_by_participant[participant_index].append(i)

        already_assigned = self.addresses_by_participant.keys()
        if len(already_assigned) == len(message_indices_by_participant):
            return dict()

        common_ranges_by_participant = self.find_common_ranges_by_cluster(self.msg_vectors,
                                                                          message_indices_by_participant,
                                                                          range_type="hex")

        self._debug("Common ranges by participant:", common_ranges_by_participant)

        result = defaultdict(list)
        participants = sorted(common_ranges_by_participant)  # type: list[int]

        if len(participants) == 0:
            return result
        elif len(participants) == 1:
            participant = participants[0]
            result[participant] = [cr.values[0] for cr in common_ranges_by_participant[participant]]
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
                for sub_seq in self.find_longest_common_sub_sequences(seq1, seq2):
                    if not p1_already_assigned:
                        result[p1].append(sub_seq)

                    if not p2_already_assigned:
                        result[p2].append(sub_seq)

        return result
