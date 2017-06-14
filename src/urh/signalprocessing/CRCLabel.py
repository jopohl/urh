import ast

from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.util.crc import crc_generic
import xml.etree.ElementTree as ET

class CRCLabel(ProtocolLabel):
    __slots__ = ("data_ranges", "crc")

    def __init__(self, name: str, start: int, end: int, color_index: int, field_type: FieldType,
                 fuzz_created=False, auto_created=False):
        assert field_type.function == FieldType.Function.CRC
        super().__init__(name, start, end, color_index, fuzz_created, auto_created, field_type)

        self.data_ranges = []  # type: list[tuple]
        self.crc = None   # type: crc_generic

    @staticmethod
    def from_label(label: ProtocolLabel):
        result = CRCLabel(label.name, label.start, label.end-1, label.color_index, label.field_type,
                          label.fuzz_created, label.auto_created)
        result.apply_decoding = label.apply_decoding
        result.show = label.show
        result.fuzz_me = label.fuzz_me
        result.fuzz_values = label.fuzz_values
        result.display_format_index = label.display_format_index
        return result

    @staticmethod
    def from_xml(tag: ET.Element, field_types_by_type_id=None):
        lbl = super().from_xml(tag, field_types_by_type_id)
        result = CRCLabel.from_label(lbl)
        result.data_ranges = ast.literal_eval(tag.get("data_ranges", "[]"))
        result.crc = None # TODO: Define CRC Format for storage in XML

    def to_xml(self, index: int):
        result = super().to_xml(index)
        result.tag = "crc_label"
        result.attrib.update({"data_ranges": str(self.data_ranges), "crc": str(self.crc)})
