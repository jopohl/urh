from enum import Enum

from PyQt5.QtCore import QSettings


class FieldType(object):

    __slots__ = ["caption", "function", "display_format_index"]

    class Function(Enum):
        PREAMBLE = "preamble"
        SYNC = "synchronization"
        SRC_ADDRESS = "source address"
        DST_ADDRESS = "destination address"

        SEQUENCE_NUMBER = "sequence number"
        CRC = "crc"
        CUSTOM = "custom"

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

    def __repr__(self):
        return "FieldType: {0} - {1} ({2})".format(self.function.name, self.caption, self.display_format_index)

    @staticmethod
    def read_from_settings(settings: QSettings):
        """

        :rtype: list of FieldType
        """
        size = settings.beginReadArray("field_types")
        result = []
        for i in range(0, size):
            settings.setArrayIndex(i)
            caption = settings.value("caption", defaultValue="", type=str)
            function = settings.value("function", defaultValue="CUSTOM", type=str)
            display_format_index = settings.value("display_format_index", defaultValue=None, type=int)

            result.append(FieldType(caption, FieldType.Function[function], display_format_index))

        return result

if __name__ == "__main__":
    import urh.constants as constants
    print(FieldType.read_from_settings(constants.SETTINGS))

