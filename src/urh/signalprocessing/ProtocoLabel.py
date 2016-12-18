from enum import Enum

from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET

from urh.signalprocessing.Interval import Interval
from urh.util.Formatter import Formatter


class ProtocolLabel(object):
    """
    Eine Eigenschaft des Protokolls (zum Beispiel Temperatur), die an einer bestimmten Stelle steht.
    Die Stelle wird durch (from, to) beschrieben und der Wert der Eigenschaft durch Value.
    From und To beziehen sich immer auf die Bitdarstellung des Protokolls!
    """

    DISPLAY_FORMATS = ["Bit", "Hex", "ASCII", "Decimal"]
    SEARCH_TYPES = ["Number", "Bits", "Hex", "ASCII"]

    class Type(Enum):
        PREAMBLE = "preamble"
        SYNC = "synchronization"
        SRC_ADDRESS = "source address"
        DST_ADDRESS = "destination address"

        SEQUENCE_NUMBER = "sequence number"
        CRC = "crc"
        CUSTOM = ""

    def __init__(self, name: str, start: int, end: int, color_index: int, fuzz_created=False, auto_created=False):
        self.__name = name
        self.start = start
        self.end = end + 1

        self.apply_decoding = True
        self.color_index = color_index
        self.show = Qt.Checked

        self.fuzz_me = Qt.Checked
        self.fuzz_values = []

        self.fuzz_created = fuzz_created

        self.__type = ProtocolLabel.Type.CUSTOM

        self.display_format_index = 0

        self.auto_created = auto_created

    @property
    def name(self):
        if not self.__name:
            self.__name = "No name"

        return self.__name

    @name.setter
    def name(self, val):
        if val:
            self.__name = val

    @property
    def type(self) -> Type:
        return self.__type

    @type.setter
    def type(self, value: Type):
        if value != self.type:
            self.__type = value
            # set viewtype for type
            if self.type in (self.Type.PREAMBLE, self.Type.SYNC):
                self.display_format_index = 0
            elif self.type in (self.Type.DST_ADDRESS, self.Type.SRC_ADDRESS, self.Type.CRC):
                self.display_format_index = 1
            elif self.type == self.Type.SEQUENCE_NUMBER:
                self.display_format_index = 3


    @property
    def title(self):
        if self.type != ProtocolLabel.Type.CUSTOM:
            return self.type.value
        else:
            return self.name

    @property
    def fuzz_maximum(self):
        return 2 ** (self.end - self.start)

    @property
    def active_fuzzing(self) -> bool:
        return self.fuzz_me and len(self.fuzz_values) > 1

    @property
    def range_complete_fuzzed(self) -> bool:
        upper_limit = 2 ** (self.end - self.start)
        return len(self.fuzz_values) == upper_limit

    def __lt__(self, other):
        if self.start != other.start:
            return self.start < other.start
        elif self.end != other.end:
            return self.end < other.end
        elif self.name is not None and other.name is not None:
            return len(self.name) < len(other.name)
        else:
            return False

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end and self.name == other.name

    def __hash__(self):
        return hash("{}/{}/{}".format(self.start, self.end, self.name))

    def __repr__(self):
        return "Protocol Label - start: {0} end: {1} name: {2}".format(self.start, self.end, self.name)

    def overlaps_with(self, other_label):
        return Interval(self.start, self.end).overlaps_with(Interval(other_label.start, other_label.end))

    def add_fuzz_value(self):
        cur_val = self.fuzz_values[-1]
        format_string = "{0:0" + str(len(cur_val)) + "b}"
        maximum = 2 ** len(cur_val)
        cur_val = format_string.format((int(str(Formatter.str2val(cur_val, int)), 2) + 1) % maximum)

        self.fuzz_values.append(cur_val)

    def add_decimal_fuzz_value(self, val: int):
        cur_val = self.fuzz_values[-1]
        format_string = "{0:0" + str(len(cur_val)) + "b}"
        self.fuzz_values.append(format_string.format(val))


    def to_xml(self, index:int) -> ET.Element:
        return ET.Element("label", attrib={ "name": self.__name, "start": str(self.start), "end": str(self.end), "color_index": str(self.color_index),
                                            "apply_decoding": str(self.apply_decoding), "index": str(index),
                                            "show": str(self.show), "display_format_index": str(self.display_format_index),
                                            "fuzz_me": str(self.fuzz_me), "fuzz_values": ",".join(self.fuzz_values),
                                            "auto_created": str(self.auto_created), "type": self.type.name})

    @staticmethod
    def from_xml(tag: ET.Element):
        name = tag.get("name")
        start, end = int(tag.get("start", 0)), int(tag.get("end", 0)) - 1
        color_index = int(tag.get("color_index", 0))

        result = ProtocolLabel(name=name, start=start, end=end, color_index=color_index)
        result.apply_decoding = True if tag.get("apply_decoding", 'True') == "True" else False
        result.show = Qt.Checked if Formatter.str2val(tag.get("show", 0), int) else Qt.Unchecked
        result.fuzz_me = Qt.Checked if Formatter.str2val(tag.get("fuzz_me", 0), int) else Qt.Unchecked
        result.fuzz_values = tag.get("fuzz_values", "").split(",")
        result.display_format_index = int(tag.get("display_format_index", 0))
        result.auto_created =  True if tag.get("auto_created", 'False') == "True" else False
        result.type = ProtocolLabel.Type[tag.get("type", '')]

        return result