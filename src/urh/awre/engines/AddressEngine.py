from collections import defaultdict

import numpy as np

from urh.awre.engines.Engine import Engine
import itertools

class AddressEngine(Engine):
    def __init__(self, bitvectors, participant_indices):
        """

        :param bitvectors: Bitvectors behind synchronization
        :type bitvectors: list of np.ndarray
        :param participant_indices: list of participant indices
                                    where ith position holds participants index for ith messages
        :type participant_indices: list of int
        """
        assert len(bitvectors) == len(participant_indices)

        self.bitvectors = bitvectors
        self.participant_indices = participant_indices

    def find(self):
        # TODO
        return dict()

    def find_addresses(self) -> dict:
        message_indices_by_participant = defaultdict(list)
        for i, participant_index in enumerate(self.participant_indices):
            message_indices_by_participant[participant_index].append(i)

        common_ranges_by_participant = self.find_common_ranges_by_cluster(self.bitvectors,
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
            # common ranges are not merged yet, so there is only one element in values
            values1 = [cr.value for cr in common_ranges_by_participant[p1]]
            values2 = [cr.value for cr in common_ranges_by_participant[p2]]
            for seq1, seq2 in itertools.product(values1, values2):
                for sub_seq in self.find_longest_common_sub_sequences(seq1, seq2):
                    result[p1].append(sub_seq)
                    result[p2].append(sub_seq)

        return result
