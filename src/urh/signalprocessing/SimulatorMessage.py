import copy

from urh.signalprocessing.SimulatorItem import SimulatorItem
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType

class SimulatorMessage(Message, SimulatorItem):
    def __init__(self, destination, plain_bits, pause: int, message_type: MessageType, decoder=None, source=None):
        Message.__init__(self, plain_bits, pause, message_type, decoder=decoder, participant=source)
        SimulatorItem.__init__(self)
        self.destination = destination
        self.send_recv_messages = []
        self.repeat = 1

    def set_parent(self, value):
        if value is not None:
            assert value.parent() is None or isinstance(value, SimulatorRuleCondition)

        super().set_parent(value)

    @property
    def children(self):
        return self.message_type

    def insert_child(self, pos, child):
        self.children.append(child)
        child.set_parent(self)

    def check(self):
        return all(child.is_valid for child in self.children)

    @property
    def plain_ascii_str(self) -> str:
        plain_ascii_array = self.send_recv_messages[-1].plain_ascii_array if len(self.send_recv_messages) else self.plain_ascii_array
        return "".join(map(chr, plain_ascii_array))

    @property
    def plain_bits_str(self) -> str:
        return str(self.send_recv_messages[-1]) if len(self.send_recv_messages) else str(self)

    def __delitem__(self, index):
        labels_add = []
        labels_remove = []

        if isinstance(index, slice):
            step = index.step
            if step is None:
                step = 1
            number_elements = len(range(index.start, index.stop, step))

            for l in self.message_type:
                if index.start <= l.start and index.stop >= l.end:
                    labels_remove.append(l)

                elif index.stop - 1 < l.start:
                    l.start -= number_elements
                    l.end -= number_elements

                elif index.start <= l.start <= index.stop:
                    labels_remove.append(l)

                elif index.start >= l.start and index.stop <= l.end:
                    labels_remove.append(l)

                elif l.start <= index.start < l.end:
                    labels_remove.append(l)
        else:
            for l in self.message_type:
                if index < l.start:
                    l.start -= 1
                    l.end -= 1
                elif l.start < index < l.end:
                    labels_remove.append(l)
                    if l.end - l.start > 1:
                        l.start = index - 1
                    else:
                        labels_remove.append(l)

        self.protocol_manager.delete_items(labels_remove)
        self.protocol_manager.add_items(labels_add, -1, self)
        del self.plain_bits[index]