from abc import ABCMeta

from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from enum import Enum

from urh.util.Logger import logger


class Component(metaclass=ABCMeta):
    """
    A component is the basic building block of our AWRE algorithm.
    A component can be a Preamble or Sync or Length Field finding routine.
    Components can have a priority which determines the order in which they are processed by the algorithm.
    Additionally, components can have a set of predecessors to define hard dependencies.
    """


    EQUAL_BIT_TRESHOLD = 0.9

    class Backend(Enum):
        python = 1
        cython = 2
        plainc = 3

    def __init__(self, priority=0, predecessors=None, enabled=True, backend=None):
        """

        :param priority: Priority for this Component. 0 is highest priority
        :type priority: int
        :param predecessors: List of preceding components, that need to be run before this one
        :type predecessors: list of Component or None
        """
        self.enabled = enabled
        self.backend = backend if backend is not None else self.Backend.python
        self.priority = abs(priority)
        self.predecessors = predecessors if isinstance(predecessors, list) else []
        """:type: list of Component """

    def find_field(self, messages):
        """
        Wrapper method selecting the backend to assign the protocol field.
        Various strategies are possible e.g.:
        1) Heuristics e.g. for Preamble
        2) Scoring based e.g. for Length
        3) Fulltext search for addresses based on participant subgroups

        :param messages: messages a field shall be searched for
        :type messages: list of Message
        """
        try:
            if self.backend == self.Backend.python:
                self._py_find_field(messages)
            elif self.backend == self.Backend.cython:
                self._cy_find_field(messages)
            elif self.backend == self.Backend.plainc:
                self._c_find_field(messages)
            else:
                raise ValueError("Unsupported backend {}".format(self.backend))
        except NotImplementedError:
            logger.info("Skipped {} because not implemented yet".format(self.__class__.__name__))

    def _py_find_field(self, messages):
        raise NotImplementedError()

    def _cy_find_field(self, messages):
        raise NotImplementedError()

    def _c_find_field(self, messages):
        raise NotImplementedError()