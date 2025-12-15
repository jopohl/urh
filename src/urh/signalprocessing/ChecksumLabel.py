import array
import ast
import xml.etree.ElementTree as ET
from enum import Enum

from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.util.GenericCRC import GenericCRC
from urh.util.WSPChecksum import WSPChecksum


class ChecksumLabel(ProtocolLabel):
    __slots__ = ("__data_ranges", "checksum", "__category")

    class Category(Enum):
        generic = "generic"
        wsp = "Wireless Short Packet (WSP)"

    def __init__(
        self,
        name: str,
        start: int,
        end: int,
        color_index: int,
        field_type: FieldType,
        fuzz_created=False,
        auto_created=False,
        data_range_start=0,
    ):
        assert field_type.function == FieldType.Function.CHECKSUM
        super().__init__(
            name, start, end, color_index, fuzz_created, auto_created, field_type
        )

        self.__category = self.Category.generic
        self.__data_ranges = [
            [data_range_start, self.start]
        ]  # type: list[list[int,int]]
        self.checksum = GenericCRC(polynomial=0)  # type: GenericCRC or WSPChecksum

    def calculate_checksum(self, bits: array.array) -> array.array:
        return self.checksum.calculate(bits)

    def calculate_checksum_for_message(
        self, message, use_decoded_bits: bool
    ) -> array.array:
        data = array.array("B", [])
        bits = message.decoded_bits if use_decoded_bits else message.plain_bits
        for data_range in self.data_ranges:
            data.extend(bits[data_range[0] : data_range[1]])
        return self.calculate_checksum(data)

    @property
    def data_ranges(self):
        if self.category == self.Category.wsp:
            return [[12, -4]]
        else:
            return self.__data_ranges

    @data_ranges.setter
    def data_ranges(self, value):
        self.__data_ranges = value

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

    def to_label(self, field_type: FieldType) -> ProtocolLabel:
        result = ProtocolLabel(
            name=self.name,
            start=self.start,
            end=self.end - 1,
            color_index=self.color_index,
            field_type=field_type,
            auto_created=self.auto_created,
            fuzz_created=self.fuzz_created,
        )
        result.apply_decoding = self.apply_decoding
        result.show = self.show
        result.fuzz_me = self.fuzz_me
        result.fuzz_values = self.fuzz_values
        result.display_format_index = self.display_format_index
        return result

    @classmethod
    def from_label(cls, label: ProtocolLabel):
        result = ChecksumLabel(
            name=label.name,
            start=label.start,
            end=label.end - 1,
            color_index=label.color_index,
            field_type=FieldType(label.name, FieldType.Function.CHECKSUM),
            fuzz_created=label.fuzz_created,
            auto_created=label.auto_created,
        )
        result.apply_decoding = label.apply_decoding
        result.show = label.show
        result.fuzz_me = label.fuzz_me
        result.fuzz_values = label.fuzz_values
        result.display_format_index = label.display_format_index
        return result

    @classmethod
    def from_xml(cls, tag: ET.Element, field_types_by_caption=None):
        lbl = super().from_xml(tag, field_types_by_caption)
        if (
            lbl.field_type is None
            or lbl.field_type.function != FieldType.Function.CHECKSUM
        ):
            checksum_field_type = next(
                (
                    ft
                    for ft in field_types_by_caption.values()
                    if ft.function == FieldType.Function.CHECKSUM
                ),
                FieldType(
                    "checksum", FieldType.Function.CHECKSUM, display_format_index=1
                ),
            )
            lbl.field_type = checksum_field_type
        result = cls.from_label(lbl)
        result.data_ranges = ast.literal_eval(tag.get("data_ranges", "[]"))
        result.category = cls.Category[tag.get("category", "generic")]

        crc_tag = tag.find("crc")
        if crc_tag is not None:
            result.checksum = GenericCRC.from_xml(crc_tag)

        wsp_tag = tag.find("wsp_checksum")
        if wsp_tag is not None:
            result.checksum = WSPChecksum.from_xml(wsp_tag)

        return result

    def to_xml(self):
        result = super().to_xml()
        result.tag = "checksum_label"
        result.attrib.update(
            {"data_ranges": str(self.data_ranges), "category": self.category.name}
        )
        result.append(self.checksum.to_xml())
        return result
