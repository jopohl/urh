from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class ZeroHideAction(QUndoCommand):
    def __init__(self, protocol: ProtocolAnalyzer, following_zeros: int, view: int):
        super().__init__()
        self.protocol = protocol
        self.following_zeros = following_zeros
        self.viewtype = view

        self.setText("Hide zero sequences >= " + str(self.following_zeros))

    def redo(self):
        factor = 1
        if self.viewtype == 1:
            factor = 4
        elif self.viewtype == 2:
            factor = 8

        pa = self.protocol
        for i in range(pa.num_messages):
            message = pa.messages[i]
            if self.viewtype == 0:
                data = message.decoded_bits_str
            elif self.viewtype == 1:
                data = message.decoded_hex_str
            else:
                data = message.decoded_ascii_str

            zero_sequences = self.__get_zero_seq_indexes(data, self.following_zeros)

            for seq in reversed(zero_sequences):
                full_bits = pa.messages[i].decoded_bits
                start = seq[0] * factor
                end = seq[1] * factor
                pa.messages[i].decoded_bits = full_bits[:start] + full_bits[end:]

    def undo(self):
        self.protocol.clear_decoded_bits()

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
                    result.append((i-zero_counter, i))
                zero_counter = 0

        if zero_counter >= following_zeros:
            result.append((len(message) - zero_counter, len(message)))

        return result