from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

class SimulatorGotoAction(SimulatorItem):
    def __init__(self):
        super().__init__()
        self.goto_target = None

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None or isinstance(value, SimulatorRuleCondition)

        super().set_parent(value)

    @staticmethod
    def is_valid_goto_target(item: SimulatorItem):
        return not (item is None or isinstance(item, SimulatorProtocolLabel) or
            isinstance(item, SimulatorRule) or
            (isinstance(item, SimulatorRuleCondition) and item.type != ConditionType.IF))

    @staticmethod
    def goto_identifier():
        identifier = []

        for key, value in SimulatorItem.protocol_manager.item_dict.items():
            if SimulatorGotoAction.is_valid_goto_target(value):
                identifier.append(key)

        return identifier

    def check(self):
        return (self.goto_target in self.protocol_manager.item_dict and
                    self.is_valid_goto_target(self.protocol_manager.item_dict[self.goto_target]))

    @property
    def target(self):
        return self.protocol_manager.item_dict[self.goto_target] if self.check() else None