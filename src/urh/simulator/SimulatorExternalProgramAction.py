import xml.etree.ElementTree as ET

from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorRule import SimulatorRuleCondition
from urh.util import util


class SimulatorExternalProgramAction(SimulatorItem):
    def __init__(self):
        super().__init__()
        self.ext_prog = None
        self.args = None

    def validate(self):
        return util.validate_command(self.ext_prog)

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None or isinstance(value, SimulatorRuleCondition)

        super().set_parent(value)

    def to_xml(self):
        attrib = dict()
        if self.ext_prog:
            attrib["ext_prog"] = self.ext_prog
        if self.args:
            attrib["args"] = self.args
        return ET.Element("simulator_program_action", attrib=attrib)

    @classmethod
    def from_xml(cls, tag):
        result = SimulatorExternalProgramAction()
        result.ext_prog = tag.get("ext_prog", None)
        result.args = tag.get("args", None)
        return result
