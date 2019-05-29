import copy
import xml.etree.ElementTree as ET

from PyQt5.QtCore import Qt

from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Interval import Interval
from urh.util.Formatter import Formatter


class ProtocolLabel(object):
    """
    This represents a field in the protocol, e.g. temperature
    Field range is described by (start, end) and it's value by value
    start and end always refer to bit view!
    """

    DISPLAY_FORMATS = ["Bit", "Hex", "ASCII", "Decimal", "BCD"]

    DISPLAY_BIT_ORDERS = ["MSB", "LSB", "LSD"]

    SEARCH_TYPES = ["Number", "Bits", "Hex", "ASCII"]

    __slots__ = ("__name", "start", "end", "apply_decoding", "color_index", "show", "__fuzz_me", "fuzz_values",
                 "fuzz_created", "__field_type", "display_format_index", "display_bit_order_index",
                 "display_endianness", "auto_created", "copied")

    def __init__(self, name: str, start: int, end: int, color_index: int, fuzz_created=False,
                 auto_created=False, field_type: FieldType = None):
        self.__name = name
        self.start = start
        self.end = end + 1

        self.apply_decoding = True
        self.color_index = color_index
        self.show = Qt.Checked

        self.__fuzz_me = Qt.Checked
        self.fuzz_values = []

        self.fuzz_created = fuzz_created

        if field_type is None:
            self.__field_type = FieldType.from_caption(name)
        else:
            self.__field_type = field_type  # type: FieldType

        self.display_format_index = 0 if field_type is None else field_type.display_format_index
        self.display_bit_order_index = 0
        self.display_endianness = "big"

        self.auto_created = auto_created

        self.copied = False  # keep track if label was already copied for COW in generation to avoid needless recopy

    @property
    def fuzz_me(self) -> int:
        return self.__fuzz_me

    @fuzz_me.setter
    def fuzz_me(self, value):
        if isinstance(value, bool):
            value = Qt.Checked if value else Qt.Unchecked
        self.__fuzz_me = value

    @property
    def is_preamble(self) -> bool:
        return self.field_type is not None and self.field_type.function == FieldType.Function.PREAMBLE

    @property
    def is_sync(self) -> bool:
        return self.field_type is not None and self.field_type.function == FieldType.Function.SYNC

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def field_type(self) -> FieldType:
        return self.__field_type

    @field_type.setter
    def field_type(self, value: FieldType):
        if value != self.field_type:
            self.__field_type = value
            # set viewtype for type
            if hasattr(value, "display_format_index"):
                self.display_format_index = value.display_format_index

    @property
    def field_type_function(self):
        if self.field_type is not None:
            return self.field_type.function
        else:
            return None

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

    @property
    def display_order_str(self) -> str:
        try:
            bit_order = self.DISPLAY_BIT_ORDERS[self.display_bit_order_index]
            return bit_order + "/{}".format("BE" if self.display_endianness == "big" else "LE")
        except IndexError:
            return ""

    @display_order_str.setter
    def display_order_str(self, value: str):
        prefix = value.strip().split("/")[0]
        suffix = value.strip().split("/")[-1]
        if suffix == "BE":
            endianness = "big"
        elif suffix == "LE":
            endianness = "little"
        else:
            return

        try:
            self.display_bit_order_index = self.DISPLAY_BIT_ORDERS.index(prefix)
            self.display_endianness = endianness
        except ValueError:
            return

    def get_copy(self):
        if self.copied:
            return self
        else:
            result = copy.deepcopy(self)
            result.copied = True
            return result

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
        return self.start == other.start and \
               self.end == other.end and \
               self.name == other.name and \
               self.field_type_function == other.field_type_function

    def __hash__(self):
        return hash((self.start, self.end, self.name, self.field_type_function))

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

    def to_xml(self) -> ET.Element:
        return ET.Element("label", attrib={"name": self.__name, "start": str(self.start), "end": str(self.end),
                                           "color_index": str(self.color_index),
                                           "apply_decoding": str(self.apply_decoding), "show": str(self.show),
                                           "display_format_index": str(self.display_format_index),
                                           "display_bit_order_index": str(self.display_bit_order_index),
                                           "display_endianness": str(self.display_endianness),
                                           "fuzz_me": str(self.fuzz_me), "fuzz_values": ",".join(self.fuzz_values),
                                           "auto_created": str(self.auto_created)})

    @classmethod
    def from_xml(cls, tag: ET.Element, field_types_by_caption=None):
        """

        :param tag:
        :type field_types_by_caption: dict[str, FieldType]
        :return:
        """
        field_types_by_caption = dict() if field_types_by_caption is None else field_types_by_caption

        name = tag.get("name")
        start, end = int(tag.get("start", 0)), int(tag.get("end", 0)) - 1
        color_index = int(tag.get("color_index", 0))

        result = ProtocolLabel(name=name, start=start, end=end, color_index=color_index)
        result.apply_decoding = True if tag.get("apply_decoding", 'True') == "True" else False
        result.show = Qt.Checked if Formatter.str2val(tag.get("show", 0), int) else Qt.Unchecked
        result.fuzz_me = Qt.Checked if Formatter.str2val(tag.get("fuzz_me", 0), int) else Qt.Unchecked
        result.fuzz_values = tag.get("fuzz_values", "").split(",")
        result.auto_created = True if tag.get("auto_created", 'False') == "True" else False

        if result.name in field_types_by_caption:
            result.field_type = field_types_by_caption[result.name]
        else:
            result.field_type = None

        # set this after result.field_type because this would change display_format_index to field_types default
        result.display_format_index = int(tag.get("display_format_index", 0))
        result.display_bit_order_index = int(tag.get("display_bit_order_index", 0))
        result.display_endianness = tag.get("display_endianness", "big")

        return result
