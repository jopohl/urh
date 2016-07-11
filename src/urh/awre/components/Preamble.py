from urh import constants
from urh.awre.components.Component import Component

class Preamble(Component):
    def __init__(self, priority=0, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)

    def _py_find_field(self, bitvectors, exclude_indices):


        preamble_ends = [pre_end for pre_end in (self.__find_preamble_end(bv, exclude_indices) for bv in bitvectors) if pre_end]

        if len(preamble_ends) == 0:
            return 0, 0

        preamble_end = max(preamble_ends, key=preamble_ends.count)
        return 0, preamble_end


    def __find_preamble_end(self, bitvector, exclude_indices): # TODO Consider exlcude indices
        try:
            start = 0 if bitvector[0] else 1
            for i in (range(start, len(bitvector), constants.SHORTEST_PREAMBLE_IN_BITS)):
                for j in range(0, constants.SHORTEST_PREAMBLE_IN_BITS, 2):
                    if not(bitvector[i+j] and not bitvector[i+j+1]):
                        return i - 1 if i - 1 >= 0 else None

            return len(bitvector) - 1 if len(bitvector) - 1 >= 0 else None

        except IndexError:
            return None