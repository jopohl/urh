from abc import ABCMeta
from collections import defaultdict

import numpy as np

from urh.signalprocessing.Interval import Interval
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

    def find_field(self, bitvectors, column_ranges, rows) -> ProtocolLabel:
        """
        Wrapper method selecting the backend to find the protocol field.
        Various strategies are possible e.g.:
        1) Heuristics e.g. for Preamble
        2) Scoring based e.g. for Length
        3) Fulltext search for addresses based on participant subgroups

        :param column_ranges: list of tuples of columns to search
        :type column_ranges: dict[int, list of tuple]
        :param bitvectors: The data to be searched by this component
        :return: Highest probable label for this field
        """
        try:
            if self.backend == self.Backend.python:
                start, end = self._py_find_field(bitvectors, column_ranges, rows)
            elif self.backend == self.Backend.cython:
                start, end = self._cy_find_field(bitvectors, column_ranges, rows)
            elif self.backend == self.Backend.plainc:
                start, end = self._c_find_field(bitvectors, column_ranges, rows)
            else:
                raise ValueError("Unsupported backend {}".format(self.backend))
        except NotImplementedError:
            logger.info("Skipped {} because not implemented yet".format(self.__class__.__name__))
            return None

        if start == end == 0:
            return None

        return ProtocolLabel(name=self.__class__.__name__, start=start, end=end - 1, val_type_index=0, color_index=None)

    def _py_find_field(self, bitvectors, column_ranges, rows):
        raise NotImplementedError()

    def _cy_find_field(self, bitvectors, column_ranges, rows):
        raise NotImplementedError()

    def _c_find_field(self, bitvectors, column_ranges, rows):
        raise NotImplementedError()