from urh.awre.components.Component import Component

class SequenceNumber(Component):
    def __init__(self, priority=2, predecessors=None, enabled=True, backend=None):
        super().__init__(priority, predecessors, enabled, backend)

    def _py_find_field(self, bitvectors, exclude_indices):
        raise NotImplementedError("Todo")