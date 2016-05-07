from copy import deepcopy

from PyQt5.QtCore import Qt, QObject, pyqtSignal
import xml.etree.ElementTree as ET


class LabelSignals(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    apply_decoding_changed = pyqtSignal(object)

class ProtocolLabel(object):
    """
    Eine Eigenschaft des Protokolls (zum Beispiel Temperatur), die an einer bestimmten Stelle steht.
    Die Stelle wird durch (from, to) beschrieben und der Wert der Eigenschaft durch Value.
    From und To beziehen sich immer auf die Bitdarstellung des Protokolls!
    """

    VALUE_TYPES = ["Bits", "Hex", "ASCII"]
    DISPLAY_TYPES = ["Bit", "Hex", "ASCII", "Decimal"]
    SEARCH_TYPES = ["Number", "Bits", "Hex", "ASCII"]

    def __init__(self, name: str, start: int, end: int, refblock: int, val_type_index: int,
                 color_index: int, restrictive: bool):
        self.signals = LabelSignals()
        self.__block_numbers = []
        self.__name = name
        self.__refblock = refblock
        self.refblock_offset = 0  # Offset, für Fuzzing Labels
        val_type = self.VALUE_TYPES[val_type_index]
        if val_type == "Bits":
            self.start = start
            self.end = end + 1
        elif val_type == "Hex":
            self.start = 4 * start
            self.end = 4 * (end + 1)
        elif val_type == "ASCII":
            self.start = 8 * start
            self.end = 8 * (end + 1)

        self.__apply_decoding = True
        self.color_index = color_index
        self.restrictive = restrictive
        self.reference_bits = ""
        self.show = Qt.Checked

        self.fuzz_me = Qt.Checked
        self.fuzz_values = []

        self.display_type_index = 0

        self.nfuzzed = 0  # Für Anzeige der erzeugten gefuzzten Blöcken

    @property
    def block_numbers(self):
        """
        List of Blockindices the label matches

        :type: list of int
        """
        return self.__block_numbers

    @block_numbers.setter
    def block_numbers(self, val):
        self.__block_numbers = val

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
    def apply_decoding(self):
        return self.__apply_decoding

    @apply_decoding.setter
    def apply_decoding(self, value: bool):
        if self.__apply_decoding != value:
            self.__apply_decoding = value
            self.signals.apply_decoding_changed.emit(self)

    @property
    def fuzz_maximum(self):
        return 2 ** (self.end - self.start)

    @property
    def refblock(self):
        return self.__refblock + self.refblock_offset

    @refblock.setter
    def refblock(self, val):
        self.__refblock = val

    @property
    def active_fuzzing(self) -> bool:
        return self.fuzz_me and len(self.fuzz_values) > 1

    @property
    def range_complete_fuzzed(self) -> bool:
        upper_limit = 2 ** (self.end - self.start)
        return len(self.fuzz_values) == upper_limit

    def find_block_numbers(self, proto_blocks):
        """

        :type proto_blocks: list of str
        """
        old_numbers = self.block_numbers[:]

        if self.restrictive:
            self.block_numbers = [i for i, p in enumerate(proto_blocks)
                                  if p[self.start:self.end] == self.reference_bits]
        else:
            self.block_numbers = list(range(len(proto_blocks)))

        if old_numbers != self.block_numbers and not self.apply_decoding:
            self.signals.apply_decoding_changed.emit(self)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k != "signals":
                setattr(result, k, deepcopy(v, memo))
        result.signals = LabelSignals()
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
        return self.start == other.start and self.end == other.end and self.name == other.name

    def __repr__(self):
        return "Protocol Label - start: {0} end: {1} name: {2}".format(self.start, self.end, self.name)

    def add_fuzz_value(self):
        cur_val = self.fuzz_values[-1]
        format_string = "{0:0" + str(len(cur_val)) + "b}"
        maximum = 2 ** len(cur_val)
        cur_val = format_string.format((int(cur_val, 2) + 1) % maximum)

        self.fuzz_values.append(cur_val)

    def add_decimal_fuzz_value(self, val: int):
        cur_val = self.fuzz_values[-1]
        format_string = "{0:0" + str(len(cur_val)) + "b}"
        self.fuzz_values.append(format_string.format(val))


    def to_xml(self, index:int) -> ET.Element:
        return ET.Element("label", attrib={ "name": self.__name, "start": str(self.start), "end": str(self.end),
                                            "refblock": str(self.__refblock), "color_index": str(self.color_index),
                                            "apply_decoding": str(self.__apply_decoding), "index": str(index),
                                            "show": str(self.show), "restrictive": str(self.restrictive),
                                            "fuzz_me": str(self.fuzz_me), "fuzz_values": ",".join(self.fuzz_values)})

    @staticmethod
    def from_xml(tag: ET.Element):
        name = tag.get("name")
        start, end = int(tag.get("start", 0)), int(tag.get("end", 0)) - 1
        refblock, color_index = int(tag.get("refblock", 0)), int(tag.get("color_index", 0))
        restrictive = True if tag.get("restrictive", 'True') == "True" else False

        result = ProtocolLabel(name, start, end, refblock, 0, color_index, restrictive)
        result.apply_decoding = True if tag.get("apply_decoding", 'True') == "True" else False
        result.show = Qt.Checked if int(tag.get("show", 0)) else Qt.Unchecked
        result.fuzz_me = Qt.Checked if int(tag.get("fuzz_me", 0)) else Qt.Unchecked
        result.fuzz_values = tag.get("fuzz_values", "").split(",")

        return result