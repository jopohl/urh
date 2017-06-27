import ast

import array

from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.util.GenericCRC import GenericCRC
from enum import Enum
import xml.etree.ElementTree as ET

from urh.util.WSPChecksum import WSPChecksum


class ChecksumLabel(ProtocolLabel):
    __slots__ = ("data_ranges", "checksum", "__category")

    class Category(Enum):
        generic = "generic"
        wsp = "Wireless Short Packet (WSP)"

    def __init__(self, name: str, start: int, end: int, color_index: int, field_type: FieldType,
                 fuzz_created=False, auto_created=False):
        assert field_type.function == FieldType.Function.CHECKSUM
        super().__init__(name, start, end, color_index, fuzz_created, auto_created, field_type)

        self.__category = self.Category.generic
        self.data_ranges = [[0, self.start]]  # type: list[list[int,int]]
        self.checksum = GenericCRC(polynomial=0)   # type: GenericCRC or WSPChecksum

    def calculate_checksum(self, bits: array.array) -> array.array:
        return self.checksum.calculate(bits)

    @property
    def is_generic_crc(self):
        return self.category == self.Category.generic

    @property
    def category(self) -> Category:
        return self.__category

    @category.setter
    def category(self, value: Category):
        if value != self.category:
            self.__category = value
            if self.category == self.Category.generic:
                self.checksum = GenericCRC()
            elif self.category == self.Category.wsp:
                self.checksum = WSPChecksum()
            else:
                raise ValueError("Unknown Category")

    @staticmethod
    def from_label(label: ProtocolLabel):
        result = ChecksumLabel(label.name, label.start, label.end - 1, label.color_index, label.field_type,
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
        result = ChecksumLabel.from_label(lbl)
        result.data_ranges = ast.literal_eval(tag.get("data_ranges", "[]"))
        result.category = ChecksumLabel.Category[tag.get("category", "generic")]
        result.checksum = None # TODO: Define CRC Format for storage in XML

    def to_xml(self, index: int):
        result = super().to_xml(index)
        result.tag = "checksum_label"
        result.attrib.update({"data_ranges": str(self.data_ranges), "checksum": str(self.checksum), "category": str(self.category)})
