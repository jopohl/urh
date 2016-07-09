from urh.awre.components.Component import Component

class Preamble(Component):
    def __init__(self, priority=0, predecessors=None):
        super().__init__(priority, predecessors)

    def find_field(self, data):
        raise NotImplementedError("Todo")