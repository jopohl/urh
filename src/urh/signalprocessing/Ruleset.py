import operator
from enum import Enum
import xml.etree.ElementTree as ET

from urh.util.Logger import logger

OPERATIONS = {
                '>':  operator.gt,
                '<':  operator.lt,
                '>=': operator.ge,
                '<=': operator.le,
                '=':  operator.eq,
                '!=': operator.ne
             }

OPERATION_DESCRIPTION = {">": "greater", "<": "lower", ">=": "greater equal", "<=": "lower equal", "=": "equal", "!=": "not equal"}

class Mode(Enum):
    all_apply = 0
    atleast_one_applies = 1
    none_applies = 2


class Rule(object):
    def __init__(self, start: int, end: int, operator: str, target_value: str, value_type: int):
        assert operator in OPERATIONS
        self.__start = start
        self.__end = end + 1
        self.__value_type = value_type # 0 = Bit, 1 = Hex, 2 = ASCII
        self.operator = operator
        self.target_value = target_value

    @property
    def start(self) -> int:
        return int(self.__start)

    @start.setter
    def start(self, value: int):
        try:
            self.__start = int(value)
        except ValueError:
            logger.warning("{} could not be cast to integer".format(value))

    @property
    def end(self) -> int:
        return int(self.__end)

    @end.setter
    def end(self, value: int):
        try:
            self.__end = int(value)
        except ValueError:
            logger.warning("{} could not be cast to integer".format(value))

    @property
    def value_type(self):
        return int(self.__value_type)

    @value_type.setter
    def value_type(self, value: int):
        try:
            self.__value_type = int(value)
        except ValueError:
            logger.warning("{} could not be cast to integer".format(value))

    def applies_for_message(self, message):
        data = message.decoded_bits_str if self.value_type == 0 else message.decoded_hex_str if self.value_type == 1 else message.decoded_ascii_str
        return OPERATIONS[self.operator](data[self.start:self.end], self.target_value)

    @property
    def operator_description(self):
        return OPERATION_DESCRIPTION[self.operator]

    @operator_description.setter
    def operator_description(self, value):
        for key, val in OPERATION_DESCRIPTION.items():
            if val == value:
                self.operator = key
                return
        logger.warning("Could not find operator description " + str(value))

    def to_xml(self) -> ET.Element:
        root = ET.Element("rule")

        for attr, val in vars(self).items():
            root.set(attr, str(val))

        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        result = Rule(start=-1, end=-1, operator="=", target_value="", value_type=0)
        for attrib, value in tag.attrib.items():
            setattr(result, attrib, value)
        return result


class Ruleset(list):
    def __init__(self, mode: Mode = Mode.all_apply, rules = None):
        rules = rules if rules is not None else []
        self.mode = mode
        super().__init__(rules)

    def applies_for_message(self, message):
        napplied_rules = sum(rule.applies_for_message(message) for rule in self)

        if self.mode == Mode.all_apply:
            return napplied_rules == len(self)
        elif self.mode == Mode.atleast_one_applies:
            return napplied_rules > 0
        elif self.mode == Mode.none_applies:
            return napplied_rules == 0
        else:
            raise ValueError("Unknown behavior " + str(self.mode))

    def to_xml(self) -> ET.Element:
        root = ET.Element("ruleset")
        root.set("mode", str(self.mode.value))

        for rule in self:
            root.append(rule.to_xml())

        return root

    @staticmethod
    def from_xml(tag: ET.Element):
        if tag:
            result = Ruleset(mode=Mode(int(tag.get("mode", 0))))
            for rule in tag.findall("rule"):
                result.append(Rule.from_xml(rule))
            return result
        else:
            return Ruleset(mode=Mode.all_apply)
