from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.util.crc import crc_generic


class CRCLabel(ProtocolLabel):
    __slots__ = ("data_ranges", "crc")

    def __init__(self, name: str, start: int, end: int, color_index: int, field_type: FieldType,
                 fuzz_created=False, auto_created=False):
        assert field_type.function == FieldType.function.CRC
        super().__init__(name, start, end, color_index, fuzz_created, auto_created, field_type)

        self.data_ranges = []  # type: list[tuple]
        self.crc = None   # type: crc_generic
