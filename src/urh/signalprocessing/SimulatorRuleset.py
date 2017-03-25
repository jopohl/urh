import operator
import weakref
from enum import Enum

#from urh.ui.SimulatorScene import LabelItem
from urh.signalprocessing.Ruleset import OPERATIONS, OPERATION_DESCRIPTION

class Mode(Enum):
    all_apply = 0
    atleast_one_applies = 1

class SimulatorRule(object):
    def __init__(self, variable, operator: str, target_value: str):
        assert operator in OPERATIONS
        self.__variable = weakref.ref(variable) if variable else None
        self.operator = operator
        self.target_value = target_value

    @property
    def variable(self):
        if not self.__variable or not self.__variable():
            return None
        else:
            return self.__variable()

    @variable.setter
    def variable(self, value):
        self.__variable = weakref.ref(value) if value else None

    @property
    def operator_description(self):
        return OPERATION_DESCRIPTION[self.operator]

    @operator_description.setter
    def operator_description(self, value):
        for key, val in OPERATION_DESCRIPTION.items():
            if val == value:
                self.operator = key
                return

class SimulatorRuleset(list):
    def __init__(self, mode: Mode = Mode.all_apply, rules = None):
        rules = rules if rules is not None else []
        self.mode = mode
        super().__init__(rules)