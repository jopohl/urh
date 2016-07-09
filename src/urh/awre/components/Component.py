from abc import ABCMeta, abstractmethod
from urh.signalprocessing.ProtocoLabel import ProtocolLabel

class Component(metaclass=ABCMeta):
    """
    A component is the basic building block of our AWRE algorithm.
    A component can be a Preamble or Sync or Length Field finding routine.
    Components can have a priority which determines the order in which they are processed by the algorithm.
    Additionally, components can have a set of predecessors to define hard dependencies.
    """

    def __init__(self, priority=0, predecessors=None):
        """

        :param priority: Priority for this Component. 0 is highest priority
        :type priority: int
        :param predecessors: List of preceding components, that need to be run before this one
        :type predecessors: list of Component or None
        """
        self.priority = abs(priority)
        self.predecessors = predecessors if isinstance(predecessors, list) else []
        """:type: list of Component """

    @abstractmethod
    def find_field(self, data) -> ProtocolLabel:
        """
        Abstract method for subclasses to define the actual logic for finding a protocol field.
        Various strategies are possible e.g.:
        1) Heuristics e.g. for Preamble
        2) Scoring based e.g. for Length
        3) Fulltext search for addresses based on participant subgroups

        :param data: The data to be searched by this component
        :return: Highest probable label for this field
        """
        pass