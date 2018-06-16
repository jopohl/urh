from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class MessageTypeBuilder(object):
    def __init__(self, name: str):
        self.message_type = MessageType(name)

    def add_label(self, label_type: FieldType.Function, length: int, name: str=None):
        try:
            start = self.message_type[-1].end
            color_index = self.message_type[-1].color_index + 1
        except IndexError:
            start, color_index = 0, 0

        if name is None:
            name = label_type.value

        lbl = ProtocolLabel(name, start, start+length-1, color_index, field_type=FieldType(label_type.name, label_type))
        self.message_type.append(lbl)
