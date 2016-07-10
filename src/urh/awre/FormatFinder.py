from urh.awre.components.Address import Address
from urh.awre.components.Component import Component
from urh.awre.components.Flags import Flags
from urh.awre.components.Length import Length
from urh.awre.components.Preamble import Preamble
from urh.awre.components.SequenceNumber import SequenceNumber
from urh.awre.components.Synchronization import Synchronization
from urh.awre.components.Type import Type


class FormatFinder(object):
    def __init__(self):
        self.preamble_component = Preamble(priority=0)
        self.sync_component = Synchronization(priority=1, predecessors=[self.preamble_component])
        self.length_component = Length(priority=2, predecessors=[self.preamble_component, self.sync_component])
        self.address_component = Address(priority=3, predecessors=[self.preamble_component, self.sync_component])
        self.sequence_number_component = SequenceNumber(priority=4, predecessors=[self.preamble_component, self.sync_component])
        self.type_component = Type(priority=5, predecessors=[self.preamble_component, self.sync_component])
        self.flags_component = Flags(priority=6, predecessors=[self.preamble_component, self.sync_component])

    def build_component_order(self):
        """
        Build the order of component based on their priority and predecessors

        :rtype: list of Component
        """
        present_components = [item for item in self.__dict__.values() if isinstance(item, Component)]
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
