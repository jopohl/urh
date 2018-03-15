from collections import defaultdict

import numpy as np

from urh.awre.engines.Engine import Engine


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

    def find_addresses(self):
        message_indices_by_participant = defaultdict(list)
        for i, participant_index in enumerate(self.participant_indices):
            message_indices_by_participant[participant_index].append(i)

        common_ranges_by_participant = self.find_common_ranges_by_cluster(self.bitvectors,
                                                                          message_indices_by_participant,
                                                                          range_type="hex")

        self._debug("Common ranges by participant:", common_ranges_by_participant)
        # Here we have candidate ranges
        # The ranges may be too long if they have e.g. common destination addresses



