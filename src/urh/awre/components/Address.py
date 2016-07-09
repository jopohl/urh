from urh.awre.components.Component import Component

class Address(Component):
    def __init__(self, priority=2, predecessors=None):
        super().__init__(priority, predecessors)

    def find_field(self, data):
        raise NotImplementedError("Todo")