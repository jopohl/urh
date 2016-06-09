import operator
from enum import Enum

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


class DataRule(object):
    def __init__(self, start: int, end: int, operator: str, target_value: str, value_type: int):
        assert operator in OPERATIONS
        self.start = start
        self.end = end + 1
        self.value_type = value_type # 0 = Bit, 1 = Hex, 2 = ASCII
        self.operator = operator
        self.target_value = target_value

    def applies_for_block(self, block):
        data = block.decoded_bits_str if self.value_type == 0 else block.decoded_hex_str if self.value_type == 1 else block.decoded_ascii_str
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

class Ruleset(list):
    def __init__(self, mode: Mode = Mode.all_apply, rules = None):
        rules = rules if rules is not None else []
        self.mode = mode
        super().__init__(rules)

    def applies_for_block(self, block):
        napplied_rules = sum(rule.applies_for_block(block) for rule in self)

        if self.mode == Mode.all_apply:
            return napplied_rules == len(self)
        elif self.mode == Mode.atleast_one_applies:
            return napplied_rules > 0
        elif self.mode == Mode.none_applies:
            return napplied_rules == 0
        else:
            raise ValueError("Unknown behavior " + str(self.mode))