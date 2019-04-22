from urh.signalprocessing.ChecksumLabel import ChecksumLabel

from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class MessageTypeBuilder(object):
    def __init__(self, name: str):
        self.name = name
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

    def add_checksum_label(self, length, checksum, data_start=None, data_end=None, name: str=None):
        label_type = FieldType.Function.CHECKSUM
        try:
            start = self.message_type[-1].end
            color_index = self.message_type[-1].color_index + 1
        except IndexError:
            start, color_index = 0, 0

        if name is None:
            name = label_type.value

        if data_start is None:
            # End of sync or preamble
            sync_label = self.message_type.get_first_label_with_type(FieldType.Function.SYNC)
            if sync_label:
                data_start = sync_label.end
            else:
                preamble_label = self.message_type.get_first_label_with_type(FieldType.Function.PREAMBLE)
                if preamble_label:
                    data_start = preamble_label.end
                else:
                    data_start = 0

        if data_end is None:
            data_end = start

        lbl = ChecksumLabel(name, start, start+length-1, color_index, field_type=FieldType(label_type.name, label_type))
        lbl.data_ranges = [(data_start, data_end)]
        lbl.checksum = checksum
        self.message_type.append(lbl)
