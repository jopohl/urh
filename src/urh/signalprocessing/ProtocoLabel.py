from enum import Enum

from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET

from urh.signalprocessing.FieldType import FieldType
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

    __slots__ = ("__name", "start", "end", "apply_decoding", "color_index", "show", "fuzz_me", "fuzz_values",
                 "fuzz_created", "__type", "display_format_index", "auto_created", "copied")

    def __init__(self, name: str, start: int, end: int, color_index: int, fuzz_created=False,
                 auto_created=False, type:FieldType=None):
        self.__name = name
        self.start = start
        self.end = end + 1

        self.apply_decoding = True
        self.color_index = color_index
        self.show = Qt.Checked

        self.fuzz_me = Qt.Checked
        self.fuzz_values = []

        self.fuzz_created = fuzz_created

        self.__type = type # type: FieldType

        self.display_format_index = 0 if type is None else type.display_format_index

        self.auto_created = auto_created

        self.copied = False  # keep track if label was already copied for COW in generation to avoid needless recopy

    @property
    def type(self) -> FieldType:
        return self.__type

    @type.setter
    def type(self, value: FieldType):
        if value != self.type:
            self.__type = value
            # set viewtype for type
            if hasattr(value, "display_format_index"):
                self.display_format_index = value.display_format_index

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
        return self.start == other.start and self.end == other.end and self.name == other.name and self.type == other.type

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
                                            "auto_created": str(self.auto_created), "type_id": self.type.id if self.type is not None else ""})

    @staticmethod
    def from_xml(tag: ET.Element, field_types_by_type_id=None):
        """

        :param tag:
        :type field_types_by_type_id: dict[str, FieldType]
        :return:
        """
        field_types_by_type_id = dict() if field_types_by_type_id is None else field_types_by_type_id

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
        type_id = tag.get("type_id", None)
        if type_id and type_id in field_types_by_type_id:
            result.type = field_types_by_type_id[type_id]
        else:
            result.type = None

        return result
