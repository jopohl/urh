import xml.etree.ElementTree as ET

from urh.simulator.SimulatorItem import SimulatorItem
from urh.simulator.SimulatorRule import SimulatorRuleCondition
from urh.util.Formatter import Formatter


class SimulatorSleepAction(SimulatorItem):
    def __init__(self):
        super().__init__()
        self.sleep_time = 1.0

    @property
    def caption(self):
        return "Sleep for " + Formatter.science_time(self.sleep_time)

    def validate(self):
        return True

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None or isinstance(value, SimulatorRuleCondition)

        super().set_parent(value)

    def to_xml(self):
        attrib = {"sleep_time": str(self.sleep_time)}
        return ET.Element("simulator_sleep_action", attrib=attrib)

    @classmethod
    def from_xml(cls, tag):
        result = SimulatorSleepAction()
        result.sleep_time = Formatter.str2val(tag.get("sleep_time", "1.0"), float, 1.0)
        return result
