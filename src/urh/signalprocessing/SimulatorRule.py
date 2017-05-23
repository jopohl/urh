from enum import Enum

from urh.signalprocessing.SimulatorItem import SimulatorItem

class SimulatorRule(SimulatorItem):
    def __init__(self):
        super().__init__()

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None

        super().set_parent(value)

    def has_else_condition(self):
        return any(child.type is ConditionType.ELSE for child in self.children)

class ConditionType(Enum):
    IF = "IF"
    ELSE_IF = "ELSE IF"
    ELSE = "ELSE"

class SimulatorRuleCondition(SimulatorItem):
    def __init__(self, type: ConditionType):
        super().__init__()
        self.type = type
        self.condition = ""

    def set_parent(self, value):
        if value is not None:
            assert isinstance(value, SimulatorRule)

        super().set_parent(value)