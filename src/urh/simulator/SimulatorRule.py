from enum import Enum
import xml.etree.ElementTree as ET

from urh.simulator.SimulatorItem import SimulatorItem


class SimulatorRule(SimulatorItem):
    def __init__(self):
        super().__init__()

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None

        super().set_parent(value)

    def has_else_condition(self):
        return any(child.type is ConditionType.ELSE for child in self.children)

    def true_condition(self):
        for child in self.children:
            if child.applies():
                return child

        return None

    def next_item(self):
        result = self.next_sibling()

        for child in self.children:
            if child.applies() and child.child_count():
                result = child.children[0]
                break

        return result

    def to_xml(self) -> ET.Element:
        result = ET.Element("simulator_rule")
        for condition in self.children:
            assert isinstance(condition, SimulatorRuleCondition)
            result.append(condition.to_xml())
        return result

    @classmethod
    def from_xml(cls, tag: ET.Element):
        result = SimulatorRule()
        for i, child in enumerate(tag):
            result.insert_child(i, SimulatorRuleCondition.from_xml(child))
        return result

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

    def applies(self):
        if self.type is ConditionType.ELSE:
            return True

        valid, _, node = self.expression_parser.validate_expression(self.condition, is_formula=False)
        assert valid == True and node is not None
        return self.expression_parser.evaluate_node(node)

    def check(self):
        if self.type is ConditionType.ELSE:
            return True

        result, _, _ = self.expression_parser.validate_expression(self.condition, is_formula=False)
        return result

    def to_xml(self):
        return ET.Element("rule_condition", attrib={"type": self.type.value,
                                                    "condition": self.condition})

    @classmethod
    def from_xml(cls, tag: ET.Element):
        cond_type = tag.get("type", ConditionType.IF.value)
        condition = tag.get("condition", "")

        result = SimulatorRuleCondition(type=ConditionType(cond_type))
        result.condition = condition

        return result