from urh.awre.components.Component import Component

class Address(Component):
    def __init__(self, participant_lut, participant_cluster, priority=2, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)
        self.participant_cluster = participant_cluster
        self.participant_lut = participant_lut

    def _py_find_field(self, bitvectors, column_ranges, rows):
        equal_ranges_per_participant = dict()
    #    for p in self.participant_cluster:
    #        equal_ranges = self._find_equal_ranges(self.participant_cluster[p], bitvectors=bitvectors, column_ranges=column_ranges,
    #                                                   rows=[row for row in rows if self.participant_lut[row] == p])
    #        equal_ranges_per_participant[p] = equal_ranges

     #   for key in sorted(equal_ranges_per_participant):
     #       for l in sorted(equal_ranges_per_participant[key]):
     #           print(l, equal_ranges_per_participant[key][l])

        raise NotImplementedError("Todo")