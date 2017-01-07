from enum import Enum


class FieldType(object):

    __slots__ = ["caption", "function", "display_format_index"]

    class Function(Enum):
        PREAMBLE = "preamble"
        SYNC = "synchronization"
        SRC_ADDRESS = "source address"
        DST_ADDRESS = "destination address"

        SEQUENCE_NUMBER = "sequence number"
        CRC = "crc"
        CUSTOM = ""

    def __init__(self, caption: str, function: Function, display_format_index:int = None):
        self.caption = caption
        self.function = function

        if display_format_index is None:
            if self.function in (self.Function.PREAMBLE, self.Function.SYNC):
                self.display_format_index = 0
            elif self.function in (self.Function.DST_ADDRESS, self.Function.SRC_ADDRESS, self.Function.CRC):
                self.display_format_index = 1
            elif self.function in (self.Function.SEQUENCE_NUMBER, ):
                self.display_format_index = 3
            else:
                self.display_format_index = 0
        else:
            self.display_format_index = display_format_index

        self.display_format_index = display_format_index