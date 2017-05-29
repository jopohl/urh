from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorMessage import SimulatorMessage

class SimulatorProtocolLabel(ProtocolLabel, SimulatorItem):
    VALUE_TYPES = ["Constant value", "Get live during simulation", "Formula", "External program", "Random value"]

    def __init__(self, name: str, start: int, end: int, color_index: int, type:FieldType=None):
        ProtocolLabel.__init__(self, name, start, end, color_index, type=type)
        SimulatorItem.__init__(self)

        self.value_type_index = 0
        self.external_program = ""
        self.formula = ""

    def set_parent(self, value):
        if value is not None:
            assert isinstance(value, SimulatorMessage)

        super().set_parent(value)

    def __hash__(self):
        return object.__hash__(self)

    def __eq__(self, other):
        return object.__eq__(self, other)