from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.FieldType import FieldType

class SimulatorProtocolLabel(ProtocolLabel):
    def __init__(self, name: str, start: int, end: int, color_index: int, type:FieldType=None):
        super().__init__(name, start, end, color_index, type=type)

    def __hash__(self):
        return object.__hash__(self)

    def __eq__(self, other):
        return object.__eq__(self, other)