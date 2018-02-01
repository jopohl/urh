import xml.etree.ElementTree as ET
from enum import Enum

from urh.simulator.SimulatorItem import SimulatorItem


class SimulatorRule(SimulatorItem):
    def __init__(self):
        super().__init__()

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None

        super().set_parent(value)

    @property
    def has_else_condition(self) -> bool:
        return any(child.type is ConditionType.ELSE for child in self.children)

    def get_first_applying_condition(self):
        return next((child for child in self.children if child.condition_applies), None)

    def next_item(self):
        return next((c.children[0] for c in self.children if c.condition_applies and c.child_count()), self.next_sibling())

    def to_xml(self) -> ET.Element:
        return ET.Element("simulator_rule")

    @classmethod
    def from_xml(cls, tag: ET.Element):
        return SimulatorRule()


class ConditionType(Enum):
    IF = "IF"
    ELSE_IF = "ELSE IF"
    ELSE = "ELSE"


class SimulatorRuleCondition(SimulatorItem):
    def __init__(self, type: ConditionType):
        super().__init__()
        self.type = type
        self.condition = ""

    @property
    def condition_applies(self) -> bool:
        if self.type is ConditionType.ELSE:
            return True

        valid, _, node = self.expression_parser.validate_expression(self.condition, is_formula=False)
        assert valid == True and node is not None
        return self.expression_parser.evaluate_node(node)

    def set_parent(self, value):
        if value is not None:
            assert isinstance(value, SimulatorRule)

        super().set_parent(value)

    def validate(self):
        if self.type is ConditionType.ELSE:
            return True

        result, _, _ = self.expression_parser.validate_expression(self.condition, is_formula=False)
        return result

    def to_xml(self):
        return ET.Element("simulator_rule_condition", attrib={"type": self.type.value,
                                                              "condition": self.condition})

    @classmethod
    def from_xml(cls, tag: ET.Element):
        cond_type = tag.get("type", ConditionType.IF.value)
        condition = tag.get("condition", "")

        result = SimulatorRuleCondition(type=ConditionType(cond_type))
        result.condition = condition

        return result
