from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorMessage import SimulatorMessage

class SimulatorProtocolLabel(SimulatorItem):
    VALUE_TYPES = ["Constant value", "Get live during simulation", "Formula", "External program", "Random value"]

    def __init__(self, label: ProtocolLabel):
        #ProtocolLabel.__init__(self, name, start, end, color_index, field_type=field_type)
        SimulatorItem.__init__(self)

        self.label = label

        self.value_type_index = 0
        self.external_program = ""
        self.formula = ""
        self.random_min = 0
        self.random_max = self.label.fuzz_maximum - 1

    def set_parent(self, value):
        if value is not None:
            assert isinstance(value, SimulatorMessage)

        super().set_parent(value)
    
    def __lt__(self, other):
        if self.label.start != other.label.start:
            return self.label.start < other.label.start
        elif self.label.end != other.label.end:
            return self.label.end < other.label.end
        elif self.label.name is not None and other.label.name is not None:
            return len(self.label.name) < len(other.label.name)
        else:
            return False

    @property
    def name(self):
        return self.label.name

    @name.setter
    def name(self, val):
        self.label.name = val

    @property
    def color_index(self):
        return self.label.color_index

    @property
    def start(self):
        return self.label.start

    @property
    def end(self):
        return self.label.end

    @property
    def display_format_index(self):
        return self.label.display_format_index

    @display_format_index.setter
    def display_format_index(self, val):
        self.label.display_format_index = val

    @property
    def field_type(self) -> FieldType:
        return self.label.field_type

    @field_type.setter
    def field_type(self, val):
        self.label.field_type = val

    @property
    def apply_decoding(self):
        return self.label.apply_decoding

#    def __hash__(self):
#        return object.__hash__(self)

#    def __eq__(self, other):
#        return object.__eq__(self, other)

    def check(self):
        result = True

        if self.value_type_index == 2:
            result, _, _ = self.expression_parser.validate_expression(self.formula)
        
        return result