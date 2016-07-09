from urh.awre.components.Component import Component

class Synchronization(Component):
    def __init__(self, priority=1, predecessors=None):
        super().__init__(priority, predecessors)

    def find_field(self, data):
        raise NotImplementedError("Todo")