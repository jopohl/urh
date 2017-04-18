from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType

class SimulatorMessage(Message, SimulatorItem):
    def __init__(self, destination, plain_bits, pause: int, message_type: MessageType, decoder=None, source=None):
        Message.__init__(self, plain_bits, pause, message_type, decoder=decoder, participant=source)
        SimulatorItem.__init__(self)
        self.destination = destination

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None or isinstance(value, SimulatorRuleCondition)

        super().set_parent(value)