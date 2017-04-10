from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.FieldType import FieldType

class SimulatorProtocolLabel(ProtocolLabel, SimulatorItem):
    def __init__(self, name: str, start: int, end: int, color_index: int, type:FieldType=None):
        ProtocolLabel.__init__(self, name, start, end, color_index, type)
        SimulatorItem.__init__(self)