from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
import xml.etree.ElementTree as ET


class SimulatorGotoAction(SimulatorItem):
    def __init__(self):
        super().__init__()
        self.goto_target = None  # type: str

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

    def to_xml(self) -> ET.Element:
        attribs = dict()
        if self.goto_target is not None:
            attribs["goto_target"] = self.goto_target

        return ET.Element("simulator_goto_action", attrib=attribs)

    @classmethod
    def from_xml(cls, tag: ET.Element):
        result = SimulatorGotoAction()
        result.goto_target = tag.get("goto_target", None)
        return result
