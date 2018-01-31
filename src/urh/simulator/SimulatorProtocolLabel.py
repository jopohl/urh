from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.FieldType import FieldType
from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorMessage import SimulatorMessage
import xml.etree.ElementTree as ET

from urh.util.Formatter import Formatter


class SimulatorProtocolLabel(SimulatorItem):
    VALUE_TYPES = ["Constant value", "Get live during simulation", "Formula", "External program", "Random value"]

    def __init__(self, label: ProtocolLabel):
        SimulatorItem.__init__(self)

        self.label = label

        self.value_type_index = 0
        self.external_program = ""
        self.formula = ""
        self.random_min = 0
        self.random_max = self.label.fuzz_maximum - 1

    def get_copy(self):
        # no copy needed in simulator
        return self

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

    @start.setter
    def start(self, value):
        self.label.start = value

    @property
    def end(self):
        return self.label.end

    @end.setter
    def end(self, value):
        self.label.end = value

    @property
    def display_format_index(self):
        return self.label.display_format_index

    @display_format_index.setter
    def display_format_index(self, val):
        self.label.display_format_index = val

    @property
    def field_type(self) -> FieldType:
        return self.label.field_type

    @property
    def fuzz_maximum(self):
        return self.label.fuzz_maximum

    @field_type.setter
    def field_type(self, val: FieldType):
        if self.is_checksum_label and val.function != FieldType.Function.CHECKSUM:
            assert isinstance(self.label, ChecksumLabel)
            self.label = self.label.to_label(val)
        elif not self.is_checksum_label and val.function == FieldType.Function.CHECKSUM:
            self.label = ChecksumLabel.from_label(self.label)
        self.label.field_type = val

    @property
    def apply_decoding(self):
        return self.label.apply_decoding

    @property
    def show(self):
        return self.label.show

    @show.setter
    def show(self, value):
        self.label.show = value

    @property
    def is_checksum_label(self):
        return isinstance(self.label, ChecksumLabel)

    @property
    def display_bit_order_index(self):
        return self.label.display_bit_order_index

    @display_bit_order_index.setter
    def display_bit_order_index(self, value):
        self.label.display_bit_order_index = value

    def check(self):
        result = True

        if self.value_type_index == 2:
            result, _, _ = self.expression_parser.validate_expression(self.formula)

        return result

    def to_xml(self) -> ET.Element:
        result = ET.Element("simulator_label", attrib={"value_type_index": str(self.value_type_index),
                                                       "external_program": str(self.external_program),
                                                       "formula": str(self.formula),
                                                       "random_min": str(self.random_min),
                                                       "random_max": str(self.random_max)})
        result.append(self.label.to_xml())
        return result

    @classmethod
    def from_xml(cls, tag: ET.Element, field_types_by_caption=None):
        """

        :param tag:
        :type field_types_by_caption: dict[str, FieldType]
        :return:
        """
        label_tag = tag.find("label")
        if label_tag is not None:
            label = ProtocolLabel.from_xml(label_tag, field_types_by_caption)
        else:
            label = ChecksumLabel.from_xml(tag.find("checksum_label"), field_types_by_caption)
        result = SimulatorProtocolLabel(label)
        result.value_type_index = Formatter.str2val(tag.get("value_type_index", "0"), int)
        result.external_program = tag.get("external_program", "")
        result.formula = tag.get("formula", "")
        result.random_min = Formatter.str2val(tag.get("random_min", "0"), int)
        result.random_max = Formatter.str2val(tag.get("random_max", str(label.fuzz_maximum-1)), int)
        return result
