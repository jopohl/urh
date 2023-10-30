import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message


class MessageBreakAction(QUndoCommand):
    def __init__(self, proto_analyzer: ProtocolAnalyzer, msg_nr: int, pos: int):
        super().__init__()
        self.proto_analyzer = proto_analyzer
        self.msg_nr = msg_nr
        self.pos = pos
        self.orig_messages = copy.deepcopy(proto_analyzer.messages)

        self.setText("Break message behind selection")

    def redo(self):
        message = self.proto_analyzer.messages[self.msg_nr]
        message1 = Message(
            plain_bits=message.plain_bits[: self.pos],
            pause=0,
            rssi=message.rssi,
            decoder=message.decoder,
            message_type=message.message_type,
            samples_per_symbol=message.samples_per_symbol,
        )
        message2 = Message(
            plain_bits=message.plain_bits[self.pos :],
            pause=message.pause,
            rssi=message.rssi,
            decoder=message.decoder,
            message_type=message.message_type,
            samples_per_symbol=message.samples_per_symbol,
        )
        self.proto_analyzer.messages[self.msg_nr] = message1
        self.proto_analyzer.messages.insert(self.msg_nr + 1, message2)

    def undo(self):
        self.proto_analyzer.messages = self.orig_messages

    def __get_zero_seq_indexes(self, message: str, following_zeros: int):
        """
        :rtype: list[tuple of int]
        """

        result = []
        if following_zeros > len(message):
            return result

        zero_counter = 0
        for i in range(0, len(message)):
            if message[i] == "0":
                zero_counter += 1
            else:
                if zero_counter >= following_zeros:
                    result.append((i - zero_counter, i))
                zero_counter = 0

        if zero_counter >= following_zeros:
            result.append((len(message) - 1 - following_zeros, len(message) - 1))

        return result
