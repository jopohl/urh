import xml.etree.ElementTree as ET

from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorRule import SimulatorRuleCondition
from urh.util import util


class SimulatorTriggerCommandAction(SimulatorItem):
    def __init__(self):
        super().__init__()
        self.command = None

    def validate(self):
        return util.validate_command(self.command)

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None or isinstance(value, SimulatorRuleCondition)

        super().set_parent(value)

    def to_xml(self):
        attrib = dict()
        if self.command:
            attrib["command"] = self.command
        return ET.Element("simulator_trigger_command_action", attrib=attrib)

    @classmethod
    def from_xml(cls, tag):
        result = SimulatorTriggerCommandAction()
        result.command = tag.get("command", None)
        return result
