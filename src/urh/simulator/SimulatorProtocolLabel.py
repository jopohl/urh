from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.FieldType import FieldType
from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorMessage import SimulatorMessage
import xml.etree.ElementTree as ET

from urh.util import util
from urh.util.Formatter import Formatter


class SimulatorProtocolLabel(SimulatorItem):
    VALUE_TYPES = ["Constant value", "Live input", "Formula", "External program", "Random value"]

    def __init__(self, label: ProtocolLabel):
        super().__init__()

        self.label = label

        self.value_type_index = 0
        self.external_program = ""
        self.formula = ""
        self.random_min = 0
        self.random_max = self.label.fuzz_maximum - 1

    @property
    def has_live_input(self):
        return not self.is_checksum_label and self.value_type_index == 1

    def get_copy(self):
        # no copy needed in simulator
        return self

    def set_parent(self, value):
        if value is not None:
            assert isinstance(value, SimulatorMessage)

        super().set_parent(value)

    def __lt__(self, other):
        return self.label < other.label

    def __getattr__(self, name):
        if name == "label":
            return self.__getattribute__("label")

        return self.label.__getattribute__(name)

    def __setattr__(self, key, value):
        if key == "field_type":
            # Use special field type property for changing the label type when changing the field type
            super().__setattr__(key, value)
        try:
            self.label.__setattr__(key, value)
        except AttributeError:
            super().__setattr__(key, value)

    @property
    def field_type(self) -> FieldType:
        return self.label.field_type

    @field_type.setter
    def field_type(self, val: FieldType):
        if val is None:
            return

        if self.is_checksum_label and val.function != FieldType.Function.CHECKSUM:
            assert isinstance(self.label, ChecksumLabel)
            self.label = self.label.to_label(val)
        elif not self.is_checksum_label and val.function == FieldType.Function.CHECKSUM:
            self.label = ChecksumLabel.from_label(self.label)
            self.value_type_index = 0
        self.label.field_type = val

    @property
    def is_checksum_label(self):
        return isinstance(self.label, ChecksumLabel)

    def validate(self):
        result = True

        if self.value_type_index == 2:
            result, _, _ = self.expression_parser.validate_expression(self.formula)
        elif self.value_type_index == 3:
            result = util.validate_command(self.external_program)

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
