import numpy as np
import time

from urh.signalprocessing.FieldType import FieldType
from urh.util.Logger import logger

from urh.awre.components.Address import Address
from urh.awre.components.Component import Component
from urh.awre.components.Flags import Flags
from urh.awre.components.Length import Length
from urh.awre.components.Preamble import Preamble
from urh.awre.components.SequenceNumber import SequenceNumber
from urh.awre.components.Type import Type
from urh.cythonext import util

class FormatFinder(object):
    MIN_MESSAGES_PER_CLUSTER = 2 # If there is only one message per cluster it is not very significant

    def __init__(self, protocol, participants=None, field_types=None):
        """

        :type protocol: urh.signalprocessing.ProtocolAnalyzer.ProtocolAnalyzer
        :param participants:
        """
        if participants is not None:
            protocol.auto_assign_participants(participants)

        self.protocol = protocol
        self.bitvectors = [np.array(msg.decoded_bits, dtype=np.int8) for msg in self.protocol.messages]
        self.len_cluster = self.cluster_lengths()
        self.xor_matrix = self.build_xor_matrix()


        mt = self.protocol.message_types

        field_types = FieldType.load_from_xml() if field_types is None else field_types

        self.preamble_component = Preamble(fieldtypes=field_types, priority=0, messagetypes=mt)
        self.length_component = Length(fieldtypes=field_types, length_cluster=self.len_cluster, priority=1,
                                       predecessors=[self.preamble_component], messagetypes=mt)
        self.address_component = Address(fieldtypes=field_types, xor_matrix=self.xor_matrix, priority=2,
                                         predecessors=[self.preamble_component], messagetypes=mt)
        self.sequence_number_component = SequenceNumber(fieldtypes=field_types, priority=3,
                                                        predecessors=[self.preamble_component])
        self.type_component = Type(priority=4, predecessors=[self.preamble_component])
        self.flags_component = Flags(priority=5, predecessors=[self.preamble_component])

    def build_component_order(self):
        """
        Build the order of component based on their priority and predecessors

        :rtype: list of Component
        """
        present_components = [item for item in self.__dict__.values() if isinstance(item, Component) and item.enabled]
        result = [None] * len(present_components)
        used_prios = set()
        for component in present_components:
            index = component.priority % len(present_components)
            if index in used_prios:
                raise ValueError("Duplicate priority: {}".format(component.priority))
            used_prios.add(index)

            result[index] = component

        # Check if predecessors are valid
        for i, component in enumerate(result):
            if any(i < result.index(pre) for pre in component.predecessors):
                raise ValueError("Component {} comes before at least one of its predecessors".format(component))

        return result

    def perform_iteration(self):
        for component in self.build_component_order():
            # OPEN: Create new message types e.g. for addresses
            component.find_field(self.protocol.messages)

    def cluster_lengths(self):
        """
        This method clusters some bitvectors based on their length. An example output is

        2: [0.5, 1]
        4: [1, 0.75, 1, 1]

        Meaning there were two message lengths: 2 and 4 bit.
        (0.5, 1) means, the first bit was equal in 50% of cases (meaning maximum difference) and bit 2 was equal in all messages

        A simple XOR would not work as it would be error prone.

        :rtype: dict[int, tuple[np.ndarray, int]]
        """

        number_ones = dict()  # dict of tuple. 0 = number ones vector, 1 = number of blocks for this vector
        for vector in self.bitvectors:
            vec_len = 4 * (len(vector) // 4)
            if vec_len == 0:
                continue

            if vec_len not in number_ones:
                number_ones[vec_len] = [np.zeros(vec_len, dtype=int), 0]

            number_ones[vec_len][0] += vector[0:vec_len]
            number_ones[vec_len][1] += 1

        # Calculate the relative numbers and normalize the equalness so e.g. 0.3 becomes 0.7
        return {vl: (np.vectorize(lambda x: x if x >= 0.5 else 1 - x)(number_ones[vl][0] / number_ones[vl][1]))
                for vl in number_ones if number_ones[vl][1] >= self.MIN_MESSAGES_PER_CLUSTER}

    def build_xor_matrix(self):
        t = time.time()
        xor_matrix = util.build_xor_matrix(self.bitvectors)
        logger.debug("XOR matrix: {}s".format(time.time()-t))
        return xor_matrix
