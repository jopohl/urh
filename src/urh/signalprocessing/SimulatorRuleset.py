import operator
from enum import Enum

from urh.util.Logger import logger

#from urh.ui.SimulatorScene import LabelItem
from urh.signalprocessing.Ruleset import OPERATIONS, OPERATION_DESCRIPTION

class Mode(Enum):
    all_apply = 0
    atleast_one_applies = 1

class SimulatorRulesetItem(object):
    VIEW_TYPES = ["Bit", "Hex", "ASCII"]

    def __init__(self, variable, operator: str, target_value: str, value_type: int):
        assert operator in OPERATIONS
        self.variable = variable
        self.__value_type = value_type
        self.operator = operator
        self.target_value = target_value

    @property
    def operator_description(self):
        return OPERATION_DESCRIPTION[self.operator]

    @operator_description.setter
    def operator_description(self, value):
        for key, val in OPERATION_DESCRIPTION.items():
            if val == value:
                self.operator = key
                return

    def __str__(self):
        return self.variable + " " + self.operator + " " + self.target_value

    @property
    def value_type(self):
        return int(self.__value_type)

    @value_type.setter
    def value_type(self, value: int):
        try:
            self.__value_type = int(value)
        except ValueError:
            logger.warning("{} could not be cast to integer".format(value))


class SimulatorRuleset(list):
    def __init__(self, mode: Mode = Mode.all_apply, rules = None):
        rules = rules if rules is not None else []
        self.mode = mode
        super().__init__(rules)